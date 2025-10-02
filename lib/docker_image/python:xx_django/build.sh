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

##########################

# python版本
# PYTHON_VERSION="3.10"
PYTHON_VERSION="3.13"

# 制作依赖的基础镜像
BUILD_BASE_IMAGE="${DOCKER_PROXY_DOCKER_IO}yc913344706/ubuntu:22.04_python${PYTHON_VERSION}"  

# 制作成的目标镜像--NAME
DOCKER_IMAGE_NAME="${PRIVATE_HARBOR_PREFIX}yc913344706/python"

# 制作成的目标镜像--TAG
DOCKER_IMAGE_TAG="${PYTHON_VERSION}_django" 

##########################

mkdir -p ./tmp
if [ -f ${WORKSPACE}/code/backend/requirements.txt ]; then
  cp -a ${WORKSPACE}/code/backend/requirements.txt ./tmp/requirements.txt
fi

build_image() {
  docker build \
    --build-arg BASE_IMAGE="${BUILD_BASE_IMAGE}" \
    -t "${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}" . || die "docker build failed"
}

build_image
push_image_with_manifest_for_arch "${DOCKER_IMAGE_NAME}" "${DOCKER_IMAGE_TAG}"
# push_image

rm -rf ./tmp/
