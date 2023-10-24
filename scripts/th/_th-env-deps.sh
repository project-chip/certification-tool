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

# Function to check if a command exists
command_exists () {
    type "$1" &> /dev/null
}

# Fetch Node, npm, and Angular versions locally
echo "----- JavaScript/TypeScript Environments -----"

if command_exists node; then
    echo "Node version: $(node -v)"
else
    echo "Node is not installed."
fi

if command_exists npm; then
    echo "npm version: $(npm -v)"
else
    echo "npm is not installed."
fi

if command_exists ng; then
    # Assuming that Angular CLI is installed globally and you can use 'ng version'
    angular_version=$(ng version 2>&1 | grep 'Angular CLI:' | awk '{print $3}')
    echo "Angular version: $angular_version"
else
    echo "Angular CLI is not installed."
fi
echo ""

# Fetch pip list locally
echo "----- Python Environment -----"
if command_exists pip; then
    pip list
elif command_exists pip3; then
    pip3 list
else
    echo "Neither pip nor pip3 is found on the system."
fi

