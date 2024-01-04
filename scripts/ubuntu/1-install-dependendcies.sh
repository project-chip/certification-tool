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

# Install Docker Package Repo
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor --yes -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Silence user prompts about reboot and service restart required (script will prompt user to reboot in the end)
sudo sed -i "s/#\$nrconf{kernelhints} = -1;/\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
sudo sed -i "s/#\$nrconf{restart} = 'i';/\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf

sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# TODO Comment on what dependency is required for:
packagelist=(
    apt-transport-https
    avahi-utils                   # Matter uses Avahi
    ca-certificates
    curl
    docker-ce                     # Test Harness uses Docker
    figlet
    g++
    gcc
    generate-ninja
    git                           # Update to latest git for code checkout
    gnupg
    libavahi-client-dev
    libcairo2-dev
    libdbus-1-dev
    libgirepository1.0-dev
    libglib2.0-dev
    libreadline-dev
    libssl-dev
    lsb-release
    net-tools
    ninja-build
    npm
    pkg-config
    python3-pip                   # Test Harness CLI uses Python              
    python3-venv                  # Test Harness CLI uses Python
    software-properties-common
    toilet
    unzip

)
sudo DEBIAN_FRONTEND=noninteractive sudo apt-get install ${packagelist[@]} -y

# Install Docker Compose, needed for Test Harness
sudo pip3 install docker==6.1.3
sudo pip3 install docker-compose

# Install Peotry, needed for Test Harness CLI
curl -sSL https://install.python-poetry.org | python3 -
