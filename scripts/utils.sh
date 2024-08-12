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

print_script_step()
{
    info=$1
    #Retreive the script name
    script_name=`basename "$(realpath $0)"`

    printf "\n\n********************************************************************************\n"
    printf "$script_name: $info\n"
    printf "********************************************************************************\n"
}

print_start_of_script()
{
    #Retreive the script name
    script_name=`basename "$(realpath $0)"`
    printf "\n\n################################################################################\n"
    printf "$script_name: Starting...\n"
    printf "################################################################################\n"
}

print_end_of_script()
{
    #Retreive the script name
    script_name=`basename "$(realpath $0)"`
    printf "\n\n################################################################################\n"
    printf "$script_name: Finishing...\n"
    printf "################################################################################\n"
}

verify_return_code()
{
    if [ $? -ne 0 ]; then
        printf "\n\n"
        printf "################################################################################\n"
        printf "############################### Exit with Error ################################\n"
        printf "################################################################################\n\n"
        printf "Please try the installation again and if the problem persists, \n"
        printf "please collect as much information as possible and file an issue here: \n"
        printf "https://github.com/project-chip/certification-tool/issues \n\n\n"
        exit 1
    fi
}

print_installation_success()
{
    printf "\n\n"
    printf "################################################################################\n"
    printf "The installation was completed successfully.\n"
    printf "################################################################################\n\n"
}

check_ubuntu_os_version()
{
    UBUNTU_VERSION_NUMBER=$(lsb_release -sr)
    if [ "$UBUNTU_VERSION_NUMBER" != "24.04" ]; then
        printf "\n\n"
        printf "###################################################################################\n"
        printf "######  Matter Certification-Tool requires Ubuntu Server 24.04 LTS (64-bit)  ######\n"
        printf "###################################################################################\n\n"
        printf "Please format the SDCard and perform a fresh installation or\n"
        printf "update you OS and then run the auto-install script again.\n"
        return 1
    fi

    return 0
}

check_user_name()
{
    USER_NAME=$(whoami)
    printf "$USER_NAME"
    if [ "$USER_NAME" != "ubuntu" ]; then
        printf "\n\n"
        printf "###################################################################################\n"
        printf "######  The Matter certification tool requires the username to be 'ubuntu'  #######\n"
        printf "###################################################################################\n\n"
        printf "After creating the 'ubuntu' user, log in and run the auto-install script again.\n"
        return 1
    fi
}

check_installation_prerequisites()
{
    print_script_step "Verify Matter Test Harness Prerequisites"

    check_ubuntu_os_version
    INVALID_VERSION=$?
    INVALID_USER=$(check_user_name)
    if [ $INVALID_VERSION == 1 ] || [ $INVALID_USER == 1 ]; then
        printf "FALHOU"
        exit 1
    fi
    exit 2
}

check_installation_prerequisites              
