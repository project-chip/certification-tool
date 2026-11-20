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

# Removes the host Avahi interface restriction written by the machine configuration of some
# earlier installs (allow-interfaces=eth0,<wlan interface>,wpan0 on Ubuntu or eth0,wpan0 on WSL,
# and allow-point-to-point=yes), restoring the stock commented-out lines. An allow-interfaces list
# with any other value is left as it is. Safe to re-run.
AVAHI_CONF=/etc/avahi/avahi-daemon.conf
TH_ALLOW_INTERFACES="^allow-interfaces=eth0(,[^,]+)?,wpan0$"

print_script_step "Removing the host Avahi interface restriction"
if [ ! -f "$AVAHI_CONF" ]; then
    printf "\n $AVAHI_CONF not found (avahi-daemon is not installed); skipping.\n"
elif grep -qE "$TH_ALLOW_INTERFACES" "$AVAHI_CONF"; then
    printf "\n Updating: $AVAHI_CONF\n"
    sudo sed -i -E \
        -e "s|$TH_ALLOW_INTERFACES|#allow-interfaces=eth0|" \
        -e "s|^allow-point-to-point=yes$|#allow-point-to-point=no|" \
        "$AVAHI_CONF"
    sudo systemctl restart avahi-daemon || printf "\n Could not restart avahi-daemon; restart it manually.\n"
else
    printf "\n No restriction set by the Test Harness installation in $AVAHI_CONF; nothing to do.\n"
fi

print_end_of_script
