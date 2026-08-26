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
        printf "###################################################################################\n"
        printf "#                                                                                 #\n"
        printf "#  Please format the SDCard and perform a fresh installation or                   #\n"
        printf "#  update you OS and then run the auto-install script again.                      #\n"
        printf "#                                                                                 #\n"
        printf "###################################################################################\n"
        return 1
    fi
}

check_user_name()
{
    USER_NAME=$(whoami)
    if [ "$USER_NAME" != "ubuntu" ]; then
        printf "\n\n"
        printf "###################################################################################\n"
        printf "######  The Matter certification tool requires the username to be 'ubuntu'  #######\n"
        printf "###################################################################################\n"
        printf "#                                                                                 #\n"
        printf "# After creating the 'ubuntu' user, log in and run the auto-install script again. #\n"
        printf "#                                                                                 #\n"
        printf "###################################################################################\n"
        return 1
    fi
}

check_installation_prerequisites()
{
    print_script_step "Verify Matter Test Harness Prerequisites"

    check_ubuntu_os_version
    INVALID_VERSION=$?
    check_user_name
    INVALID_USER=$?

    if [ $INVALID_VERSION == 1 ] || [ $INVALID_USER == 1 ]; then
        exit 1
    fi
}

# Silence needrestart prompts (reboot hints, service restarts) during the
# install, and restore the defaults when done. needrestart comes preinstalled
# on Ubuntu Server images but not on minimal ones such as the WSL image, so
# both functions are no-ops when the config file is absent.
silence_needrestart()
{
    if [ -f /etc/needrestart/needrestart.conf ]; then
        sudo sed -i "s/#\$nrconf{kernelhints} = -1;/\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
        sudo sed -i "s/#\$nrconf{restart} = 'i';/\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf
    fi
}

restore_needrestart()
{
    if [ -f /etc/needrestart/needrestart.conf ]; then
        sudo sed -i "s/\$nrconf{kernelhints} = -1;/#\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
        sudo sed -i "s/\$nrconf{restart} = 'a';/#\$nrconf{restart} = 'i';/" /etc/needrestart/needrestart.conf
    fi
}

is_running_in_wsl()
{
    # Layered detection: the kernel version string covers stock WSL kernels in
    # any context (login shells, systemd services); the WSLInterop hook covers
    # custom-compiled WSL kernels; the env var covers interop-disabled setups
    # (user sessions only, WSL does not set it for systemd services).
    grep -qi microsoft /proc/version 2>/dev/null || \
        [ -e /proc/sys/fs/binfmt_misc/WSLInterop ] || \
        [ -n "$WSL_DISTRO_NAME" ]
}
