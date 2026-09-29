#! /usr/bin/env bash

 #
 # Copyright (c) 2023 Project CHIP Authors
 #
 # Licensed under the Apache License, Version 2.0 (the "License");
 # you may not use this file except in compliance with the License.
 # You may obtain a copy of the License at
 #
 # http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.
set -e

ROOT_DIR=$(realpath $(dirname "$0")/../..)
SCRIPT_DIR="$ROOT_DIR/scripts"
UBUNTU_SCRIPT_DIR="$SCRIPT_DIR/ubuntu"

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

WLAN_INTERFACE="${WLAN_INTERFACE:-wlan0}"

# Configure docker access from user
print_script_step "Configuring Docker access for user"
# docker-ce's own postinst already creates this group, so it normally exists by the
# time this runs; tolerate that instead of letting it fail the whole script.
sudo groupadd docker || true
sudo usermod -a -G docker $USER
sudo service docker restart

# Grant access to serial devices (e.g. the nRF52840/SiLabs Thread RCP dongle at
# /dev/ttyACM0) without needing sudo for every nrfutil/otbr invocation.
print_script_step "Configuring serial device access for user"
sudo usermod -a -G dialout $USER

# Setup Wifi
print_script_step "Configure wpa_supplicant service"
# The packaged wpa_supplicant.service provides the dbus-fi.w1.wpa_supplicant1.service
# alias, and on stock images /etc/systemd/system/dbus-fi.w1.wpa_supplicant1.service is
# already a symlink to it. So instead of writing a unit at that path (which would write
# through the symlink into the packaged unit), override ExecStart with a drop-in.
WPA_ALIAS_UNIT_FILE=/etc/systemd/system/dbus-fi.w1.wpa_supplicant1.service
WPA_DROPIN_DIR=/etc/systemd/system/wpa_supplicant.service.d
# Older installs wrote a standalone unit at the alias path, which would conflict with the alias.
if [ -f "$WPA_ALIAS_UNIT_FILE" ] && [ ! -L "$WPA_ALIAS_UNIT_FILE" ]; then
    printf "\n Removing standalone unit from a previous install: $WPA_ALIAS_UNIT_FILE\n"
    sudo rm "$WPA_ALIAS_UNIT_FILE"
fi
printf "\n Writing: $WPA_DROPIN_DIR/matter-th.conf\n"
sudo mkdir -p "$WPA_DROPIN_DIR"
cat << EOF | sudo tee "$WPA_DROPIN_DIR/matter-th.conf"
[Service]
ExecStart=
ExecStart=/usr/sbin/wpa_supplicant -u -s -i $WLAN_INTERFACE -c /etc/wpa_supplicant/wpa_supplicant.conf
EOF
sudo systemctl daemon-reload
sudo systemctl enable wpa_supplicant.service

WPA_SUPPLICANT_FILE=/etc/wpa_supplicant/wpa_supplicant.conf
WPA_SUPPLICANT_SETTINGS=(
    "ctrl_interface=DIR=/run/wpa_supplicant"
    "update_config=1"
)
printf "\n Updating: $WPA_SUPPLICANT_FILE\n"
# The directory only exists once wpasupplicant is installed, which not every image has.
sudo mkdir -p "$(dirname "$WPA_SUPPLICANT_FILE")"
sudo touch "$WPA_SUPPLICANT_FILE"
for setting in ${WPA_SUPPLICANT_SETTINGS[@]}; do
    echo "  setting: $setting"
    grep -qxF "$setting" "$WPA_SUPPLICANT_FILE" || echo "$setting" | sudo tee -a "$WPA_SUPPLICANT_FILE"
done

# Setup Network
print_script_step "Accept Router Advertisements on network interfaces"
SYSCTL_FILE=/etc/sysctl.conf
SYSCTL_SETTINGS=(
    "net.ipv6.conf.eth0.accept_ra=2"
    "net.ipv6.conf.eth0.accept_ra_rt_info_max_plen=64"
    "net.ipv6.conf.$WLAN_INTERFACE.accept_ra=2"
    "net.ipv6.conf.$WLAN_INTERFACE.accept_ra_rt_info_max_plen=64"
)
printf "\n Updating: $SYSCTL_FILE\n"
sudo touch "$SYSCTL_FILE"
for setting in ${SYSCTL_SETTINGS[@]}; do
    echo "  setting: $setting"
    grep -qxF "$setting" "$SYSCTL_FILE" || echo "$setting" | sudo tee -a "$SYSCTL_FILE"
done

print_script_step "Enable ip6table_filter in kernel modules"
printf "\n Updating: /etc/modules\n"
grep -qxF "ip6table_filter" /etc/modules || echo "ip6table_filter" | sudo tee -a /etc/modules

print_script_step "Configuring Wi-Fi devices"
$UBUNTU_SCRIPT_DIR/2.1-configure-wifi-devices.sh
verify_return_code

print_script_step "Create System Service for Matter Test Harness"
printf "\n Writing: /etc/systemd/system/matter-th.service"
cat << EOF | sudo tee /etc/systemd/system/matter-th.service
[Unit]
Description=Matter Test Harness
After=network.target
[Service]
Type=oneshot
User=$USER
Group=$(id -gn)
ExecStart=$ROOT_DIR/scripts/start.sh
[Install]
WantedBy=default.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable matter-th

print_script_step "Enable systemd-timesyncd"
# Some images (e.g. ones using chrony) don't ship timesyncd; they already sync time.
if systemctl list-unit-files systemd-timesyncd.service --no-legend | grep -q .; then
    sudo systemctl enable systemd-timesyncd
    sudo systemctl start systemd-timesyncd
else
    printf "\n systemd-timesyncd is not installed; skipping.\n"
fi

print_end_of_script
