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
ROOT_DIR=$(realpath $(dirname "$0")/../..)
SCRIPT_DIR="$ROOT_DIR/scripts"

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

check_ubuntu_os_version
verify_return_code

if [ $# != 1 ] || [ $1 = "--help" ]; then
  echo "Usage:"
  echo "./scripts/ubuntu/auto-update.sh <branch_name>"
  echo "Mandatory: <branch_name>  branch name"
  exit 1
fi

print_script_step "Stopping Containers"
$SCRIPT_DIR/stop.sh

BRANCH_NAME=$1

print_script_step "Update Test Harness code"
$SCRIPT_DIR/update-th-code.sh "$BRANCH_NAME"
verify_return_code

print_script_step "Update Test Harness Setup"
$SCRIPT_DIR/update.sh "$BRANCH_NAME"
verify_return_code

print_end_of_script
