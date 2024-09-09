#! /usr/bin/env bash

 #
 # Copyright (c) 2024 Project CHIP Authors
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

# A way to validate the installation of packages used by the Matter Test
# harness has been created.
# This is a common/recurring problem because some packages no longer exist
# or the installation method changes (Docker, for example).
# Therefore, we can use this script to periodically validate whether the 
# packages are available for installation without having to perform a
# complete system installation.
#
# Usage: ./scripts/validate_installation_prerequisites/build_and_run.sh

set -e

TH_DIR=$(realpath $(dirname "$0")/../..)

source "$TH_DIR/scripts/utils.sh"

print_start_of_script

CONTAINER_TH_DIR="/app/certification-tool"
VALIDATE_SCRIPT_DIR="scripts/validate_installation_prerequisites"
CONTAINER_VALIDATE_SCRIPT="$CONTAINER_TH_DIR/$VALIDATE_SCRIPT_DIR/validate_install.sh"
DOCKER_IMAGE="csa-certification-tool-validation:v1"

cd $TH_DIR/$VALIDATE_SCRIPT_DIR

DOCKER_IMAGE_FOUND=$(docker images -q $DOCKER_IMAGE)

if [[ -z "$DOCKER_IMAGE_FOUND" ]]; then
    print_script_step "Building '$DOCKER_IMAGE' image"
    docker build -t $DOCKER_IMAGE .
else
    print_script_step "Validation Docker image already exists"
    echo "$DOCKER_IMAGE"
fi

print_script_step "Running Validation Script"
docker run -v $TH_DIR:/app/certification-tool:ro -it $DOCKER_IMAGE $CONTAINER_VALIDATE_SCRIPT

print_end_of_script
