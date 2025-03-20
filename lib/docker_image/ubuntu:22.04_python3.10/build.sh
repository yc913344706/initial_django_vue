#!/bin/bash
set -e

WORKSPACE="$(dirname $(dirname $(dirname $(dirname $(realpath $0)))))"
. "${WORKSPACE}"/lib/log.sh
. "${WORKSPACE}"/lib/docker_tools.sh
. "${WORKSPACE}"/etc/docker_config.sh

DOCKER_IMAGE_NAME="${HARBOR_PREFIX}ubuntu:22.04_python3.10"
build_image() {
  docker build --build-arg BASE_IMAGE="${DOCKER_PROXY}library/ubuntu:22.04" -t "${DOCKER_IMAGE_NAME}" . || die "docker build failed"
}

build_image
push_image
