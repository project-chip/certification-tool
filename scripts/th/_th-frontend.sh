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

# Function to check if command exists
command_exists () {
    type "$1" &> /dev/null ;
}

# Check Node version
if command_exists node; then
    node_version=$(node -v)
    echo "Node version: $node_version"
else
    echo "Node is not installed"
fi

# Check npm version
if command_exists npm; then
    npm_version=$(npm -v)
    echo "npm version: $npm_version"
else
    echo "npm is not installed"
fi

# Check Angular version
if command_exists ng; then
    ng_version=$(ng version)
    # Extract only the version number using grep and awk (as ng version command outputs multiple lines)
    angular_version=$(echo "$ng_version" | grep 'Angular CLI:' | awk '{print $3}')
    echo "Angular version: $angular_version"
else
    echo "Angular CLI is not installed"
fi
