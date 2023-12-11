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

if [ $# != 1 ] || [ $1 = "--help" ]; then
  echo "Usage:"
  echo "./scripts/auto-update.sh <branch_name>"
  echo "Mandatory: <branch_name>  branch name"
  exit 1
fi

BRANCH_NAME=$1

# It is necessary to update the branch references from origin
# to prevent unrecognized branch error during checkout.
git fetch 

printf "\n\n**********"
printf "\n*** Getting Test Harness code ***\n"

$SCRIPT_DIR/update.sh "$BRANCH_NAME"

printf "\n\n**********"
printf "\n*** Fetching sample apps ***\n"
$UBUNTU_SCRIPT_DIR/update-sample-apps.sh

printf "\n\n**********"
printf "\n*** Fetching PAA Certs from SDK ***\n"
$UBUNTU_SCRIPT_DIR/update-paa-certs.sh

printf "\n\n**********"
printf "\n*** Stoping Containers ***\n"
$SCRIPT_DIR/stop.sh

printf "\n\n**********"
printf "\n*** Building Clean Images ***\n"
$SCRIPT_DIR/build.sh --latest --no-cache
