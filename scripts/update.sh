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

# Store the current branch for the update
ROOT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Exit in case anything goes wrong
set -e

# Check if a branch name was not provided.
if [ $# -eq 1 ]; then
    ROOT_BRANCH="$1"
fi

echo "*** Stashing local changes"
cd $ROOT_DIR && git stash && git submodule foreach 'git stash'

echo "*** Pull Test Harness code"
cd $ROOT_DIR && \
    git checkout $ROOT_BRANCH && \
    git pull && \
    git submodule update --init --recursive

echo "*** Download Docker images"
cd $ROOT_DIR
# Ensure .env exists
./scripts/install-default-env.sh

# Download docker images from docker-compose.yml.
# As this might be run during setup we use `newgrp` command to ensure 
# docker works.
newgrp docker << END
# You can do more lines than just this./
docker compose pull
END

echo "*** Update CLI dependencies"
source ~/.profile #ensure poetry is in path
cd $ROOT_DIR/cli && poetry install

echo "*** Setup Test Collections"
cd $ROOT_DIR
for dir in ./test_collections/*
do
    setup=$dir/setup.sh
    # Only run setup.sh if present/
    if [ -x $setup ]; then
        echo "Running "$setup"..."
        $setup
    fi
done

# We echo "complete" to ensure this scripts last command has exit code 0.
echo "Test Collection Setup Complete"
