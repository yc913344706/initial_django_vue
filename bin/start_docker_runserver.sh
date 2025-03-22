#!/bin/bash

set -e
set -o errexit
set -o pipefail

WORKSPACE="$(dirname $(dirname $(realpath $0)))"

. "${WORKSPACE}"/lib/log.sh
. "${WORKSPACE}"/lib/check.sh
. "${WORKSPACE}"/lib/param.sh
. "${WORKSPACE}"/lib/docker_tools.sh

pre_check() {
  check_var_exists "ENV"

  # 检查环境变量文件
  check_file_exists "${WORKSPACE}/etc/docker_env_files/${ENV}.env"
  . "${WORKSPACE}"/etc/docker_env_files/${ENV}.env

  # 检查项目目录
  check_dir_exists "${WORKSPACE}/code/${DJANGO_PROJECT_NAME}"

  # 检查必要的命令
  check_command_exists "docker"
}

main() {
  # 参数解析
  analyze_params $*


  pre_check

  DOCKER_CONTAINER_NAME="${DJANGO_PROJECT_NAME}_DJANGO_RUNSERVER"
  stop_old_docker_container "${DOCKER_CONTAINER_NAME}"

  log_info "start docker runserver..."
  docker run -itd --rm \
    -p ${DJANGO_SERVER_PORT_IN_HOST}:8000 \
    --name ${DOCKER_CONTAINER_NAME} \
    -v ${WORKSPACE}/etc/hosts:/etc/hosts \
    -v ${WORKSPACE}/etc/resolv.conf:/etc/resolv.conf \
    -v ${WORKSPACE}/persistent:/data/persistent \
    -v ${WORKSPACE}/logs:/var/log/${DJANGO_PROJECT_NAME} \
    -v ${WORKSPACE}:/data/workspace \
    -w /data/workspace/code/${DJANGO_PROJECT_NAME} \
    --env-file ${WORKSPACE}/etc/docker_env_files/${ENV}.env \
    ${DOCKER_IMAGE_NAME} \
    bash -c "
      set -e && \
      pip install -r /data/workspace/etc/requirements.txt && \
      python3 manage.py runserver 0.0.0.0:8000
    "
    log_info "start over."
}

main $*
