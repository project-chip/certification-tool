#! /usr/bin/env bash

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
ROOT_DIR=$(realpath $(dirname "$0")/..)

## SET BACKEND PATH ENV
KEY="BACKEND_FILEPATH_ON_HOST"
VALUE=$(readlink -f $ROOT_DIR/backend)
export $KEY=$VALUE

cd $ROOT_DIR

# Exit in case of error
set -e

# Ensure .env exists
./scripts/install-default-env.sh

# Record Backend SHA to a file
sh ./scripts/record-backend-sha-version.sh

# Dev override files
BACKEND_COMPOSE="-f docker-compose.override-backend-dev.yml"
FRONTEND_COMPOSE="-f docker-compose.override-frontend-dev.yml"

# Parse args for which docker-compose overrides to use
DEV_COMPOSE_FILES=""
COMPOSE_CACHE_OPTION=""
BACKEND_DEV=false
FRONTEND_DEV=false
for arg in "$@"
do
    case $arg in
        -b|--backend-dev)
        BACKEND_DEV=true
        DEV_COMPOSE_FILES="$DEV_COMPOSE_FILES $BACKEND_COMPOSE"
        shift # Remove --backend from processing
        ;;
        -f|--frontend-dev)
        FRONTEND_DEV=true
        DEV_COMPOSE_FILES="$DEV_COMPOSE_FILES $FRONTEND_COMPOSE"
        shift # Remove --frontend from processing
        ;;
        --build-no-cache)
        COMPOSE_CACHE_OPTION="--no-cache"
        shift # Remove --build-no-cache from processing
        ;;
        *)
        OTHER_ARGUMENTS+=("$1")
        shift # Remove generic argument from processing
        ;;
    esac
done


docker-compose \
-f docker-compose.yml \
$DEV_COMPOSE_FILES \
config > docker-stack.yml

if [ ! -z "$COMPOSE_CACHE_OPTION" ] ; then
    echo "Building no-cache"
    docker-compose -f docker-stack.yml build $COMPOSE_CACHE_OPTION
fi

docker-compose -f docker-stack.yml up -d

if [ "$FRONTEND_DEV" = true ] ; then
    echo "!!!! Matter TH frontend started in development mode."
    echo "!!!! Manually start frontend by connecting to the frontend container"
fi

if [ "$BACKEND_DEV" = true ] ; then
    echo "!!!! Matter TH backend started in development mode."
    echo "!!!! Manually start backend by connecting to the backend container"
fi
