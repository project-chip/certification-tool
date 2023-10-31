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

CONTAINER_NAME="chip-certification-tool_backend_1"

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

# Fetch pip list from container
echo "----- Python Environment -----"
if command_exists_in_container pip; then
    pip_list=$(docker exec $CONTAINER_NAME pip list)
    echo "$pip_list"
elif command_exists_in_container pip3; then
    pip_list=$(docker exec $CONTAINER_NAME pip3 list)
    echo "$pip_list"
else
    echo "Neither pip nor pip3 is installed in the container."
fi

