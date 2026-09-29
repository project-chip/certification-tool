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
set -e

ROOT_DIR=$(realpath $(dirname "$0")/../..)
SCRIPT_DIR="$ROOT_DIR/scripts"

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

# Writes udev rules governing the Wi-Fi devices the Test Harness uses. Kept separate from the rest
# of the machine configuration because it is safe to re-run, and so runs on updates as well as on a
# fresh install.
UDEV_RULES_FILE=/etc/udev/rules.d/70-matter-th-wifi.rules

print_script_step "Configuring udev rules for Wi-Fi devices"
printf "\n Writing: $UDEV_RULES_FILE\n"
cat << 'EOF' | sudo tee "$UDEV_RULES_FILE"
# USB Wi-Fi adapters belong to the Test Harness by default, rather than the
# host's network management. NetworkManager (if installed) would claim every
# Wi-Fi device it finds, and interfere with the operation of the Wi-Fi
# Fixture container. (The most noticeable symptom of this is the failure to
# assign a link-local IPv6 address to the interface during fixture operation.)
# Note that systemd-networkd is conservative by default and only configures
# links matching a .network file.
#
# If NetworkManager is required to drive a particular USB adapter, it has to be
# configured to do so explicitly via managed=1 in a [device] section, which will
# override this rule.
SUBSYSTEM=="net", ACTION=="add|change", SUBSYSTEMS=="usb", ENV{DEVTYPE}=="wlan", ENV{NM_UNMANAGED}="1"

# Prevent renaming of VIFs created by hostapd or wpa_supplicant by matching MAC
# addresses that have the Local bit set, indicating a locally assigned address,
# such as the one the kernel generates based on the universal MAC of the real
# device. The Local bit is B1 of the top octet; B0 (LSB) is 0 for unicast
# addresses, i.e. we're looking for addresses where the first octet ends in one
# of the hex digits 2, 6, A, or E. Setting NAME to the kernel-assigned name
# stops later rules from modifying it.
SUBSYSTEM=="net", ACTION=="add", ATTR{address}=="?[26ae]:*", NAME="$kernel"
EOF

# Reload so that the rules apply to devices appearing from here on. There is deliberately no
# udevadm trigger: rules of this kind take effect as a device appears, and NetworkManager decides
# whether a device is its to manage when it first sees it rather than revisiting that on a change
# event, so triggering one leaves an adapter it has already claimed exactly as it was.
print_script_step "Reloading udev rules"
sudo udevadm control --reload-rules

printf "\n Note: a USB Wi-Fi adapter that is already connected keeps whatever the host has\n"
printf " already done with it. Re-plug it, or reboot, for these rules to apply to it.\n"

print_end_of_script
