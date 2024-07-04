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

# Retrieve the hostname
host=$(hostname -I | awk '{print $1}')

# Define the endpoint with dynamic host
endpoint="http://$host/api/v1/projects/default_config"

# Make the GET request and store the response along with headers
response=$(curl -si "$endpoint")

# Check if the curl command was successful
if [ $? -eq 0 ]; then
    # Extract the HTTP status code from the response
    status_code=$(echo "$response" | grep -oP '(?<=HTTP/1.1 )\d+')
    
    # Check if the status code indicates an error (i.e., not 2xx)
    if [[ $status_code -lt 200 || $status_code -ge 300 ]]; then
        echo "Received an error response. Status Code: $status_code"
        # Handle the error (e.g., retry, log the error, notify an admin, etc.)
        exit 1
    else
        # Extract the body from the response (exclude headers)
        body=$(echo "$response" | sed -n '/^\r$/,$p' | sed '1d')
        # Check if the body starts with a valid JSON character
        if [[ "$body" =~ ^\{ || "$body" =~ ^\[ ]]; then
            # Output the body (pretty-printed with Python)
            if command -v python &>/dev/null
            then
                echo "$body" | python -m json.tool
            elif command -v python3 &>/dev/null
            then
                echo "$body" | python3 -m json.tool
            else
                echo "Python is not installed. Cannot pretty-print JSON."
            fi
        else
            echo "The endpoint did not return valid JSON data."
            echo "Response body: $body"
        fi
    fi
else
    # Output an error message if the curl command fails
    echo "Failed to retrieve data from endpoint."
fi
