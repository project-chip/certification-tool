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

WLAN_INTERFACE="${WLAN_INTERFACE:-wlan0}"

# Trust github
printf "\n\n************************************************************"
printf "\n*** Apply github.com fingerprint ***\n"
ssh-keygen -F github.com || ssh-keyscan github.com >>~/.ssh/known_hosts

# Configure docker access from user
printf "\n\n************************************************************"
printf "\n*** Configuring Docker access for user ***\n"

sudo groupadd docker
sudo usermod -a -G docker $USER
sudo service docker restart

# Setup Wifi
printf "\n\n************************************************************"
printf "\n*** Create System Service for wpa_suppliant ***\n"
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
printf "\n\n************************************************************"
printf "\n*** Accept Router Advertisements on network interfaces ***\n"
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

printf "\n\n************************************************************"
printf "\n*** Enable ip6table_filter in kernel modules ***\n"
printf "\n Updating: /etc/modules\n"
grep -qxF "ip6table_filter" /etc/modules || echo "ip6table_filter" | sudo tee -a /etc/modules

printf "\n\n************************************************************"
printf "\n*** Create System Service for Matter Test Harness ***\n"
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

printf "\n\n************************************************************"
printf "\n*** Enable systemd-timesyncd ***\n"
sudo systemctl enable systemd-timesyncd
sudo systemctl start systemd-timesyncd
