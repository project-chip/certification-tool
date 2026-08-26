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

# Exit in case anything goes wrong
set -e

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

cd $ROOT_DIR
# Ensure .env exists
./scripts/install-default-env.sh

# Download docker images from docker-compose.yml.
# As this might be run during setup we use `newgrp` command to ensure 
# docker works.
BUILD_BACKEND=false
BUILD_FRONTEND=false
set +e

# The published backend/frontend images are built for arm64 (Raspberry Pi)
# only. On other host architectures a pull of a single-arch image can still
# "succeed" with a platform mismatch warning and produce unusable containers,
# so skip the pulls and build the images locally instead.
HOST_ARCH=$(uname -m)
if [ "$HOST_ARCH" != "aarch64" ]; then
    print_script_step "Published images are arm64 only: building locally on $HOST_ARCH"
    BUILD_BACKEND=true
    BUILD_FRONTEND=true
else # arm64: download the published images

print_script_step "Downloading backend Docker image"
newgrp docker << END
docker compose pull backend
END
if [ $? -ne 0 ]; then
    BUILD_BACKEND=true
fi

print_script_step "Downloading frontend Docker image"
newgrp docker << END
docker compose pull frontend
END
if [ $? -ne 0 ]; then
    BUILD_FRONTEND=true
fi

fi # HOST_ARCH check
set -e

print_script_step "Downloading proxy and db Docker images"
newgrp docker << END
docker compose pull db proxy
END

# In case of failure, the images will be built locally
if $BUILD_BACKEND; then
newgrp docker << END
    $ROOT_DIR/backend/scripts/build-docker-image.sh
END
fi

if $BUILD_FRONTEND; then
newgrp docker << END
    $ROOT_DIR/frontend/scripts/build-docker-image.sh
END
fi

print_end_of_script
