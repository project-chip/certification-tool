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
cd $ROOT_DIR

SDK_SHA=$(cat $ROOT_DIR/backend/app/core/config.py | grep SDK_SHA | cut -d'"' -f 2 | cut -d"'" -f 2)
SDK_DOCKER_IMAGE=$(cat $ROOT_DIR/backend/app/core/config.py | grep SDK_DOCKER_IMAGE | cut -d'"' -f 2 | cut -d"'" -f 2)
SDK_DOCKER_TAG=$(cat $ROOT_DIR/backend/app/core/config.py | grep SDK_DOCKER_TAG | cut -d'"' -f 2 | cut -d"'" -f 2)

read_version() {
    # Input validation for path
    if [ -z "$1" ]; then
        echo "Please provide a path."
        return 1
    fi

    # Input validation for title
    if [ -z "$2" ]; then
        echo "Please provide a title."
        return 1
    fi

    file_path="$1"
    title="$2"

    # Check if file exists
    if [ ! -f "$file_path" ]; then
        echo "File not found!"
        return 1
    fi

    # Read the file content into a variable
    file_content=$(cat "$file_path")

    # Print the title and file content
    echo "$title: $file_content"

    cd $ROOT_DIR
}

read_version $ROOT_DIR"/backend/.version_information" "Version"
read_version $ROOT_DIR"/backend/.sha_information" "SHA"
echo 'SDK SHA:' $SDK_SHA
echo 'Docker image:' $SDK_DOCKER_IMAGE
echo 'Docker tag:' $SDK_DOCKER_TAG