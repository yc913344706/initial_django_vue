#!/bin/bash

set -e
set -o errexit
set -o pipefail

# 基本导入
WORKSPACE="$(dirname $(dirname $(realpath $0)))"

. "${WORKSPACE}"/lib/log.sh
. "${WORKSPACE}"/lib/check.sh
. "${WORKSPACE}"/lib/param.sh
. "${WORKSPACE}"/lib/docker_tools.sh

usage() {
    echo "Usage:"
    echo "    $0 -E <env> [-hd]"
    echo "    E: required, 指定环境名称. dev, test, prod"
    echo "    d: optional, debug mode"
    echo "    h: optional, print help information"
}

pre_check() {
    check_var_exists "ENV"
    . "${WORKSPACE}"/etc/docker_env_files/${ENV}.env

    # 检查必要的命令
    check_command_exists "docker"

    # 全局变量
    FRONTEND_DIR="${WORKSPACE}/code/${FRONTEND_PROJECT_NAME}"

    # 检查项目目录
    check_dir_exists "${FRONTEND_DIR}"

    # 检查环境变量文件
    _env_file="${FRONTEND_DIR}/.env.${ENV}"
    case "${ENV}" in
        dev)
            _env_file="${FRONTEND_DIR}/.env.development"
            ;;
        *)
            die "Invalid environment: ${ENV}"
            ;;
    esac
    log_info "检查环境变量文件: ${_env_file}"
    check_file_exists "${_env_file}"
}

setup_container() {
    log_info "准备构建环境..."
    
    # 移除可能存在的同名容器
    stop_rm_docker_container "${DOCKER_CONTAINER_NAME}"
    
    # 启动构建容器
    log_info "启动构建容器"
    docker run -d --name ${DOCKER_CONTAINER_NAME} \
        -v "${WORKSPACE}/code/${FRONTEND_PROJECT_NAME}:/workspace" \
        -p ${FRONTEND_SERVER_PORT_IN_HOST}:8080 \
        -w "/workspace" \
        ${FRONTEND_IMAGE} \
        tail -f /dev/null

}

cleanup_container() {
    log_info "清理构建环境..."
    stop_rm_docker_container "${DOCKER_CONTAINER_NAME}"
}

install_deps() {
    log_info "正在安装依赖..."
    docker exec ${DOCKER_CONTAINER_NAME} pnpm store prune
    docker exec ${DOCKER_CONTAINER_NAME} pnpm install
}

build_frontend() {
    log_info "正在构建前端项目..."
    docker exec ${DOCKER_CONTAINER_NAME} pnpm dev
}

main() {
    # 参数解析
    analyze_params $*

    # 环境检查
    pre_check
    DOCKER_CONTAINER_NAME="${FRONTEND_PROJECT_NAME}_${FRONTEND_CONTAINER_NAME_SUFFIX}"

    # 设置构建容器
    setup_container

    # 安装依赖
    install_deps

    # 构建项目
    build_frontend
    log_info "前端项目启动完成"
}

main $*
