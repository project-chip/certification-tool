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

source "$SCRIPT_DIR/utils.sh"

print_start_of_script

print_script_step "Setup CLI dependencies"
$SCRIPT_DIR/update-setup-cli-dependencies.sh
verify_return_code

print_script_step "Setup Test Collections"
cd $ROOT_DIR

try_to_execute_setup_script()
{
    program_folder=$1

    if [ -d $program_folder ]; then 
        setup_script=$program_folder/setup.sh
        # Only run setup.sh if present and it's executable
        if [ -x $setup_script ]; then 
            print_script_step "Running setup script: $setup_script"
            $setup_script
            if [ $? -ne 0 ]; then
                return 1
            fi
            printf "Setup script finished with success\n"
        fi
    fi
}

MATTER_PROGRAM_FOLDER="./backend/test_collections/matter"
try_to_execute_setup_script $MATTER_PROGRAM_FOLDER
if [ $? -ne 0 ]; then
    printf "################################################################################\n"
    printf "The Matter program setup script failed.\n"
    printf "Retry the installation and if the problem persists, contact the Matter program developers.\n"
    printf "################################################################################\n"
    exit 1
fi

TEST_COLLECTIONS_FOLDER="./test_collections/*"
for program_folder in $TEST_COLLECTIONS_FOLDER
do
    try_to_execute_setup_script $program_folder  
    if [ $? -ne 0 ]; then
        printf "################################################################################\n"
        printf "The program's setup script failed.\n"
        printf "Please repeat the installation and if the problem persists, contact the program developers.\n"
        printf "################################################################################\n"
        exit 1
    fi
done

print_end_of_script
