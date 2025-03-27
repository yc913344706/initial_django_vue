#!/bin/bash

set -e

WORKSPACE="$(dirname $(dirname $(realpath $0)))"

. "${WORKSPACE}"/lib/log.sh
. "${WORKSPACE}"/lib/docker_tools.sh
. "${WORKSPACE}"/etc/global_config.sh

mkdir -p ${WORKSPACE}/code/

IMAGE_NAME="${PRIVATE_HARBOR_PREFIX}yc913344706/python"
IMAGE_TAG="3.8_django"
check_docker_image_exist "${IMAGE_NAME}" "${IMAGE_TAG}"

docker run -it \
    --name generate_backend_project \
    --rm -v ${WORKSPACE}/code:/data/code \
    ${IMAGE_NAME}:${IMAGE_TAG} \
    bash -c "cd /data/code && \
    rm -rf backend && \
    django-admin startproject backend && \
    cd backend && \
    python3 manage.py startapp demo"




