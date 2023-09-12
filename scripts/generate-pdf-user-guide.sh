#!/usr/bin/env bash

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
# This is an Asciidoc to PDF file format bash script
#
# The solution uses the Docker Asciidoctor to convert the Test-Harness User Guide Asciidoc file
#
# Unfortunatly, the Asciidoctor project does not provide multi-arch docker images
# Thus, this script only works for x86_64 CPU architecture machines
#
# For more information on the docker asciidoctor, please refer to:
# https://github.com/asciidoctor/docker-asciidoctor
#

# Project's root directory
ROOT_DIR=$(realpath $(dirname "$0")/..)
USER_GUIDE_PATH="$ROOT_DIR/docs/Matter_TH_User_Guide/"

# Docker related variables
DOCKER_IMAGE=asciidoctor/docker-asciidoctor             # Official Docker image with Asciidoctor
ALT_DOCKER_IMAGE=kidip/chip-documentation               # Alternative Docker Image with Asciidoctor
DOCKER_ARGS="run --rm -v $USER_GUIDE_PATH:/documents/"  # Docker arguments with run and volumes bind

# Call the Docker Asciidoctor PDF application
docker $DOCKER_ARGS $DOCKER_IMAGE asciidoctor-pdf Matter_TH_User_Guide.adoc
