#!/bin/bash

set -e
set -o errexit
set -o pipefail

# 基本导入
WORKSPACE="$(dirname $(dirname $(dirname $(realpath $0))))"

. "${WORKSPACE}"/lib/log.sh
. "${WORKSPACE}"/lib/check.sh
. "${WORKSPACE}"/lib/param.sh
. "${WORKSPACE}"/lib/prepare.sh
. "${WORKSPACE}"/lib/docker_tools.sh
. "${WORKSPACE}"/lib/sh_read_yaml.sh

usage() {
    echo "Usage:"
    echo "    $0 -E <env> [-hd]"
    echo "    E: required, 指定环境名称. dev"
    echo "    d: optional, debug mode"
    echo "    h: optional, print help information"
}

pre_check() {
  check_var_exists "ENV"
  . "${WORKSPACE}"/etc/docker_env_files/${ENV}.env

  # 检查必要的命令
  check_command_exists "docker"

  # 检查项目目录
  check_dir_exists "${WORKSPACE}/code/${DJANGO_PROJECT_NAME}"

  # 检查环境变量文件
  check_file_exists "${WORKSPACE}/etc/docker_env_files/${ENV}.env"
  check_file_exists "${WORKSPACE}/etc/config_dir/${ENV}.yaml"

  # # 检查HAS_REDIS
  # HAS_REDIS=$(read_yaml_key_docker "${WORKSPACE}/etc/config_dir/${ENV}.yaml" "HAS_REDIS")

  # 准备配置文件
  prepare_config_file \
    "${WORKSPACE}/etc/config_dir/${ENV}.yaml" \
    "${WORKSPACE}/code/${DJANGO_PROJECT_NAME}/config.yaml"

  # 准备基础路由文件
  prepare_config_file \
    "${WORKSPACE}/etc/backend/perm_jsons/base_routes.json" \
    "${WORKSPACE}/code/${DJANGO_PROJECT_NAME}/base_routes.json"
}

main() {

  # 参数解析
  analyze_params $*

  pre_check

  DOCKER_CONTAINER_NAME="${DJANGO_PROJECT_NAME}_${DJANGO_CELERY_CONTAINER_NAME_SUFFIX}"
  stop_rm_docker_container "${DOCKER_CONTAINER_NAME}"

  # log_info "need sudo, please input sudo password."
  # sudo mkdir -p ${WORKSPACE}/logs
  # sudo chown -R 644 ${WORKSPACE}/logs

  # 运行
  log_info "start docker ${DOCKER_CONTAINER_NAME}..."
  docker run -itd --rm \
    --name ${DOCKER_CONTAINER_NAME} \
    -v ${WORKSPACE}/etc/backend/hosts:/etc/hosts \
    -v ${WORKSPACE}/etc/backend/resolv.conf:/etc/resolv.conf \
    -v ${WORKSPACE}/persistent:/data/persistent \
    -v ${WORKSPACE}/logs:/var/log/${DJANGO_PROJECT_NAME} \
    -v ${WORKSPACE}:/data/workspace \
    -w /data/workspace/code/${DJANGO_PROJECT_NAME} \
    --env-file ${WORKSPACE}/etc/docker_env_files/${ENV}.env \
    ${DJANGO_IMAGE_NAME} \
    bash -c "
      celery -A ${DJANGO_PROJECT_NAME} worker -l info -B --logfile /var/log/${DJANGO_PROJECT_NAME}/celery.log
    "

    # -B：这个参数用于启动一个内置的定时任务调度器（Beat）。
    # Beat 是 Celery 的一个组件，用于定时发送任务。如果你的应用需要定时执行任务，那么你需要启动 Beat。
    # 注意，-B 参数启动的 Beat 运行在同一个进程中，如果你需要在一个单独的进程中运行 Beat，你应该单独启动一个 Beat 进程。
    log_info "start ${DOCKER_CONTAINER_NAME} over."
}

main $*
