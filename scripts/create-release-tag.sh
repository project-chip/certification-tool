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

GIT_SUBMODULES=$(git submodule)

echo "*** Deleting old local tag"
git tag -d $TAG_NAME

echo "*** Creating a local release tag"
git tag -a $TAG_NAME -m "$TAG_NAME" -m "$TAG_DESCRIPTION" -m "$GIT_SUBMODULES"

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
