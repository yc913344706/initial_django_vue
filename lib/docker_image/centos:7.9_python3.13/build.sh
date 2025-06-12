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

get_os_arch
cp -a ${CURRENT_DIR}/root/etc/yum.repos.d/centos.repo.${OS_ARCH} ${CURRENT_DIR}/root/etc/yum.repos.d/centos.repo

DOCKER_IMAGE_NAME="${PRIVATE_HARBOR_PREFIX}yc913344706/centos"
DOCKER_IMAGE_TAG="7.9_python3.13"

build_image() {
  docker build --build-arg BASE_IMAGE="${DOCKER_PROXY_DOCKER_IO}centos:7.9" -t "${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}" . || die "docker build failed"
}

build_image
push_image_with_manifest_for_arch "${DOCKER_IMAGE_NAME}" "${DOCKER_IMAGE_TAG}"
# push_image "${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
