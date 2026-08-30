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

ROOT_DIR=$(realpath "$(dirname "$0")/../..")
SCRIPT_DIR="$ROOT_DIR/scripts"

# Exit in case anything goes wrong
set -e

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

cd "$ROOT_DIR"

# Ensure .env exists
./scripts/install-default-env.sh

# As this might be run during setup we use `newgrp` command to ensure
# docker works.
print_script_step "Downloading proxy and db Docker images"
newgrp docker << END
docker compose pull db proxy
END

# The stock build scripts tag images with the submodule's commit (plus
# "-local" when its tree has changes), while docker-compose.yml references a
# pinned tag. Retag the built image to the pinned tag when they differ, so
# compose finds it instead of trying to download it.
retag_to_compose_pin()
{
    local name=$1
    local repository built_tag pinned_tag
    repository="ghcr.io/project-chip/csa-certification-tool-$name"
    built_tag=$(git -C "$ROOT_DIR/$name" rev-parse --short HEAD)$(git -C "$ROOT_DIR/$name" diff -s --exit-code || echo "-local")
    pinned_tag=$(grep "$repository" "$ROOT_DIR/docker-compose.yml" | cut -d: -f3 | tr -d "' ")
    if [ -n "$pinned_tag" ] && [ "$built_tag" != "$pinned_tag" ]; then
        echo "Retagging the built $name image ($built_tag) to the tag docker-compose.yml expects ($pinned_tag)"
newgrp docker << END
docker tag $repository:$built_tag $repository:$pinned_tag
END
    fi
}

print_script_step "Building backend Docker image locally"
# The backend Dockerfile installed npm@latest until certification-tool-backend
# PR 341 removed the nodejs/npm install entirely, and npm 12 dropped support
# for the image's node version. While the pinned backend predates that
# removal, pin npm at build time and restore the file afterwards.
NPM_PATCHED=false
if grep -q "npm install -g npm@latest" "$ROOT_DIR/backend/Dockerfile"; then
    print_script_step "Patching known npm issue in the backend Dockerfile"
    echo "The pinned backend installs npm@latest, which no longer supports the image's"
    echo "node version. Pinning npm for this build (newer backends no longer install npm)."
    sed -i "s/npm install -g npm@latest/npm install -g npm@11/" "$ROOT_DIR/backend/Dockerfile"
    NPM_PATCHED=true
fi
newgrp docker << END
    $ROOT_DIR/backend/scripts/build-docker-image.sh
END
retag_to_compose_pin backend
if $NPM_PATCHED; then
    git -C "$ROOT_DIR/backend" checkout -- Dockerfile
fi

print_script_step "Building frontend Docker image locally"
newgrp docker << END
    $ROOT_DIR/frontend/scripts/build-docker-image.sh
END
retag_to_compose_pin frontend

print_end_of_script
