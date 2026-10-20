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

# WSL variant of scripts/update-docker-images.sh (sync tracked in wsl-utils.sh).
# The stock script pulls the pinned backend and frontend images whenever their
# tag exists, but a pull of an image published only for arm64 (Raspberry Pi)
# can still "succeed" on another architecture with a platform mismatch warning
# and produce unusable containers. So each image is pulled only when the
# registry publishes it for this host's architecture, and otherwise built
# locally with the same stock build script the original uses as its fallback.
# The proxy and db images are multi-arch and are pulled as usual.

ROOT_DIR=$(realpath "$(dirname "$0")/../..")
SCRIPT_DIR="$ROOT_DIR/scripts"

# Exit in case anything goes wrong
set -e

source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/wsl/wsl-utils.sh"

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

HOST_ARCH=$(host_docker_arch)

# Tag that docker-compose.yml pins for an image (backend or frontend).
compose_pinned_tag()
{
    grep "ghcr.io/project-chip/csa-certification-tool-$1" "$ROOT_DIR/docker-compose.yml" | cut -d: -f3 | tr -d "' "
}

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
    pinned_tag=$(compose_pinned_tag "$name")
    if [ -n "$pinned_tag" ] && [ "$built_tag" != "$pinned_tag" ]; then
        echo "Retagging the built $name image ($built_tag) to the tag docker-compose.yml expects ($pinned_tag)"
newgrp docker << END
docker tag $repository:$built_tag $repository:$pinned_tag
END
    fi
}

provide_image()
{
    local name=$1
    local image archs
    image="ghcr.io/project-chip/csa-certification-tool-$name:$(compose_pinned_tag "$name")"
    archs=$(published_image_archs "$image")
    if [[ " $archs " == *" $HOST_ARCH "* ]]; then
        print_script_step "Downloading $name Docker image (published for $HOST_ARCH)"
        if newgrp docker << END
docker compose pull $name
END
        then
            return
        fi
        echo "The pull failed: building the $name image locally instead."
    else
        print_script_step "Building $name Docker image locally (published for: ${archs:-unknown}, not $HOST_ARCH)"
    fi
    # Heredoc delimiter is intentionally unquoted so the outer shell expands
    # $ROOT_DIR here; the literal quotes that remain are then parsed by the
    # inner `newgrp docker` subshell, correctly handling a path with spaces.
newgrp docker << END
    "$ROOT_DIR/$name/scripts/build-docker-image.sh"
END
    retag_to_compose_pin "$name"
}

provide_image backend
provide_image frontend

print_end_of_script
