#!/bin/bash

set -e

WORKSPACE="$(dirname $(dirname $(realpath $0)))"

. "${WORKSPACE}"/lib/log.sh
. "${WORKSPACE}"/lib/docker_tools.sh
. "${WORKSPACE}"/etc/docker_config.sh

mkdir -p ${WORKSPACE}/code/

IMAGE_NAME="${HARBOR_PREFIX}python"
IMAGE_TAG="3.8_django"
check_docker_image_exist "${IMAGE_NAME}" "${IMAGE_TAG}"

docker run -it \
    --rm -v ${WORKSPACE}/code:/data/code \
    ${IMAGE_NAME}:${IMAGE_TAG} \
    bash -c "cd /data/code && django-admin startproject backend && python manage.py startapp demo"




