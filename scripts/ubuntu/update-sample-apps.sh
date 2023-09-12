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
ROOT_DIR=$(realpath $(dirname "$0")/../..)

printf "\n\n**********"
printf "\n*** Update Matter Sample Apps ***\n"
# We are fetching SDK docker image and tag name from backend
# This is done to minimize the places the SDK version is tracked.
cd $ROOT_DIR
SDK_DOCKER_IMAGE=$(cat $ROOT_DIR/backend/app/core/config.py | grep SDK_DOCKER_IMAGE | cut -d'"' -f 2 | cut -d"'" -f 2)
SDK_DOCKER_TAG=$(cat $ROOT_DIR/backend/app/core/config.py | grep SDK_DOCKER_TAG | cut -d'"' -f 2 | cut -d"'" -f 2)
sudo docker pull $SDK_DOCKER_IMAGE:$SDK_DOCKER_TAG
sudo docker run -t -v ~/apps:/apps $SDK_DOCKER_IMAGE:$SDK_DOCKER_TAG bash -c "rm -v /apps/*; cp -v * /apps/;"
sudo chown -R `whoami` ~/apps
