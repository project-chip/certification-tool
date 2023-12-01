#!/bin/bash

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
cd $ROOT_DIR

get_repo_and_branch_info() {
    # Input validation
    if [ -z "$1" ]; then
        echo "Please provide a path."
        return 1
    fi

    path="$1"
    repo_friendly_name="Test Harness"

    if [ "$path" != "." ]; then
        title_case_path=$(echo "$path" | awk '{ for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2)); }1')
        repo_friendly_name=$title_case_path
    fi

    # Check if the directory exists
    if [ ! -d "$path" ]; then
        echo "Directory '$path' does not exist."
        return 1
    fi

    cd $path

    # Get the URL of the remote origin
    remote_url=$(git config --get remote.origin.url)

    # Check if remote URL is non-empty
    if [ -n "$remote_url" ]; then
        # Extract the repository name from the URL
        repo_name=$(basename -s .git "$remote_url")
        echo "$repo_friendly_name: $repo_name"
    else
        # Print error message if there is no remote URL
        echo "Not a Git repository or no remote set"
        return 1
    fi

    # Get the commit SHA of the current HEAD
    commit_sha=$(git rev-parse HEAD)
    echo "Commit SHA: $commit_sha"

    # Get the commit message of the current HEAD
    commit_message=$(git log -1 --pretty=format:"%B")
    echo "Commit Message: $commit_message"

    # Get the commit author of the current HEAD
    commit_author=$(git log -1 --pretty=format:"%an")
    echo "Commit Author: $commit_author"

    # Get the commit date and time of the current HEAD including timezone
    commit_datetime=$(git log -1 --pretty=format:"%cd" --date=format:"%Y-%m-%d %H:%M:%S %z")
    echo "Commit Date: $commit_datetime"

    # Attempt to find branches that contain this commit
    branches=$(git branch --contains $commit_sha)

    if [ -n "$branches" ]; then
        echo "Contained in branches:"
        echo "$branches"
    else
        echo "This commit is not on any known branch."
    fi

    echo

    # Navigate back to the original directory
    cd $ROOT_DIR
}












get_repo_and_branch_info "."
get_repo_and_branch_info "frontend"
get_repo_and_branch_info "backend"
get_repo_and_branch_info "cli"
