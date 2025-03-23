#!/bin/bash

set -e
set -o errexit
set -o pipefail

# 基本导入
WORKSPACE="$(dirname $(dirname $(realpath $0)))"

. "${WORKSPACE}"/lib/log.sh
. "${WORKSPACE}"/lib/check.sh
. "${WORKSPACE}"/lib/param.sh
. "${WORKSPACE}"/lib/prepare.sh
. "${WORKSPACE}"/lib/docker_tools.sh

pre_check() {
  check_var_exists "ENV"
  . "${WORKSPACE}"/etc/docker_env_files/${ENV}.env

  # 检查项目目录
  check_dir_exists "${WORKSPACE}/code/${DJANGO_PROJECT_NAME}"

  # 检查环境变量文件
  check_file_exists "${WORKSPACE}/etc/docker_env_files/${ENV}.env"
  check_file_exists "${WORKSPACE}/etc/config_dir/${ENV}.yaml"
  prepare_django_config "${WORKSPACE}/etc/config_dir/${ENV}.yaml"

  rm -rf ${WORKSPACE}/code/${DJANGO_PROJECT_NAME}/base_routes.json && \
    cp -a ${WORKSPACE}/etc/backend/perm_jsons/base_routes.json \
    ${WORKSPACE}/code/${DJANGO_PROJECT_NAME}/base_routes.json

  # 检查必要的命令
  check_command_exists "docker"
}

main() {

  # 参数解析
  analyze_params $*

  pre_check

  DOCKER_CONTAINER_NAME="${DJANGO_PROJECT_NAME}_DJANGO_UWSGI"
  stop_old_docker_container "${DOCKER_CONTAINER_NAME}"

  # log_info "need sudo, please input sudo password."
  # sudo mkdir -p ${WORKSPACE}/logs
  # sudo chown -R 644 ${WORKSPACE}/logs

  # 运行
  log_info "start docker uwsgi..."
  docker run -itd --rm \
    -p 8000:8000 \
    --name ${DOCKER_CONTAINER_NAME} \
    -v ${WORKSPACE}/etc/backend/hosts:/etc/hosts \
    -v ${WORKSPACE}/etc/backend/resolv.conf:/etc/resolv.conf \
    -v ${WORKSPACE}/persistent:/data/persistent \
    -v ${WORKSPACE}/logs:/var/log/${DJANGO_PROJECT_NAME} \
    -v ${WORKSPACE}:/data/workspace \
    -w /data/workspace \
    --env-file ${WORKSPACE}/etc/docker_env_files/${ENV}.env \
    ${DOCKER_IMAGE_NAME} \
    bash -c "
      set -e && \
      pip3 install -r /data/workspace/etc/backend/requirements.txt && \
      uwsgi \
        --set-placeholder DJANGO_PROJECT_NAME=${DJANGO_PROJECT_NAME} \
        --set-placeholder UWSGI_CPU_PROCESSES=${UWSGI_CPU_PROCESSES} \
        --set-placeholder UWSGI_CPU_THREADS=${UWSGI_CPU_THREADS} \
        --ini /data/workspace/etc/backend/uwsgi.ini:prod
    "
    log_info "start over."
}

main $*
