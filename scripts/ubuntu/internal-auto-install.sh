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

check_installation_prerequisites
verify_return_code

print_script_step "Installing Test Harness Dependencies"
$UBUNTU_SCRIPT_DIR/1-install-dependencies.sh
verify_return_code

print_script_step "Installing Additional Dependencies"
$UBUNTU_SCRIPT_DIR/1.2-install-additional-dependencies.sh
verify_return_code

print_script_step "Configure Machine"
$UBUNTU_SCRIPT_DIR/2-machine-cofiguration.sh
verify_return_code

print_script_step "Update Test Harness code"
# Store the current branch for the update
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
$UBUNTU_SCRIPT_DIR/auto-update.sh "$CURRENT_BRANCH"
verify_return_code

print_script_step "Revert needrestart config to default"
restore_needrestart

print_end_of_script

print_installation_success

if is_running_in_wsl; then
    print_script_step "Applying configuration changes (WSL, no reboot required)"
    sudo sysctl -p || true
    sudo modprobe ip6table_filter 2>/dev/null || echo "ip6table_filter module not available in the WSL kernel"
    printf "Log out and back in (or restart WSL) for docker group membership to take effect.\n"

    SDK_DOCKER_PACKAGE=$(cat $ROOT_DIR/backend/test_collections/matter/config.py | grep SDK_DOCKER_IMAGE | cut -d'"' -f 2 | cut -d"'" -f 2)
    SDK_DOCKER_TAG=$(cat $ROOT_DIR/backend/test_collections/matter/config.py | grep SDK_DOCKER_TAG | cut -d'"' -f 2 | cut -d"'" -f 2)
    if [[ -z $(sudo docker images -q $SDK_DOCKER_PACKAGE:$SDK_DOCKER_TAG) ]]; then
        print_script_step "Reminder: SDK image and sample apps still pending"
        printf "The SDK image is published for arm64 only, so the sample apps installation was skipped.\n"
        printf "After logging back in:\n"
        printf "  1. Build the SDK image locally (takes about an hour):\n"
        printf "     ./backend/test_collections/matter/scripts/build-local-sdk-image.sh\n"
        printf "  2. Install the sample apps:\n"
        printf "     ./scripts/update.sh\n"
    fi
    exit 0
fi

print_script_step "You need to reboot to finish setup"
printf "Do you want to reboot now? (Press 1 to reboot now)\n"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) sudo reboot; break;;
        No ) exit;;
    esac
done
