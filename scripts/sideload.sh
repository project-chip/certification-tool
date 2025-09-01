#! /usr/bin/env bash

 #
 # Copyright (c) 2024 Project CHIP Authors
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

ROOT_DIR=$(realpath $(dirname "$0")/..)
SCRIPT_DIR="$ROOT_DIR/scripts"


DATE_STR=$(date +"%F-%H-%M-%S")

SIDELOAD_LOGFILE_PATH="logs/sideload_$DATE_STR.log"

# Redirect all output (stdout and stderr) to both the terminal and the log file
exec > >(tee -a "$SIDELOAD_LOGFILE_PATH") 2>&1

# backend container
CONTAINER_NAME="certification-tool-backend-1"

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

print_script_step "Updating tests information"
docker exec -i $CONTAINER_NAME python3 /app/test_collections/matter/sdk_tests/support/python_testing/list_python_tests_classes.py
if [ $? -ne 0 ]; then
    echo "Unable to execute command in backend container. Could you please check if it is running?"
    exit 1
fi

# Retrieve backend container ID
print_script_step "Retrieving backend container ID..."
CONTAINER_ID=$(docker ps -qf "name=${CONTAINER_NAME}")

# Check if the container was found
if [ -z "$CONTAINER_ID" ]; then
    echo "Container '${CONTAINER_NAME}' not found."
    exit 1
fi

# Restart the container
print_script_step "Restarting container ${CONTAINER_NAME} (ID: ${CONTAINER_ID})..."
docker restart "$CONTAINER_ID"

# Check if the restart process was successful
if [ $? -eq 0 ]; then
    echo -n "Waiting for backend to start"
    CHECK_BACKEND_SERVICE="docker exec -i $CONTAINER_NAME curl --fail -s --output /dev/null http://localhost/docs"
    until $CHECK_BACKEND_SERVICE
    do
        echo -n "."
        sleep 5
    done
    echo "Container restarted successfully!"

else
    echo "Failed to restart the container!"
    exit 1
fi

print_end_of_script
