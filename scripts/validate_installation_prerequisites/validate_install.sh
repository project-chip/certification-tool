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

# Paths
TH_DIR="/app/certification-tool"
TH_DOCKER_REPO_INSTALL_FILE="$TH_DIR/scripts/ubuntu/1.1-install-docker-repository.sh"
TH_PACKAGE_LIST_FILE="$TH_DIR/scripts/ubuntu/package-dependency-list.txt"
MATTER_PROGRAM_DIR="$TH_DIR/backend/test_collections/matter"
MATTER_PACKAGE_LIST_FILE="$MATTER_PROGRAM_DIR/scripts/package-dependency-list.txt"

source "$TH_DIR/scripts/utils.sh"

print_start_of_script

print_script_step "Calling Install Docker Repository Script"
$TH_DOCKER_REPO_INSTALL_FILE
verify_return_code

IFS=$(echo -en "\r")
readarray th_package_list < "$TH_PACKAGE_LIST_FILE"
readarray matter_package_list < "$MATTER_PACKAGE_LIST_FILE"

for package in ${th_package_list[@]}; do
    print_script_step "Installing package: ${package[@]}"
    DEBIAN_FRONTEND=noninteractive apt-get satisfy ${package[@]} -y --allow-downgrades
    verify_return_code
done

for package in ${matter_package_list[@]}; do
    print_script_step "Installing package: ${package[@]}"
    DEBIAN_FRONTEND=noninteractive apt-get satisfy ${package[@]} -y --allow-downgrades
    verify_return_code
done

print_installation_success

print_end_of_script
