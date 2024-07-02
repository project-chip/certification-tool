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
FILE_PATH=$ROOT_DIR"/cli/pyproject.toml"

# Check if file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "File not found! This usually means that the submodules aren't initialized."
    exit 1
fi

# Function to extract and print dependencies from a section
print_dependencies() {
    section=$1
    echo -e "${section}"
    printf "%-30s %-20s\n" "Package Name" "Listed Version"
    echo "---------------------------------------------"
    awk -v section="$section" 'BEGIN{flag=0} $0 == section {flag=1; next} flag && /^\[/{exit} flag {print $0}' "$FILE_PATH" | \
    grep '=' | sed 's/ = /:/g' | tr -d '"' | tr -d ',' | while read -r line; do
        package_name=$(echo $line | cut -d: -f1)
        listed_version=$(echo $line | cut -d: -f2)
        printf "%-30s %-20s\n" "$package_name" "$listed_version"
    done
    echo ""  # Print an empty line as a separator
}

# Call the function for each section
print_dependencies "[tool.poetry.dependencies]"
print_dependencies "[tool.poetry.dev-dependencies]"
