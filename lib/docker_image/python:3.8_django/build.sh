#!/bin/bash
set -e
set -o errexit
set -o pipefail

CURRENT_DIR=$(dirname $(realpath $0))
WORKSPACE="$(dirname $(dirname $(dirname $(dirname $(realpath $0)))))"
. "${WORKSPACE}"/lib/log.sh
. "${WORKSPACE}"/lib/docker_tools.sh
. "${WORKSPACE}"/etc/global_config.sh
. "${WORKSPACE}"/lib/os.sh
. "${WORKSPACE}"/lib/check.sh

. "${WORKSPACE}"/lib/param.sh
analyze_params $*


DOCKER_IMAGE_NAME="${PRIVATE_HARBOR_PREFIX}yc913344706/python"
DOCKER_IMAGE_TAG="3.8_django"

mkdir -p ./tmp
if [ -f ${WORKSPACE}/etc/backend/requirements.txt ]; then
  cp -a ${WORKSPACE}/etc/backend/requirements.txt ./tmp/requirements.txt
fi

build_image() {
  docker build --build-arg BASE_IMAGE="${DOCKER_PROXY_DOCKER_IO}yc913344706/ubuntu:20.04_python3.8" -t "${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}" . || die "docker build failed"
}

build_image
push_image_with_manifest_for_arch "${DOCKER_IMAGE_NAME}" "${DOCKER_IMAGE_TAG}"
# push_image

rm -rf ./tmp/
