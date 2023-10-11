#!/bin/bash

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

# Set the path to the file containing the package list
FILE_PATH=$ROOT_DIR"/scripts/ubuntu/1-install-dependendcies.sh"

# Check if file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "File not found!"
    exit 1
fi

# Extract the package list from the file and remove comments
packagelist=($(sed -n '/packagelist=(/,/)/p' "$FILE_PATH" | sed -e '1d;$d;s/#.*//'))

printf "%-36s %-20s\n" "Package Name" "Installed Version"
echo "------------------------------------------------------"

for package in "${packagelist[@]}"; do
    package_name=$(echo $package | tr -d ',' | tr -d '[:space:]')
    if [ ! -z "$package_name" ]; then
        version=$(dpkg-query -W -f='${Version}' "$package_name" 2>/dev/null || echo "Not installed")
        # Remove trailing whitespaces from version
        version=$(echo $version | sed 's/[[:space:]]*$//')
        printf "%-36s %-20s\n" "$package_name" "$version"
    fi
done
