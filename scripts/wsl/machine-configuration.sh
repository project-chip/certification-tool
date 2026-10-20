#! /usr/bin/env bash

 #
 # Copyright (c) 2026 Project CHIP Authors
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

# WSL variant of scripts/ubuntu/2-machine-configuration.sh (sync tracked in
# wsl-utils.sh). Identical except the Wi-Fi parts are removed, since WSL has no
# wlan interface: the wpa_supplicant service setup, the wlan sysctl entries
# and the Wi-Fi device configuration (2.1-configure-wifi-devices.sh).
set -e

ROOT_DIR=$(realpath $(dirname "$0")/../..)
SCRIPT_DIR="$ROOT_DIR/scripts"

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

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

# Setup Network
print_script_step "Accept Router Advertisements on network interfaces"
SYSCTL_FILE=/etc/sysctl.conf
SYSCTL_SETTINGS=(
    "net.ipv6.conf.eth0.accept_ra=2"
    "net.ipv6.conf.eth0.accept_ra_rt_info_max_plen=64"
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
