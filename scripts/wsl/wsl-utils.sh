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

# Shared helpers for the WSL install/update scripts in this folder.
# Sourced, not executed.

require_wsl()
{
    # The kernel version string covers stock WSL kernels; the WSLInterop hook
    # covers custom-compiled WSL kernels; the env var covers interop-disabled
    # setups.
    if ! grep -qi microsoft /proc/version 2>/dev/null &&
        [ ! -e /proc/sys/fs/binfmt_misc/WSLInterop ] &&
        [ -z "$WSL_DISTRO_NAME" ]; then
        echo "This script is intended for WSL2 only."
        echo "On Raspberry Pi or a regular Ubuntu machine use scripts/ubuntu/auto-install.sh."
        exit 1
    fi
    # The checks above also match WSL1, which cannot run docker or systemd.
    # Requiring a running systemd rejects WSL1 and catches WSL2 instances
    # without systemd enabled (a prerequisite, see README.md).
    if [ ! -d /run/systemd/system ]; then
        echo "systemd is not running. The Test Harness requires WSL2 with systemd"
        echo "enabled: add to /etc/wsl.conf:"
        echo "  [boot]"
        echo "  systemd=true"
        echo "then restart WSL (wsl --shutdown) and run this script again."
        exit 1
    fi
}

# Docker platform architecture of this host (amd64, arm64, ...).
host_docker_arch()
{
    case "$(uname -m)" in
        x86_64)  echo "amd64" ;;
        aarch64) echo "arm64" ;;
        armv7l)  echo "arm" ;;
        *)       uname -m ;;
    esac
}

# Architectures the registry publishes for an image, space separated. Empty
# when the manifest cannot be read (not published, or no network).
published_image_archs()
{
    sudo docker manifest inspect -v "$1" 2>/dev/null | python3 -c '
import json
import sys
try:
    manifests = json.load(sys.stdin)
except ValueError:
    sys.exit(0)
if not isinstance(manifests, list):
    manifests = [manifests]
archs = {m.get("Descriptor", {}).get("platform", {}).get("architecture") for m in manifests}
print(" ".join(sorted(a for a in archs if a and a != "unknown")))
'
}

# The scripts in this folder replay parts of the stock install/update flow.
# Each entry records the stock file a WSL script mirrors and its content hash
# (git hash-object, first 12 characters) when the WSL script was last synced
# against it. When a stock file changes, warn so the WSL variant gets reviewed
# (and this table updated).
WSL_SYNC_TABLE=(
    "scripts/ubuntu/auto-install.sh c5989a121ca1"
    "scripts/ubuntu/internal-auto-install.sh 8add9f9ca1bd"
    "scripts/ubuntu/auto-update.sh 2c42af0d2faa"
    "scripts/ubuntu/internal-auto-update.sh 5f8fcfa3f35b"
    "scripts/ubuntu/2-machine-configuration.sh 00ea2e312d22"
    "scripts/update.sh cab4e1395f10"
    "scripts/update-docker-images.sh 501a18094186"
)

check_wsl_scripts_sync()
{
    local root_dir=$1
    local entry stock_file synced_hash current_hash
    for entry in "${WSL_SYNC_TABLE[@]}"; do
        stock_file=${entry% *}
        synced_hash=${entry#* }
        current_hash=$(git -C "$root_dir" hash-object "$stock_file" 2>/dev/null | cut -c1-12)
        if [ -n "$current_hash" ] && [ "$current_hash" != "$synced_hash" ]; then
            echo "WARNING: $stock_file changed since the WSL scripts were last synced against it."
            echo "         Review its history, apply what applies to the WSL variant, then"
            echo "         update WSL_SYNC_TABLE in scripts/wsl/wsl-utils.sh."
        fi
    done
}
