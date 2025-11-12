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

print_script_step "Set up Docker's apt repository"
$UBUNTU_SCRIPT_DIR/1.1-install-docker-repository.sh

print_script_step "Silence user prompts about reboot and service restart required (script will prompt user to reboot in the end)"
sudo sed -i "s/#\$nrconf{kernelhints} = -1;/\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
sudo sed -i "s/#\$nrconf{restart} = 'i';/\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf

sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

readarray packagelist < "$UBUNTU_SCRIPT_DIR/package-dependency-list.txt"

SAVEIFS=$IFS
IFS=$(echo -en "\r")
for package in ${packagelist[@]}; do
  print_script_step "Installing package: ${package[@]}"

  # Special handling for docker-ce to avoid version 29.x
  if [[ "${package%%[[:space:]]}" == docker-ce* ]]; then
    # Get the latest version that is not 29.x
    DOCKER_VERSION=$(apt-cache madison docker-ce | awk '$3 !~ /^5:29\./ {print $3; exit}')
    if [ -n "$DOCKER_VERSION" ]; then
      print_script_step "Installing docker-ce version $DOCKER_VERSION (excluding 29.x)"
      sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-downgrades docker-ce=$DOCKER_VERSION docker-ce-cli=$DOCKER_VERSION containerd.io
      sudo apt-mark hold docker-ce docker-ce-cli
    else
      echo "ERROR: No suitable docker-ce version found (excluding 29.x)"
      exit 1
    fi
  else
    sudo DEBIAN_FRONTEND=noninteractive apt-get satisfy "${package%%[[:space:]]}" -y --allow-downgrades
  fi
done
IFS=$SAVEIFS 

print_script_step "Install Poetry, needed for Test Harness CLI"
curl -sSL https://install.python-poetry.org | python3 -

print_end_of_script
