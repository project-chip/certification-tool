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
set -e

ROOT_DIR=$(realpath $(dirname "$0")/../..)
SCRIPT_DIR="$ROOT_DIR/scripts"

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

set +e
print_script_step "Verify docker.download.com is reachable"
# Verify docker.download.com is reachable before attempting to install the
# Docker Package Repo (network randomly fails after service restarts).
for i in {1..5}
do
    timeout 2 bash -c "(echo >/dev/tcp/docker.download.com/80) &>/dev/null"
    retVal=$?
    if [ $retVal -eq 0 ]; then
        echo "The docker.download.com is reacheable"
        break
    else
        echo "The docker.download.com is unreachable for try $i"
        sleep $(expr $i \* 2)
    fi

    if [ "$i" -eq '5' ]; then
        echo "Failed to stablish connection with the docker.download.com service."
        echo "Please verify your connection or try again later."
        exit 1
    fi
done

set -e
# Reference link: https://docs.docker.com/engine/install/ubuntu/
print_script_step "Add Docker's official GPG key"
sudo apt-get update -y
sudo apt-get install ca-certificates curl -y
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

print_script_step "Add the repository to Apt sources"
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y

print_end_of_script
