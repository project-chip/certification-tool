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

# Builds the SDK image (chip-cert-bins) locally for the host architecture,
# tagged exactly as the backend expects. Needed on non-arm64 hosts (e.g. WSL),
# where the published image is not available.
#
# Usage: build-local-sdk-image.sh [dockerfile_ref]
#   dockerfile_ref  Optional git ref of the connectedhomeip repo to fetch the
#                   Dockerfile from. Defaults to the pinned SDK_DOCKER_TAG.
#                   Pass "master" if the Dockerfile at the pinned tag fails to
#                   build (e.g. due to fixes that landed after the tag).

set -e
ROOT_DIR=$(realpath "$(dirname "$0")/../..")
SCRIPT_DIR="$ROOT_DIR/scripts"
MATTER_PROGRAM_DIR="$ROOT_DIR/backend/test_collections/matter"

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_PATH="$LOG_DIR/$(date +"log_build_local_sdk_image_%F-%H-%M-%S")"

SDK_DOCKER_PACKAGE=$(cat $MATTER_PROGRAM_DIR/config.py | grep SDK_DOCKER_IMAGE | cut -d'"' -f 2 | cut -d"'" -f 2)
SDK_DOCKER_TAG=$(cat $MATTER_PROGRAM_DIR/config.py | grep SDK_DOCKER_TAG | cut -d'"' -f 2 | cut -d"'" -f 2)
if [[ -z "$SDK_DOCKER_PACKAGE" || -z "$SDK_DOCKER_TAG" ]]; then
    echo "ERROR: could not read SDK_DOCKER_IMAGE / SDK_DOCKER_TAG from $MATTER_PROGRAM_DIR/config.py"
    exit 1
fi
SDK_DOCKER_IMAGE=$SDK_DOCKER_PACKAGE:$SDK_DOCKER_TAG
DOCKERFILE_REF=${1:-$SDK_DOCKER_TAG}

if ! command -v docker > /dev/null; then
    echo "ERROR: docker is not installed (run the installer first)"
    exit 1
fi

# Map the host architecture to the docker platform architecture
case "$(uname -m)" in
    x86_64)  HOST_DOCKER_ARCH="amd64" ;;
    aarch64) HOST_DOCKER_ARCH="arm64" ;;
    armv7l)  HOST_DOCKER_ARCH="arm" ;;
    *)       HOST_DOCKER_ARCH="$(uname -m)" ;;
esac

if [[ -n $(sudo docker images -q $SDK_DOCKER_IMAGE) ]]; then
    IMAGE_ARCH=$(sudo docker image inspect --format '{{.Architecture}}' $SDK_DOCKER_IMAGE)
    if [[ "$IMAGE_ARCH" == "$HOST_DOCKER_ARCH" ]]; then
        print_script_step "Nothing to do"
        echo "The SDK image already exists locally for this architecture ($IMAGE_ARCH):"
        echo "$SDK_DOCKER_IMAGE"
        print_end_of_script
        exit 0
    fi
    print_script_step "Existing image has the wrong architecture"
    echo "The SDK image exists locally but is $IMAGE_ARCH while the host needs"
    echo "$HOST_DOCKER_ARCH. Rebuilding it for the host architecture."
fi

BUILD_DIR=$(mktemp -d)
trap 'rm -rf $BUILD_DIR' EXIT

print_script_step "Fetching the chip-cert-bins Dockerfile at ref $DOCKERFILE_REF"
DOCKERFILE_URL="https://raw.githubusercontent.com/project-chip/connectedhomeip/$DOCKERFILE_REF/integrations/docker/images/chip-cert-bins/Dockerfile"
if ! curl -sfL "$DOCKERFILE_URL" -o $BUILD_DIR/Dockerfile; then
    echo "ERROR: could not fetch the Dockerfile from $DOCKERFILE_URL"
    echo "Check the network connection and that the ref '$DOCKERFILE_REF' exists."
    exit 1
fi

# Building locally means running a Dockerfile that has not been built since
# its image was published (arm64 installs download the prebuilt image, so the
# Dockerfile at the pinned SDK_DOCKER_TAG never runs again). That Dockerfile
# fetches the latest gn sources, and today's gn no longer builds in this older
# environment. Apply the fix the current SDK Dockerfile already uses for this:
# install the distro gn package instead of compiling gn.
if grep -q "git clone https://gn.googlesource.com/gn" $BUILD_DIR/Dockerfile; then
    print_script_step "Patching known gn issue in the Dockerfile"
    echo "This Dockerfile builds the gn tool from unpinned tip-of-tree source, which"
    echo "no longer compiles with the image's toolchain. Replacing that block with"
    echo "the generate-ninja distro package (the current SDK Dockerfile's fix)."
    python3 - "$BUILD_DIR/Dockerfile" <<'PYEOF'
import re
import sys

path = sys.argv[1]
src = open(path).read()
block = re.search(r"# build and install gn\nRUN set -x \\\n(?:.*\n)*?    && : # last line\n", src)
if not block:
    print("WARNING: could not locate the gn build block, leaving the Dockerfile unpatched")
    sys.exit(0)
replacement = (
    "# build and install gn (patched by build-local-sdk-image.sh: gn tip-of-tree\n"
    "# no longer builds with this image's toolchain, install the distro package)\n"
    "RUN apt-get update \\\n"
    "    && DEBIAN_FRONTEND=noninteractive apt-get install -fy generate-ninja \\\n"
    "    && rm -rf /var/lib/apt/lists/ \\\n"
    "    && : # last line\n"
)
open(path, "w").write(src.replace(block.group(0), replacement))
print("gn block patched")
PYEOF
fi

print_script_step "Building '$SDK_DOCKER_IMAGE' for $(uname -m) (takes about an hour)"
echo "Build output is also logged to: $LOG_PATH"
set +e
sudo docker build --build-arg COMMITHASH=$SDK_DOCKER_TAG -t $SDK_DOCKER_IMAGE $BUILD_DIR 2>&1 | tee "$LOG_PATH"
BUILD_EXIT=${PIPESTATUS[0]}
set -e

if [[ $BUILD_EXIT -ne 0 ]]; then
    echo ""
    echo "ERROR: the SDK image build failed (exit code $BUILD_EXIT)."
    echo "Full build log: $LOG_PATH"
    # The failing Dockerfile stage tells apart tooling setup problems from SDK
    # compile problems. Docker prints it in the error block as the stage name
    # plus a step counter, e.g. "> [chip-build-cert 5/12]" means the 5th of 12
    # instructions in the chip-build-cert stage; only the stage name matters here.
    FAILED_STAGE=$(grep -oE '> \[[^]]+\]' "$LOG_PATH" | tail -1 | tr -d '>[]' | tr -s ' ' | sed 's/^ *//')
    NETWORK_FAILURE=false
    if grep -qiE "could not resolve host|unable to access|temporary failure in name resolution" "$LOG_PATH"; then
        NETWORK_FAILURE=true
        echo "The log shows a network failure: check the connection and retry."
    elif [[ "$FAILED_STAGE" == *"chip-build-cert-bins"* ]]; then
        echo "The failure happened while compiling the SDK binaries (at $FAILED_STAGE),"
        echo "not in the image's tooling setup: retrying with another Dockerfile is"
        echo "unlikely to help. Check the build log for the compile error."
    elif [[ "$DOCKERFILE_REF" == "$SDK_DOCKER_TAG" ]]; then
        echo "The failure happened while setting up the image's build tooling"
        echo "${FAILED_STAGE:+(at $FAILED_STAGE) }and the Dockerfile at the pinned tag"
        echo "fetches unpinned external tools that change over time."
        echo ""
        echo "Retrying with the current SDK Dockerfile may get past a tooling issue,"
        echo "but note its later stages may not match the pinned SDK commit:"
        echo "  $0 master"
    fi
    if ! $NETWORK_FAILURE; then
        # Manual patching must start from the pinned tag's Dockerfile: its later
        # stages are the ones that match the pinned SDK commit's build output.
        PINNED_DOCKERFILE_URL="https://raw.githubusercontent.com/project-chip/connectedhomeip/$SDK_DOCKER_TAG/integrations/docker/images/chip-cert-bins/Dockerfile"
        echo ""
        echo "To investigate and patch the pinned tag's Dockerfile manually:"
        echo "  curl -sfL $PINNED_DOCKERFILE_URL -o Dockerfile"
        echo "  # edit the failing step (see the build log), then rebuild:"
        echo "  sudo docker build --build-arg COMMITHASH=$SDK_DOCKER_TAG -t $SDK_DOCKER_IMAGE ."
        echo "  # once the image builds, continue with the setup:"
        echo "  ./scripts/wsl/update.sh"
    fi
    exit $BUILD_EXIT
fi

print_script_step "Success"
sudo docker images $SDK_DOCKER_IMAGE --format "Built {{.Repository}}:{{.Tag}} ({{.Size}})"
echo "Full build log: $LOG_PATH"

print_end_of_script
