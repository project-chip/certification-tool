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

# WSL variant of scripts/update.sh (sync commit tracked in wsl-utils.sh).
# Identical except the docker images step builds the backend and frontend
# images locally instead of pulling them. Always use this instead of the stock
# update.sh on WSL: the stock pulls would overwrite the locally built images
# with arm64 ones.
#
# The test collections setup below installs the CLI and the sample apps. The
# sample apps come out of the SDK image, so on a fresh install run
# build-local-sdk-image.sh first.

ROOT_DIR=$(realpath $(dirname "$0")/../..)
SCRIPT_DIR="$ROOT_DIR/scripts"
WSL_SCRIPT_DIR="$SCRIPT_DIR/wsl"

source "$SCRIPT_DIR/utils.sh"
source "$WSL_SCRIPT_DIR/wsl-utils.sh"

require_wsl

print_start_of_script

check_wsl_scripts_sync "$ROOT_DIR"

print_script_step "Update Docker images"
$WSL_SCRIPT_DIR/build-local-images.sh
verify_return_code

print_script_step "Setup Test Collections"
$SCRIPT_DIR/update-setup-test-collections.sh
verify_return_code

print_end_of_script
