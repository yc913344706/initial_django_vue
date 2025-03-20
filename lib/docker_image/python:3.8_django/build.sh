#!/bin/bash
set -e

WORKSPACE="$(dirname $(dirname $(dirname $(dirname $(realpath $0)))))"
. "${WORKSPACE}"/lib/log.sh
. "${WORKSPACE}"/lib/docker_tools.sh
. "${WORKSPACE}"/etc/docker_config.sh

. "${WORKSPACE}"/lib/param.sh
analyze_params $*


mkdir -p ./tmp
if [ -f ${WORKSPACE}/etc/requirements.txt ]; then
  cp -a ${WORKSPACE}/etc/requirements.txt ./tmp/requirements.txt
fi

DOCKER_IMAGE_NAME="${HARBOR_PREFIX}python:3.8_django"
build_image() {
  docker images | grep "${HARBOR_PREFIX}ubuntu:20.04_python3.8" || die "docker image ${HARBOR_PREFIX}ubuntu:20.04_python3.8 not found"

  docker build --build-arg BASE_IMAGE="${HARBOR_PREFIX}ubuntu:20.04_python3.8" -t "${DOCKER_IMAGE_NAME}" . || die "docker build failed"
}

build_image

rm -rf ./tmp/

push_image
