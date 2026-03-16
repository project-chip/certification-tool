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
set -e

ROOT_DIR=$(realpath $(dirname "$0")/../..)
SCRIPT_DIR="$ROOT_DIR/scripts"
UBUNTU_SCRIPT_DIR="$SCRIPT_DIR/ubuntu"

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

print_script_step "Install additional dependencies"

# Ensure <codename>-updates is present in apt sources.
# On minimal Ubuntu images (e.g. Raspberry Pi), the sources file may only contain
# <codename> and <codename>-security.  Security point releases update runtime libraries
# (libmount1, zlib1g, libpcre2-8-0, etc.) to patch versions (e.g. -9ubuntu6.4), but the
# matching -dev packages that accept those versions only exist in <codename>-updates.
# Without this repo, apt-get satisfy fails with "held broken packages" when resolving
# transitive -dev dependencies for libgstreamer1.0-dev.
print_script_step "Ensuring <codename>-updates apt repository is configured"
UBUNTU_CODENAME=$(lsb_release -cs)
SOURCES_FILE="/etc/apt/sources.list.d/ubuntu.sources"
if [ -f "$SOURCES_FILE" ] && grep -q "^Suites:" "$SOURCES_FILE"; then
    if ! grep -q "${UBUNTU_CODENAME}-updates" "$SOURCES_FILE"; then
        sudo sed -i -E "/^Suites:.*\b(${UBUNTU_CODENAME}|${UBUNTU_CODENAME}-security)\b/ s/$/ ${UBUNTU_CODENAME}-updates/" "$SOURCES_FILE"
    fi
fi
sudo DEBIAN_FRONTEND=noninteractive apt-get update || \
    echo "Warning: apt-get update encountered errors, proceeding with existing package index"

# First, ensure all dev packages are up to date to match installed library versions.
# apt-get upgrade in the previous step may update runtime libraries (libmount1, libzstd1,
# libpcre2-8-0, libselinux1, zlib1g) to security-patch point releases (e.g. -9ubuntu6.4)
# while their -dev counterparts remain at the pre-upgrade version. This causes
# "held broken packages" errors when apt-get satisfy tries to install libgstreamer1.0-dev
# and its transitive -dev dependencies (which carry strict = version constraints).
# Upgrading all affected -dev packages first realigns them with the runtime libraries.
print_script_step "Updating development packages to match installed library versions"
sudo DEBIAN_FRONTEND=noninteractive apt-get install --only-upgrade -y \
    libmount-dev libblkid-dev \
    libzstd-dev \
    libpcre2-dev \
    libselinux1-dev \
    zlib1g-dev || true

readarray -t packagelist < "$UBUNTU_SCRIPT_DIR/additional-dependency-list.txt"

for package in "${packagelist[@]}"; do
  [ -z "$package" ] && continue

  print_script_step "Installing additional package: $package"

  sudo DEBIAN_FRONTEND=noninteractive apt-get satisfy "$package" -y --allow-downgrades
done

print_end_of_script