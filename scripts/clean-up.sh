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

ROOT_DIR=$(realpath $(dirname "$0")/..)
SCRIPT_DIR="$ROOT_DIR/scripts"

# Add utility operations to this script
source "$SCRIPT_DIR/utils.sh"

# Exit in case of error
set -e

clean_up_environment() {
	rm -rf $HOME/apps
	rm -rf $HOME/.cache/pypoetry

	print_script_step "Resetting Database"
	if [ ! $(docker ps -aq -f name=^certification-tool-backend-1$) ]; then
		docker compose -f $ROOT_DIR/docker-compose.yml -f $ROOT_DIR/docker-compose.override-backend-dev.yml up db backend --detach --no-build
	fi
	docker exec certification-tool-backend-1 bash -c "./prestart.sh ; poetry install ; ./scripts/reset_db.py"

	print_script_step "Stopping all docker containers"
	$ROOT_DIR/scripts/stop.sh

	print_script_step "Cleaning All Images"
	docker network prune -f
	docker system prune -af --volumes
}

print_start_of_script

echo
echo "This operation will erase all the data from the database and prune the docker images and networks"
read -p "Are you sure you want to clean up the Test-Harness environment? [y/N] " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
	clean_up_environment
else
	echo
	echo "Cancelling..."
fi

print_end_of_script
