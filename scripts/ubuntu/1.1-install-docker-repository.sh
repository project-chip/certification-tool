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

print_script_step "Verify docker.download.com is reachable"
# Verify docker.download.com is reachable before attempting to install the
# Docker Package Repo (network randomly fails after service restarts).
# A ping will be attempted and retried in increments of 1 second before
# a 5 minute timeout.
timeout 300s bash -c '
start_time=$(date)
echo "Ping started at: $start_time"
while :; do
  if ping -c 1 docker.download.com | grep -q "1 received"; then
    echo "Ping docker.download.com successful"
    end_time=$(date)
    echo "Ping ended at: $end_time"
    echo "Ping duration: $(($(date +%s) - $(date -d "$start_time" +%s))) seconds"
    break
  fi
  echo "Ping docker.download.com failed, retrying..."
  sleep 1
done
if [ $? -eq 124 ]; then
  end_time=$(date)
  echo "docker.download.com: Timeout reached"
  echo "Ping ended at: $end_time"
  echo "Ping duration: $(($(date +%s) - $(date -d "$start_time" +%s))) seconds"
fi
'

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
