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

# Dev override files
BACKEND_COMPOSE_DEV="-f docker-compose.override-backend-dev.yml"
FRONTEND_COMPOSE_DEV="-f docker-compose.override-frontend-dev.yml"

# Parse args for which docker compose overrides to use
BACKEND_COMPOSE=""
FRONTEND_COMPOSE=""
COMPOSE_CACHE_OPTION=""
BACKEND_DEV=false
FRONTEND_DEV=false
for arg in "$@"
do
    case $arg in
        -b|--backend-dev)
        BACKEND_DEV=true
        BACKEND_COMPOSE=$BACKEND_COMPOSE_DEV
        shift # Remove --backend from processing
        ;;
        -f|--frontend-dev)
        FRONTEND_DEV=true
        FRONTEND_COMPOSE=$FRONTEND_COMPOSE_DEV
        shift # Remove --frontend from processing
        ;;
        *)
        OTHER_ARGUMENTS+=("$1")
        shift # Remove generic argument from processing
        ;;
    esac
done

# Do not exit in case of error
set +e

echo "*** Starting 'db' and 'proxy' docker containers"
docker compose -f docker-compose.yml up db proxy --detach
if [ $? -ne 0 ]; then
    echo "### Exit with Error ###"
    echo "    Unable to start containers."
    echo "    You can also pull the images manually using this command: $ 'docker compose -f docker-compose.yml pull db proxy'"
    exit 1
fi

echo "*** Starting 'backend' docker container"
docker compose -f docker-compose.yml $BACKEND_COMPOSE up backend --detach --no-build
if [ $? -ne 0 ]; then
    echo "### Exit with Error ###"
    echo "    Unable to start backend container."
    echo "    Check if the tag is correct in the docker compose file."
    echo "    You can also build the image manually using this command: $ './backend/scripts/build-docker-image.sh'"
    exit 1
fi

echo "*** Starting 'frontend' docker container"
docker compose -f docker-compose.yml $FRONTEND_COMPOSE up frontend --detach --no-build
if [ $? -ne 0 ]; then
    echo "### Exit with Error ###"
    echo "    Unable to start frontend container."
    echo "    Check if the tag is correct in the docker compose file."
    echo "    You can also build the image manually using this command: $ './frontend/scripts/build-docker-image.sh'"
    exit 1
fi

if [ "$FRONTEND_DEV" = true ] ; then
    echo "!!!! Matter TH frontend started in development mode."
    echo "!!!! Manually start frontend by connecting to the frontend container"
else
    echo -n "Waiting for frontend to start"
    until docker compose exec frontend curl --fail -s --output /dev/null http://localhost:4200
    do
        echo -n "."
        sleep 5
    done
    echo " done"
fi

if [ "$BACKEND_DEV" = true ] ; then
    echo "!!!! Matter TH backend started in development mode."
    echo "!!!! Manually start backend by connecting to the backend container"
else
    echo -n "Waiting for backend to start"
    until docker compose exec backend curl --fail -s --output /dev/null http://localhost/docs
    do
        echo -n "."
        sleep 5
    done
    echo " done"
fi
