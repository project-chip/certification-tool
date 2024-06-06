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
UBUNTU_SCRIPT_DIR="$SCRIPT_DIR/ubuntu"

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

print_instalation_step "Installing Test Harness Dependencies"
$UBUNTU_SCRIPT_DIR/1-install-dependencies.sh
verify_return_code

print_instalation_step "Configure Machine"
$UBUNTU_SCRIPT_DIR/2-machine-cofiguration.sh
verify_return_code

print_instalation_step "Update Test Harness code"
Store the current branch for the update
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
$UBUNTU_SCRIPT_DIR/auto-update.sh "$CURRENT_BRANCH"
verify_return_code

print_instalation_step "Revert needrestart config to default"
sudo sed -i "s/\$nrconf{kernelhints} = -1;/#\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
sudo sed -i "s/\$nrconf{restart} = 'a';/#\$nrconf{restart} = 'i';/" /etc/needrestart/needrestart.conf

print_end_of_script

print_installation_success

print_instalation_step "You need to reboot to finish setup"
printf "Do you want to reboot now? (Press 1 to reboot now)\n"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) sudo reboot; break;;
        No ) exit;;
    esac
done
