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
UBUNTU_SCRIPT_DIR="$ROOT_DIR/scripts/ubuntu"
LOG_DIR="$ROOT_DIR/logs"

LOG_FILENAME=$(date +"log_ubuntu_auto_install_%F-%H-%M-%S")
LOG_PATH="$LOG_DIR/$LOG_FILENAME"
$UBUNTU_SCRIPT_DIR/internal-auto-install.sh $* | tee $LOG_PATH
