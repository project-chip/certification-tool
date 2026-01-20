#! /usr/bin/env bash

#
# Copyright (c) 2025 Project CHIP Authors
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

# This script fixes Docker 29.x compatibility issues with Traefik
# by downgrading to the latest compatible Docker 28.x version.

set -e

ROOT_DIR=$(realpath $(dirname "$0")/..)
SCRIPT_DIR="$ROOT_DIR/scripts"

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

# Function to get Docker version
get_docker_version() {
    if command -v docker >/dev/null 2>&1; then
        docker --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1
    else
        echo "not_installed"
    fi
}

# Function to compare version numbers
version_greater_than() {
    # Returns 0 (true) if $1 > $2
    [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" != "$1" ]
}

print_script_step "Checking current Docker version"
CURRENT_VERSION=$(get_docker_version)

if [ "$CURRENT_VERSION" = "not_installed" ]; then
    echo "Docker is not installed. Please install Docker first using the installation scripts."
    exit 1
fi

echo "Current Docker version: $CURRENT_VERSION"

# Check if Docker version is 29.x or higher
if version_greater_than "$CURRENT_VERSION" "28.9.9"; then
    print_script_step "Docker version $CURRENT_VERSION is >= 29.x, which has compatibility issues with Traefik"
    print_script_step "Downgrading Docker to a compatible version (latest 28.x)"

    # Remove current Docker installation
    print_script_step "Removing current Docker installation"
    sudo apt-get remove -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin || true

    # Ensure Docker repository is available
    if [ ! -f /etc/apt/sources.list.d/docker.list ]; then
        echo "Docker repository not found. Setting up Docker repository..."
        $SCRIPT_DIR/ubuntu/1.1-install-docker-repository.sh
    fi

    # Update package cache
    sudo apt-get update -y

    # Install Docker version using the same logic as the working fix
    print_script_step "Installing Docker (excluding version 29.x)"

    # Get the latest version that is not 29.x (same logic as working fix)
    DOCKER_VERSION=$(apt-cache madison docker-ce | awk '$3 !~ /^5:29\./ {print $3; exit}')

    if [ -n "$DOCKER_VERSION" ]; then
        print_script_step "Installing docker-ce version $DOCKER_VERSION (excluding 29.x)"
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-downgrades docker-ce=$DOCKER_VERSION docker-ce-cli=$DOCKER_VERSION containerd.io docker-buildx-plugin docker-compose-plugin
    else
        echo "ERROR: No suitable docker-ce version found (excluding 29.x)"
        exit 1
    fi

    # Hold Docker packages to prevent automatic upgrades
    print_script_step "Holding Docker packages to prevent automatic upgrades to 29.x"
    sudo apt-mark hold docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Verify installation
    NEW_VERSION=$(get_docker_version)
    echo "New Docker version: $NEW_VERSION"

    if version_greater_than "$NEW_VERSION" "28.9.9"; then
        echo "WARNING: Docker version is still >= 29.x. You may need to manually downgrade."
        echo "Current version: $NEW_VERSION"
        exit 1
    fi

    print_script_step "Docker successfully downgraded to version $NEW_VERSION"

    # Restart Docker service
    print_script_step "Restarting Docker service"
    sudo systemctl restart docker

    # Add current user to docker group if not already added
    if ! groups $USER | grep &>/dev/null '\bdocker\b'; then
        print_script_step "Adding user $USER to docker group"
        sudo usermod -aG docker $USER
        echo "NOTE: You may need to log out and back in for docker group changes to take effect"
    fi

    print_script_step "Docker compatibility fix completed successfully"

else
    echo "Docker version $CURRENT_VERSION is compatible (< 29.x). No action needed."
fi

print_end_of_script