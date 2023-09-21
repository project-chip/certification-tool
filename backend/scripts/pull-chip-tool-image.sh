#!/bin/bash -e
set -x
set -e

DOCKER_TAG=`python -c "from app.core.config import settings; print(f'{settings.SDK_DOCKER_IMAGE}:{settings.SDK_DOCKER_TAG}')"`
docker pull $DOCKER_TAG