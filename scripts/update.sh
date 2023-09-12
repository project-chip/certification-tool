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

# If the repo is not pointing to a branch, the branch name will appear as "HEAD"
# In that case, we ask the user if we may use the "develop" branch instead
# If refused, the whole opperation is aborted
if [ "$ROOT_BRANCH" = "HEAD" ]; then
    echo "The HEAD is detached from a branch. Should it checkout to develop before proceeding?"
    select yn in "Yes" "No"; do
        case $yn in
            Yes ) ROOT_BRANCH=develop; break;;
            No ) echo "Aborting..."; exit;;
        esac
    done
fi

echo "*** Stashing local changes"
cd $ROOT_DIR && git stash && git submodule foreach 'git stash'

echo "*** Pull latest Test Harness code"
cd $ROOT_DIR && \
    git checkout $ROOT_BRANCH && \
    git pull && \
    git submodule update --init --recursive

echo "*** Update CLI dependencies"
source ~/.profile #ensure poetry is in path
cd $ROOT_DIR/cli && poetry install
