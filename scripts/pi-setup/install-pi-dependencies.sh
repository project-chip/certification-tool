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

# Silence user prompts about reboot and service restart required (script will prompt user to reboot in the end)
sudo sed -i "s/#\$nrconf{kernelhints} = -1;/\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
sudo sed -i "s/#\$nrconf{restart} = 'i';/\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf

# Upgrade OS
sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# TODO Comment on what dependency is required for:
packagelist=(
    "pi-bluetooth (>=0.1.18ubuntu4)",
    "bluetooth (>=5.64-0ubuntu1.1)",
    "linux-rasp (>=5.15.0.1055.53)"
)

# UBUNTU_VERSION_NUMBER=$(lsb_release -sr)
# if [UBUNTU_VERSION_NUMBER -eq "22.04"]; then
#   packagelist+="linux-modules-extra-raspi (>=5.15.0.1046.44)"
# fi

SAVEIFS=$IFS
IFS=$(echo -en "\r")
for package in ${packagelist[@]}; do
  echo "# Instaling package: ${package[@]}"
  sudo DEBIAN_FRONTEND=noninteractive sudo apt satisfy ${package[@]} -y --allow-downgrades
done
IFS=$SAVEIFS 
