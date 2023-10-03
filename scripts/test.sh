#! /usr/bin/env sh

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

# Exit in case of error
set -e

# Ensure .env exists
./scripts/install-default-env.sh

DOMAIN=backend \
TRAEFIK_PUBLIC_NETWORK_IS_EXTERNAL=false \
INSTALL_DEV=true \
docker-compose \
-f docker-compose.yml \
config > docker-stack.yml

docker-compose -p "chip-cert-tool-test" -f docker-stack.yml build
docker-compose -p "chip-cert-tool-test" -f docker-stack.yml down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error
docker-compose -p "chip-cert-tool-test" -f docker-stack.yml up -d
docker-compose -p "chip-cert-tool-test" -f docker-stack.yml exec -T backend bash /app/tests-start.sh "$@"
docker-compose -p "chip-cert-tool-test" -f docker-stack.yml down -v --remove-orphans
