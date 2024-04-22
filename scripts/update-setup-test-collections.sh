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

echo "*** Update CLI dependencies"
source ~/.profile #ensure poetry is in path
cd $ROOT_DIR/cli && poetry install

echo "*** Setup Test Collections"
cd $ROOT_DIR

try_to_execute_setup_script()
{
    program_folder=$1

    if [ -d $program_folder ]; then 
        setup_script=$program_folder/setup.sh
        # Only run setup.sh if present and it's executable
        if [ -x $setup_script ]; then 
            echo "Running setup script: $setup_script"
            $setup_script
            if [ $? -ne 0 ]; then
                echo "### Exit with Error ###"
                return 1
            fi
            echo "Setup script finished with success"
        fi
    fi
}

MATTER_PROGRAM_FOLDER="./backend/test_collections/matter"
try_to_execute_setup_script $MATTER_PROGRAM_FOLDER

TEST_COLLECTIONS_FOLDER="./test_collections/*"
for program_folder in $TEST_COLLECTIONS_FOLDER
do
    try_to_execute_setup_script $program_folder  
done

# We echo "complete" to ensure this scripts last command has exit code 0.
echo "./scripts/update-setup-test-collections.sh Complete"
