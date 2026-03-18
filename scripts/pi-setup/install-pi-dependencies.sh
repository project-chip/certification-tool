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

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

print_script_step "Silence user prompts about reboot and service restart required (script will prompt user to reboot in the end)"
sudo sed -i "s/#\$nrconf{kernelhints} = -1;/\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
sudo sed -i "s/#\$nrconf{restart} = 'i';/\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf

print_script_step "Ensure package manager is ready"
# Wait up to 5 minutes for automatic updates to complete
WAIT_COUNT=0
while sudo fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 || \
      sudo fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
    [ $WAIT_COUNT -ge 30 ] && { echo "ERROR: Timeout waiting for package manager"; exit 1; }
    echo "Waiting for package manager... ($((WAIT_COUNT * 10))s)"
    sleep 10
    WAIT_COUNT=$((WAIT_COUNT + 1))
done
sudo dpkg --configure -a || { echo "ERROR: Failed to repair dpkg. Run 'sudo dpkg --configure -a' manually"; exit 1; }

print_script_step "Upgrade OS"
sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# TODO Comment on what dependency is required for:
packagelist=(
    "pi-bluetooth (>=0.1.18ubuntu4)"
    "bluetooth (>=5.64-0ubuntu1.1)"
    "linux-raspi (>=5.15.0.1055.53)"
)

SAVEIFS=$IFS
IFS=$(echo -en "\r")
for package in ${packagelist[@]}; do
  print_script_step "Instaling package: ${package[@]}"
  sudo DEBIAN_FRONTEND=noninteractive sudo apt-get satisfy ${package[@]} -y --allow-downgrades
done
IFS=$SAVEIFS 

print_end_of_script
