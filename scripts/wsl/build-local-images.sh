#! /usr/bin/env bash

 #
 # Copyright (c) 2026 Project CHIP Authors
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

# WSL variant of scripts/update-docker-images.sh (sync commit tracked in
# wsl-utils.sh). The published backend and frontend images are built for arm64
# (Raspberry Pi) only, and a pull of a single-arch image on another
# architecture can still "succeed" with a platform mismatch warning and
# produce unusable containers. So instead of pulling, this builds both images
# locally with the same stock build scripts the original uses as its pull
# fallback. The proxy and db images are multi-arch and are pulled as usual.

ROOT_DIR=$(realpath $(dirname "$0")/../..)
SCRIPT_DIR="$ROOT_DIR/scripts"

# Exit in case anything goes wrong
set -e

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

cd $ROOT_DIR

# Ensure .env exists
./scripts/install-default-env.sh

# As this might be run during setup we use `newgrp` command to ensure
# docker works.
print_script_step "Downloading proxy and db Docker images"
newgrp docker << END
docker compose pull db proxy
END

print_script_step "Building backend Docker image locally"
newgrp docker << END
    $ROOT_DIR/backend/scripts/build-docker-image.sh
END

print_script_step "Building frontend Docker image locally"
newgrp docker << END
    $ROOT_DIR/frontend/scripts/build-docker-image.sh
END

print_end_of_script
