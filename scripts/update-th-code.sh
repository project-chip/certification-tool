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

cd $ROOT_DIR

echo "*** Stashing local changes"
git stash
git submodule foreach 'git stash'

echo "*** Pulling Test Harness code"
git fetch
git checkout $ROOT_BRANCH
git pull
git submodule update --init --recursive

# We echo "complete" to ensure this scripts last command has exit code 0.
echo "./scripts/update-th-code.sh Complete"
