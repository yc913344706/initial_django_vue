#!/bin/bash
set -e

WORKSPACE="$(dirname $(dirname $(dirname $(dirname $(realpath $0)))))"
. "${WORKSPACE}"/lib/log.sh
. "${WORKSPACE}"/lib/docker_tools.sh
. "${WORKSPACE}"/etc/docker_config.sh

mkdir -p ./tmp
cp -a ${WORKSPACE}/etc/requirements.txt ./tmp/requirements.txt

DOCKER_IMAGE_NAME="${HARBOR_PREFIX}python:3.8_django"
build_image() {
  docker build --build-arg BASE_IMAGE="${DOCKER_PROXY}ubuntu:20.04_python3.8" -t "${DOCKER_IMAGE_NAME}" . || die "docker build failed"
}

build_image

rm -rf ./tmp/

push_image
