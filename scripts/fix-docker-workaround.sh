#! /usr/bin/env bash

#
# Copyright (c) 2025 Project CHIP Authors
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

# This is a standalone workaround script to fix Docker 29.x compatibility issues
# It stops the services, fixes Docker, and restarts the services.

set -e

ROOT_DIR=$(realpath $(dirname "$0")/..)
SCRIPT_DIR="$ROOT_DIR/scripts"

echo "==================================="
echo "Docker 29.x Compatibility Fix"
echo "==================================="
echo ""
echo "This script will:"
echo "1. Stop certification tool services"
echo "2. Fix Docker compatibility by downgrading from 29.x to 28.x"
echo "3. Build backend and frontend Docker images"
echo "4. Restart certification tool services"
echo ""
echo "WARNING: This will temporarily stop all running services."
echo ""

# Ask for confirmation
read -p "Do you want to continue? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operation cancelled."
    exit 0
fi

echo ""
echo "Step 1/4: Stopping certification tool services..."
echo "=============================================="
if [ -f "$SCRIPT_DIR/stop.sh" ]; then
    $SCRIPT_DIR/stop.sh
    echo "Services stopped successfully."
else
    echo "Warning: stop.sh not found, continuing with Docker fix..."
fi

echo ""
echo "Step 2/4: Fixing Docker compatibility..."
echo "======================================="
if [ -f "$SCRIPT_DIR/fix-docker-compatibility.sh" ]; then
    $SCRIPT_DIR/fix-docker-compatibility.sh
    echo "Docker compatibility fix completed."
else
    echo "Error: fix-docker-compatibility.sh not found!"
    echo "Please ensure the script exists and try again."
    exit 1
fi

echo ""
echo "Step 3/4: Building backend and frontend Docker images..."
echo "=================================================="

echo "Building backend image..."
if [ -f "$ROOT_DIR/backend/scripts/build-docker-image.sh" ]; then
    cd "$ROOT_DIR"
    ./backend/scripts/build-docker-image.sh
    echo "Backend image built successfully."
else
    echo "Warning: $ROOT_DIR/backend/scripts/build-docker-image.sh not found."
fi

echo "Building frontend image..."
if [ -f "$ROOT_DIR/frontend/scripts/build-docker-image.sh" ]; then
    cd "$ROOT_DIR"
    ./frontend/scripts/build-docker-image.sh
    echo "Frontend image built successfully."
else
    echo "Warning: $ROOT_DIR/frontend/scripts/build-docker-image.sh not found."
fi

echo "Pulling chip-cert-bins Docker image..."
if [ -f "$ROOT_DIR/backend/test_collections/matter/scripts/update-sample-apps.sh" ]; then
    cd "$ROOT_DIR"
    ./backend/test_collections/matter/scripts/update-sample-apps.sh
    echo "Chip-cert-bins image updated successfully."
else
    echo "Warning: $ROOT_DIR/backend/test_collections/matter/scripts/update-sample-apps.sh not found."
fi

echo ""
echo "Step 4/4: Starting certification tool services..."
echo "=============================================="
if [ -f "$SCRIPT_DIR/start.sh" ]; then
    $SCRIPT_DIR/start.sh
    echo "Services started successfully."
else
    echo "Warning: start.sh not found. Please start services manually."
    exit 1
fi

echo ""
echo "==================================="
echo "Docker compatibility fix completed!"
echo "==================================="
echo ""
echo "Your certification tool should now be running with a compatible Docker version."
echo "You can verify the fix by checking that there are no more API version errors in:"
echo "  docker logs certification-tool-proxy-1"
echo ""
