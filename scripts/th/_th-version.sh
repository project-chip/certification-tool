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

# Containers
BACKEND_CONTAINER_NAME="certification-tool-backend-1"
FRONTEND_CONTAINER_NAME="certification-tool-frontend-1"
DB_CONTAINER_NAME="certification-tool-db-1"
PROXY_CONTAINER_NAME="certification-tool-proxy-1"

read_version() {
    file_path="$1"
    title="$2"

    # Check if the container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${BACKEND_CONTAINER_NAME}$"; then
        echo "$title: The '$BACKEND_CONTAINER_NAME' container it not running."
        return
    fi

    # Check if file exists in the container
    if ! docker exec "$BACKEND_CONTAINER_NAME" sh -c "[ -f $file_path ]"; then
        echo "File '$file_path' not found in the container!"
        return 1
    fi

    # Read the file content from the container into a variable
    file_content=$(docker exec "$BACKEND_CONTAINER_NAME" cat "$file_path")

    # Print the title and file content
    echo "$title: $file_content"
}

show_backend_info() {
    # Check if the container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${BACKEND_CONTAINER_NAME}$"; then
        echo
        echo "$BACKEND_CONTAINER_NAME"
        echo "     The container is not running."
        return
    fi

    # Get info
    FILE_PATH1="test_collections/matter/config.py"
    FILE_PATH2="app/core/config.py"
    if docker exec $BACKEND_CONTAINER_NAME sh -c "[ -f $FILE_PATH1 ]"; then
        FILE_PATH=$FILE_PATH1
    elif docker exec $BACKEND_CONTAINER_NAME sh -c "[ -f $FILE_PATH2 ]"; then
        FILE_PATH=$FILE_PATH2
    else
        echo "Neither '$FILE_PATH1' nor '$FILE_PATH1' file paths exist."
        exit 1
    fi
    SDK_SHA=$(docker exec $BACKEND_CONTAINER_NAME sh -c "grep SDK_SHA $FILE_PATH | cut -d'\"' -f 2 | cut -d\"'\" -f 2")
    inspect_output_backend=$(docker inspect $BACKEND_CONTAINER_NAME)
    dc_version_backend=$(echo "$inspect_output_backend" | grep -oP '"com.docker.compose.version": "\K[^"]+')
    os=$(echo "$inspect_output_backend" | grep -oP '"org.opencontainers.image.ref.name": "\K[^"]+')
    os_version=$(echo "$inspect_output_backend" | grep -oP '"org.opencontainers.image.version": "\K[^"]+')
    image_backend=$(echo "$inspect_output_backend" | grep -oP '"Image": "\K[^"]+' | grep -v '^sha')

    # Print info
    echo
    echo "$BACKEND_CONTAINER_NAME"
    echo "     Docker Compose Version: $dc_version_backend"
    echo "     Image: $image_backend"
    echo "     OS: $os $os_version"
    echo "     SDK SHA: $SDK_SHA"
}

show_frontend_info() {
    # Check if the container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${FRONTEND_CONTAINER_NAME}$"; then
        echo
        echo "$FRONTEND_CONTAINER_NAME"
        echo "     The container is not running."
        return
    fi

    # Get info
    inspect_output_frontend=$(docker inspect $FRONTEND_CONTAINER_NAME)
    dc_version_frontend=$(echo "$inspect_output_frontend" | grep -oP '"com.docker.compose.version": "\K[^"]+')
    image_frontend=$(echo "$inspect_output_frontend" | grep -oP '"Image": "\K[^"]+' | grep -v '^sha')

    # Print info
    echo
    echo "$FRONTEND_CONTAINER_NAME"
    echo "     Docker Compose Version: $dc_version_frontend"
    echo "     Image: $image_frontend"
}

show_db_info() {
    # Check if the container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER_NAME}$"; then
        echo
        echo "$DB_CONTAINER_NAME"
        echo "     The container is not running."
        return
    fi

    # Get info
    inspect_output_db=$(docker inspect $DB_CONTAINER_NAME)
    dc_version_db=$(echo "$inspect_output_db" | grep -oP '"com.docker.compose.version": "\K[^"]+')
    image_db=$(echo "$inspect_output_db" | grep -oP '"Image": "\K[^"]+' | grep -v '^sha')
    version_db_app=$(echo "$inspect_output_db" | grep -oP '"PG_VERSION=[^"]+' | cut -d'=' -f2)

    # Print info
    echo
    echo "$DB_CONTAINER_NAME"
    echo "     Docker Compose Version: $dc_version_db"
    echo "     Image: $image_db"
    echo "     DB App Version: $version_db_app"
}

show_proxy_info() {
    # Check if the container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${PROXY_CONTAINER_NAME}$"; then
        echo
        echo "$PROXY_CONTAINER_NAME"
        echo "     The container is not running."
        return
    fi

    # Get info
    inspect_output_proxy=$(docker inspect $PROXY_CONTAINER_NAME)
    dc_version_proxy=$(echo "$inspect_output_proxy" | grep -oP '"com.docker.compose.version": "\K[^"]+')
    image_proxy=$(echo "$inspect_output_proxy" | grep -oP '"Image": "\K[^"]+' | grep -v '^sha')

    # Print info
    echo
    echo "$PROXY_CONTAINER_NAME"
    echo "     Docker Compose Version: $dc_version_proxy"
    echo "     Image: $image_proxy"
}

# Show Test Harness version info
read_version ".version_information" "Version"
read_version ".sha_information" "SHA"

# Show Test Harness components version info
show_backend_info
show_frontend_info
show_db_info
show_proxy_info