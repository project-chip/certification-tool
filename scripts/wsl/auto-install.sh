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

# Installs the Test Harness on WSL2 (optional development/test procedure, see
# README.md). Replays the stock install sequence, calling the stock scripts
# unmodified wherever they work on WSL and substituting the steps that do not:
# the machine configuration (no wlan interface or wpa_supplicant in WSL), the
# docker images step (the published images are arm64 only, so they are built
# locally), and the final reboot (logging out is enough on WSL).
#
# The SDK image build (about an hour) and the test collections setup that
# depends on it are deferred: this script ends with the two commands to run.
#
# Mirrors scripts/ubuntu/auto-install.sh and scripts/ubuntu/internal-auto-install.sh
# (sync commits tracked in wsl-utils.sh).

ROOT_DIR=$(realpath $(dirname "$0")/../..)
SCRIPT_DIR="$ROOT_DIR/scripts"
UBUNTU_SCRIPT_DIR="$SCRIPT_DIR/ubuntu"
WSL_SCRIPT_DIR="$SCRIPT_DIR/wsl"

source "$SCRIPT_DIR/utils.sh"
source "$WSL_SCRIPT_DIR/wsl-utils.sh"

require_wsl

LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILENAME=$(date +"log_wsl_auto_install_%F-%H-%M-%S")
exec > >(tee "$LOG_DIR/$LOG_FILENAME") 2>&1

print_start_of_script

check_wsl_scripts_sync "$ROOT_DIR"

check_installation_prerequisites
verify_return_code

# needrestart is not preinstalled on the WSL Ubuntu image, and the stock
# dependency script edits its config file unconditionally: make sure the file
# exists so the stock script runs unmodified.
sudo mkdir -p /etc/needrestart
sudo touch /etc/needrestart/needrestart.conf

print_script_step "Installing Test Harness Dependencies"
$UBUNTU_SCRIPT_DIR/1-install-dependencies.sh
verify_return_code

print_script_step "Installing Additional Dependencies"
$UBUNTU_SCRIPT_DIR/1.2-install-additional-dependencies.sh
verify_return_code

print_script_step "Configure Machine (WSL variant)"
$WSL_SCRIPT_DIR/machine-configuration.sh
verify_return_code

# The stock flow continues with auto-update.sh, which ends in the docker image
# downloads that cannot work on WSL. Replay its sequence up to that point and
# substitute the image step. The additional dependencies step it repeats is
# already done above and is not repeated here.
print_script_step "Update Test Harness code"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
$SCRIPT_DIR/update-th-code.sh "$CURRENT_BRANCH"
verify_return_code

print_script_step "Stopping Containers"
$SCRIPT_DIR/stop.sh

print_script_step "Check and fix Docker compatibility"
$SCRIPT_DIR/fix-docker-compatibility.sh
verify_return_code

print_script_step "Building Docker images locally"
$WSL_SCRIPT_DIR/build-local-images.sh
verify_return_code

print_script_step "Revert needrestart config to default"
sudo sed -i "s/\$nrconf{kernelhints} = -1;/#\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
sudo sed -i "s/\$nrconf{restart} = 'a';/#\$nrconf{restart} = 'i';/" /etc/needrestart/needrestart.conf

print_end_of_script

print_installation_success

print_script_step "Applying configuration changes (WSL, no reboot required)"
sudo sysctl -p || true
sudo modprobe ip6table_filter 2>/dev/null || echo "ip6table_filter module not available in the WSL kernel"
printf "Log out and back in (or restart WSL) for docker group membership to take effect.\n"

print_script_step "Remaining steps: SDK image and test collections"
printf "The SDK image is published for arm64 only, so it must be built locally and\n"
printf "the test collections setup that depends on it was deferred.\n"
printf "After logging back in:\n"
printf "  1. Build the SDK image locally (takes about an hour):\n"
printf "     ./scripts/wsl/build-local-sdk-image.sh\n"
printf "  2. Finish the setup (test collections, CLI, sample apps):\n"
printf "     ./scripts/wsl/update.sh\n"
