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
# set -x

TAG_DESCRIPTION=""
REMOTE="origin"
MATTER_PROGRAM_DIR=$(realpath $(dirname "$0")/../backend/test_collections/matter)

# Get configured SDK_SHA (will default to value in ./backend/test_collection/matter/config.py)
SDK_SHA=$(cat $MATTER_PROGRAM_DIR/config.py | grep SDK_SHA | cut -d'"' -f 2 | cut -d"'" -f 2)

if [ -z "$SDK_SHA"]
then
    echo "### Error: Matter SDK information not found. Please verify the Matter program 'config.py' file"
    exit 1
fi

# Check if a TAG name was provided.
if [ $# -eq 2 ]
then
    TAG_NAME="$1"
    TAG_DESCRIPTION="$2"
elif [ $# -eq 3 ]
then 
    TAG_NAME="$1"
    TAG_DESCRIPTION="$2"
    REMOTE="$3"
else
    echo "Usage: ./scripts/create-release-tag.sh tag_name tag_description custom_remote"
    echo "  tag_name        [Required] The git TAG name"
    echo "  tag_description [Required] The git TAG description"
    echo "  custom_remote   [Optional] you can set a custom remote (default is $REMOTE)"
    echo "Example: ./scripts/create-release-tag.sh v2.10+fall2024 \"Release for Fall 2024\""
    exit 1
fi

echo "*** Deleting old local tag"
git tag -d $TAG_NAME

echo "*** Creating a local release tag"
GIT_SUBMODULES=$(git submodule)
TAG_SHA_DESCRIPTION=$(printf "$GIT_SUBMODULES\n $SDK_SHA Matter SDK")
git tag -a $TAG_NAME -m "$TAG_NAME" -m "$TAG_DESCRIPTION" -m "$TAG_SHA_DESCRIPTION"

echo "*** Release tag"
git tag -v $TAG_NAME

printf "\n\n**********\n"
printf "Do you want to push the tag to remote[$REMOTE]?\n"
select yn in "Push" "Do not Push"
do
    case $yn in
        Push )
            echo "*** Pushing tag on remote"
            git push $REMOTE $TAG_NAME
            break
            ;;
        *) 
            exit
            ;;
    esac
done
