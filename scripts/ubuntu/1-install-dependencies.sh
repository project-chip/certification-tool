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

print_instalation_step "Set up Docker's apt repository"
$UBUNTU_SCRIPT_DIR/1.1-install-docker-repository.sh

print_instalation_step "Silence user prompts about reboot and service restart required (script will prompt user to reboot in the end)"
sudo sed -i "s/#\$nrconf{kernelhints} = -1;/\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
sudo sed -i "s/#\$nrconf{restart} = 'i';/\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf

sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# TODO Comment on what dependency is required for:
packagelist=(
    "python3-pip (>=22.0.2+dfsg-1ubuntu0.4)"          # Test Harness CLI uses Python              
    "python3-venv (>=3.10.6-1~22.04)"                 # Test Harness CLI uses Python
    "docker-ce (>=5:24.0.7-1~ubuntu.22.04~jammy)"
)

UBUNTU_VERSION_NUMBER=$(lsb_release -sr)
if [UBUNTU_VERSION_NUMBER -eq "22.04"]; then
  packagelist+="linux-modules-extra-raspi (>=5.15.0.1046.44)"
fi

SAVEIFS=$IFS
IFS=$(echo -en "\r")
for package in ${packagelist[@]}; do
  print_instalation_step "Instaling package: ${package[@]}"
  sudo DEBIAN_FRONTEND=noninteractive apt satisfy ${package[@]} -y --allow-downgrades
done
IFS=$SAVEIFS 

print_instalation_step "Install Poetry, needed for Test Harness CLI"
curl -sSL https://install.python-poetry.org | python3 -

print_end_of_script
