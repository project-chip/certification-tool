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


printf "\n\n**********"
printf "\n*** Installing Dependencies ***\n"
$UBUNTU_SCRIPT_DIR/1-install-dependendcies.sh

printf "\n\n**********"
printf "\n*** Configure Machine ***\n"
$UBUNTU_SCRIPT_DIR/2-machine-cofiguration.sh

printf "\n\n**********"
printf "\n*** Getting Test Harness code ***\n"

$SCRIPT_DIR/update.sh

echo "*** Build Test Harness Docker containers"
# Note: `build.sh` shouln't normally be run with sudo
# but main user was just added to docker, so we still 
# need root to control docker until machine has been rebooted.
cd $ROOT_DIR && sudo ./scripts/build.sh --latest

printf "\n\n**********"
printf "\n*** Fetching sample apps ***\n"
$UBUNTU_SCRIPT_DIR/update-sample-apps.sh

printf "\n\n**********"
printf "\n*** Fetching PAA Certs from SDK ***\n"
$UBUNTU_SCRIPT_DIR/update-paa-certs.sh

printf "\n\n**********"
printf "\n*** You need to reboot to finish setup. ***\n"
printf "\n*** Do you want to reboot now? (Press 1 to reboot now)\n"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) sudo reboot; break;;
        No ) exit;;
    esac
done
