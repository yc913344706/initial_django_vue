#!/bin/bash
set -e
set -o errexit
set -o pipefail

CURRENT_DIR=$(dirname $(realpath $0))
WORKSPACE="$(dirname $(dirname $(dirname $(dirname $(realpath $0)))))"
. "${WORKSPACE}"/lib/log.sh
. "${WORKSPACE}"/lib/docker_tools.sh
. "${WORKSPACE}"/etc/docker_config.sh
. "${WORKSPACE}"/lib/os.sh
. "${WORKSPACE}"/lib/check.sh

. "${WORKSPACE}"/lib/param.sh
analyze_params $*

get_os_arch
cp -a ${CURRENT_DIR}/root/etc/apt/sources.list.${OS_ARCH} ${CURRENT_DIR}/root/etc/apt/sources.list

DOCKER_IMAGE_NAME="${HARBOR_PREFIX}python"
DOCKER_IMAGE_TAG="3.10_django"

mkdir -p ./tmp
if [ -f ${WORKSPACE}/etc/requirements.txt ]; then
  cp -a ${WORKSPACE}/etc/requirements.txt ./tmp/requirements.txt
fi

build_image() {
  docker build --build-arg BASE_IMAGE="${DOCKER_PROXY}yc913344706/ubuntu:22.04_python3.10" -t "${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}" . || die "docker build failed"
}

build_image
push_image_with_manifest_for_arch "${DOCKER_IMAGE_NAME}" "${DOCKER_IMAGE_TAG}"
# push_image

rm -rf ./tmp/
