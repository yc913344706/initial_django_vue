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

  # 检查必要的命令
  check_command_exists "docker"
}

main() {

  # 参数解析
  analyze_params $*

  pre_check

  DOCKER_CONTAINER_NAME="${DJANGO_PROJECT_NAME}_DJANGO_UWSGI"
  stop_old_docker_container "${DOCKER_CONTAINER_NAME}"

  log_info "stop over."
}

main $*
