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
ROOT_DIR=$(realpath $(dirname "$0")/../..)
SCRIPT_DIR="$ROOT_DIR/scripts"

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

WLAN_INTERFACE="${WLAN_INTERFACE:-wlan0}"

# Trust github
print_instalation_step "Apply github.com fingerprint"
ssh-keygen -F github.com || ssh-keyscan github.com >>~/.ssh/known_hosts

# Configure docker access from user
print_instalation_step "Configuring Docker access for user"
sudo groupadd docker
sudo usermod -a -G docker $USER
sudo service docker restart

# Setup Wifi
print_instalation_step "Create System Service for wpa_suppliant"
printf "\n Writing: /etc/systemd/system/dbus-fi.w1.wpa_supplicant1.service"
cat << EOF | sudo tee /etc/systemd/system/dbus-fi.w1.wpa_supplicant1.service
[Unit]
Description=WPA supplicant
Before=network.target
After=dbus.service
Wants=network.target
IgnoreOnIsolate=true

[Service]
Type=dbus
BusName=fi.w1.wpa_supplicant1
ExecStart=/sbin/wpa_supplicant -u -s -i $WLAN_INTERFACE -c /etc/wpa_supplicant/wpa_supplicant.conf

[Install]
WantedBy=multi-user.target
Alias=dbus-fi.w1.wpa_supplicant1.service
EOF
sudo systemctl daemon-reload
sudo systemctl enable dbus-fi.w1.wpa_supplicant1

WPA_SUPPLICANT_FILE=/etc/wpa_supplicant/wpa_supplicant.conf
WPA_SUPPLICANT_SETTINGS=(
    "ctrl_interface=DIR=/run/wpa_supplicant"
    "update_config=1"
)
printf "\n Updating: $WPA_SUPPLICANT_FILE\n"
sudo touch "$WPA_SUPPLICANT_FILE"
for setting in ${WPA_SUPPLICANT_SETTINGS[@]}; do
    echo "  setting: $setting"
    grep -qxF "$setting" "$WPA_SUPPLICANT_FILE" || echo "$setting" | sudo tee -a "$WPA_SUPPLICANT_FILE"
done

# Setup Network
print_instalation_step "Accept Router Advertisements on network interfaces"
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

print_instalation_step "Enable ip6table_filter in kernel modules"
printf "\n Updating: /etc/modules\n"
grep -qxF "ip6table_filter" /etc/modules || echo "ip6table_filter" | sudo tee -a /etc/modules

print_instalation_step "Create System Service for Matter Test Harness"
printf "\n Writing: /etc/systemd/system/matter-th.service"
cat << EOF | sudo tee /etc/systemd/system/matter-th.service
[Unit]
Description=Matter Test Harness
After=network.target
[Service]
Type=oneshot
User=$USER
Group=ubuntu
ExecStart=$ROOT_DIR/scripts/start.sh
[Install]
WantedBy=default.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable matter-th

print_instalation_step "Enable systemd-timesyncd"
sudo systemctl enable systemd-timesyncd
sudo systemctl start systemd-timesyncd

print_end_of_script
