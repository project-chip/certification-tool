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

# Ensure noble-updates is present in apt sources.
# On minimal Ubuntu 24.04 images (e.g. Raspberry Pi), the sources file may only contain
# noble and noble-security.  Security point releases update runtime libraries
# (libmount1, zlib1g, libpcre2-8-0, etc.) to patch versions (e.g. -9ubuntu6.4), but the
# matching -dev packages that accept those versions only exist in noble-updates.
# Without this repo, apt-get satisfy fails with "held broken packages" when resolving
# transitive -dev dependencies for libgstreamer1.0-dev.
print_script_step "Ensuring noble-updates apt repository is configured"
SOURCES_FILE="/etc/apt/sources.list.d/ubuntu-sources.list"
if [ ! -f "$SOURCES_FILE" ]; then
    SOURCES_FILE="/etc/apt/sources.list"
fi
if ! grep -q "noble-updates" "$SOURCES_FILE" /etc/apt/sources.list.d/*.list 2>/dev/null; then
    echo "deb http://ports.ubuntu.com/ubuntu-ports/ noble-updates main restricted universe multiverse" \
        | sudo tee -a "$SOURCES_FILE"
fi
sudo DEBIAN_FRONTEND=noninteractive apt-get update

readarray -t packagelist < "$UBUNTU_SCRIPT_DIR/additional-dependency-list.txt"

for package in "${packagelist[@]}"; do
  [ -z "$package" ] && continue

  print_script_step "Installing additional package: $package"

  sudo DEBIAN_FRONTEND=noninteractive apt-get satisfy "$package" -y --allow-downgrades
done

print_end_of_script