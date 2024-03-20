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
REMOTE="origin"

if [ $# = 0 ]
then
  echo "No custom remote defined. Using 'origin' as default."
elif [ $# = 2 ] && [ $1 = "--remote" ]
then
  REMOTE=$2
  echo "Using '$REMOTE' as remote."
else
  echo "This script will update the '$TAG_NAME' tag references and push to remote."
  echo "To perform the update go to the desired commit/branch and then:"
  echo "Usage: ./scripts/update-git-latest-tag.sh --remote custom_remote"
  echo "  --remote [Optional] you can set a custom remote (default is origin)"
  exit 1
fi

echo "Updating remote '$TAG_NAME' tag references and push it to remote."

echo "*** Deleting old local tag"
git tag --delete $TAG_NAME

echo "*** Deleting old remote tag"
git push $REMOTE :refs/tags/$TAG_NAME

echo "*** Creating a local tag"
git tag --annotate $TAG_NAME -m "$TAG_COMMENT"

echo "*** Pushing tag on remote"
git push $REMOTE $TAG_NAME
