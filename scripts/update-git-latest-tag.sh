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
TAG_NAME="latest"
TAG_COMMENT="Test Harness latest release version."

if [ $# != 0 ] || [ $1 = "--help" ]; then
  echo "This script will update the '$TAG_NAME' tag references."
  echo "To perform the update, follow these steps:"
  echo "1 - Go to the desired commit/branch."
  echo "2 - Run the script: ./scripts/update-git-latest-tag.sh"
  exit 1
fi

echo "*** Old tag reference"
git rev-list --oneline -1 $TAG_NAME

echo "*** Pulling remote tag references"
git fetch --tags --force

echo "*** Deleting old local tag"
git tag --delete $TAG_NAME

echo "*** Deleting old remote tag"
git push origin :refs/tags/$TAG_NAME

echo "*** Creating a new tag"
git tag --annotate $TAG_NAME -m "$TAG_COMMENT"

echo "*** New tag reference"
git rev-list --oneline -1 $TAG_NAME

echo "*** Pushing tag on remote"
git push origin $TAG_NAME
