#!/usr/bin/env sh

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

#Current directory
CURRENT_DIR=$(dirname $(realpath "$0"))
#Parent directory
PARENT_DIR=$(dirname ${CURRENT_DIR})

#environment file where the backend SHA will be saved into.
BACKEND_SHA_FILE="${PARENT_DIR}/backend/.sha_information"

#Delete any stale SHA information
if [ -f "$BACKEND_SHA_FILE" ]; then
	rm $BACKEND_SHA_FILE
fi

#Save the backend SHA
output=$(git -C ./backend rev-parse --short HEAD)

#copy the SHA into a file in the parent directory
echo "${output}" > $BACKEND_SHA_FILE
