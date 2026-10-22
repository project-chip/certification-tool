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
WPA_SUPPLICANT_FILE=/etc/wpa_supplicant/wpa_supplicant.conf
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
ExecStart=/usr/sbin/wpa_supplicant -u -s -i $WLAN_INTERFACE -c $WPA_SUPPLICANT_FILE
EOF
sudo systemctl daemon-reload

# Only one wpa_supplicant may manage $WLAN_INTERFACE. When netplan already configures Wi-Fi
# on it (e.g. Wi-Fi set in Raspberry Pi Imager, or the netplan step of
# docs/enable_wifi_and_ssh_raspi_ubuntu_server.md), netplan runs its own wpa_supplicant there
# with the same control socket (/run/wpa_supplicant/$WLAN_INTERFACE). Running ours as well makes
# the two fight over the interface and the socket, which then disappears intermittently
# depending on start order, so CNET Wi-Fi tests fail with "No WiFi interface found".
# In that case keep netplan's (it holds the Wi-Fi connection and provides the control socket)
# and mask ours, which also stops D-Bus from activating it.
if [ -n "$(sudo netplan get "wifis.$WLAN_INTERFACE" 2>/dev/null | grep -vx 'null')" ]; then
    printf "\n netplan already manages Wi-Fi on $WLAN_INTERFACE: keeping its wpa_supplicant,"
    printf "\n masking wpa_supplicant.service so only one wpa_supplicant runs on $WLAN_INTERFACE\n"
    sudo systemctl disable --now wpa_supplicant.service || true
    sudo systemctl mask wpa_supplicant.service
    # Stopping ours may have removed the shared control socket; restart netplan's to recreate it.
    # This briefly drops Wi-Fi, and the install pulls code from GitHub right after this script,
    # so wait until the network (and DNS) is back before going on.
    sudo systemctl try-restart "netplan-wpa-$WLAN_INTERFACE.service" || true
    printf "\n Waiting for the network to come back on $WLAN_INTERFACE"
    for _ in $(seq 1 60); do
        getent hosts github.com > /dev/null && break
        printf "."
        sleep 1
    done
    printf "\n"
else
    sudo systemctl unmask wpa_supplicant.service
    sudo systemctl enable wpa_supplicant.service
fi

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

# Set "key=value" in the [server] section of $AVAHI_CONF: replace an existing or commented-out
# line, otherwise add it right after [server].
set_avahi_option() {
    local key=$1 value=$2
    echo "  setting: $key=$value"
    if grep -q "^$key=" "$AVAHI_CONF"; then
        sudo sed -i "s|^$key=.*|$key=$value|" "$AVAHI_CONF"
    elif grep -q "^#$key=" "$AVAHI_CONF"; then
        sudo sed -i "s|^#$key=.*|$key=$value|" "$AVAHI_CONF"
    else
        sudo sed -i "/^\[server\]/a $key=$value" "$AVAHI_CONF"
    fi
}

# On a Docker host Avahi also joins the docker0/br-*/veth* interfaces, so it sees its own
# mDNS records come back through them (host name conflicts, stale records). Keep it on the
# physical and Thread (wpan0) interfaces only.
print_script_step "Restrict host Avahi to physical network interfaces"
AVAHI_CONF=/etc/avahi/avahi-daemon.conf
AVAHI_ALLOW_INTERFACES="${AVAHI_ALLOW_INTERFACES:-eth0,$WLAN_INTERFACE,wpan0}"
if [ -f "$AVAHI_CONF" ]; then
    printf "\n Updating: $AVAHI_CONF\n"
    sudo cp -n "$AVAHI_CONF" "$AVAHI_CONF.orig"
    set_avahi_option allow-interfaces "$AVAHI_ALLOW_INTERFACES"
    # wpan0 is a point-to-point interface, which Avahi ignores unless this is enabled.
    set_avahi_option allow-point-to-point yes
    sudo systemctl restart avahi-daemon || printf "\n Could not restart avahi-daemon; restart it manually.\n"
else
    printf "\n $AVAHI_CONF not found (avahi-daemon is not installed); skipping.\n"
fi

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
