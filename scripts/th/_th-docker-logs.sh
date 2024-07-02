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

# Containers
BACKEND_CONTAINER_NAME="certification-tool-backend-1"
FRONTEND_CONTAINER_NAME="certification-tool-frontend-1"
DB_CONTAINER_NAME="certification-tool-db-1"
PROXY_CONTAINER_NAME="certification-tool-proxy-1"

# Function to check if a container is running and print the last 100 log lines
print_container_logs() {
    local container_name=$1

    echo
    echo
    echo "########################################################"
    echo "## Docker Logs for '${container_name}'"
    echo "##     Last 100 log lines:"
    echo "########################################################"

    if ! docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        echo "     The container is not running."
    else
        docker logs --tail 100 $container_name
    fi
}

echo
echo "^^ THE ABOVE DOCKER LOGS ARE PART OF THE '$DB_CONTAINER_NAME' CONTAINER. ^^"
echo "   IT'S UNKNOWN WHY THIS HAPPENS WITH THE DB CONTAINER ONLY, WHICH IS THE"
echo "   LOGS APPEARING BEFORE ITS HEADER TITLE, ANY HELP WITH THIS IS APPRECIATED"
echo 

# Call the function for each container
print_container_logs $BACKEND_CONTAINER_NAME
print_container_logs $FRONTEND_CONTAINER_NAME
print_container_logs $DB_CONTAINER_NAME
print_container_logs $PROXY_CONTAINER_NAME
