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
 
CONTAINER_NAME="certification-tool-frontend-1"

# Check if the container is running
container_running=$(docker inspect -f '{{.State.Running}}' $CONTAINER_NAME 2>/dev/null)

# If the docker inspect command fails or the container is not running, notify and exit
if [ "$?" -ne 0 ] || [ "$container_running" != "true" ]; then
    echo "The container \"$CONTAINER_NAME\" is not running.\nPlease start it and try again."
    exit 1
fi

# Function to check if command exists inside the container
command_exists_in_container () {
    docker exec $CONTAINER_NAME sh -c "type $1" &> /dev/null
}

# Check Node version
if command_exists_in_container node; then
    node_version=$(docker exec $CONTAINER_NAME node -v)
else
    node_version="Not installed in the container"
fi

# Check npm version
if command_exists_in_container npm; then
    npm_version=$(docker exec $CONTAINER_NAME npm -v)
else
    npm_version="Not installed in the container"
fi

# Fetch Angular version from package.json
angular_version=$(docker exec $CONTAINER_NAME sh -c "cat package.json | grep '@angular/core' | awk -F':' '{print $2}'" | sed 's/[^0-9.]*//g')

if [ -z "$angular_version" ]; then
    angular_version="Not found in package.json"
fi

# Print versions
echo "----- JavaScript/TypeScript Environments -----"
echo "Node version: $node_version"
echo "npm version: $npm_version"
echo "Angular version: $angular_version"
