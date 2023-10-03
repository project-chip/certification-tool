#!/bin/bash -e

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
set -x
set -e


# Usage: ./scripts/pi-setup/update-paa-certs.sh
#
# Will copy PAA certificates from SDK repository
#
# Environment variables can be used to override behaviour 
# - SDK_PATH (When set, SDK_SHA is ignored)
# - SDK_SHA 

# Paths
ROOT_DIR=$(realpath $(dirname "$0")/../..)
TMP_SDK_FOLDER="sdk-sparse"
TMP_SDK_PATH="/tmp/$TMP_SDK_FOLDER"
SDK_CERT_PATH="credentials/development/paa-root-certs"
CERT_PATH="/var/paa-root-certs"

# If SDK path is not present, then do local checkout
if [ -z "$SDK_PATH" ]
then

    # If SDK SHA is not present, then fetch from backend config
    if [ -z "$SDK_SHA" ]
    then
        cd $ROOT_DIR
        SDK_SHA=$(cat $ROOT_DIR/backend/app/core/config.py | grep SDK_SHA | cut -d'"' -f 2 | cut -d"'" -f 2)
    fi
    
    # Checkout SDK sparsely 
    rm -rf $TMP_SDK_PATH
    cd /tmp
    git clone --filter=blob:none --no-checkout --depth 1 --sparse https://github.com/project-chip/connectedhomeip.git $TMP_SDK_FOLDER
    cd $TMP_SDK_FOLDER
    git sparse-checkout init
    git sparse-checkout set $SDK_CERT_PATH
    git checkout -q $SDK_SHA
    SDK_PATH="$TMP_SDK_PATH"
fi

# Create folder if missing (owned by user)
if [ ! -d "$CERT_PATH" ]
then
    sudo mkdir -p $CERT_PATH
    sudo chown $USER:$USER $CERT_PATH
fi

# Copy certs from SDK
cp "$SDK_PATH/$SDK_CERT_PATH/"* $CERT_PATH/
