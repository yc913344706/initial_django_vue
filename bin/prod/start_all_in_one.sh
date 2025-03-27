#!/bin/bash

set -e
set -o errexit
set -o pipefail

# 基本导入
WORKSPACE="$(dirname $(dirname $(dirname $(realpath $0))))"

. "${WORKSPACE}"/lib/log.sh
. "${WORKSPACE}"/lib/param.sh
. "${WORKSPACE}"/lib/check.sh

usage() {
    echo "Usage:"
    echo "    $0 -E <env> [-hd]"
    echo "    E: required, 指定环境名称. dev, test, prod"
    echo "    d: optional, debug mode"
    echo "    h: optional, print help information"
}

pre_check() {
    check_var_exists "ENV"
    check_command_exists "docker"
}

main() {
    # 参数解析
    analyze_params $*

    pre_check

    # 启动后端
    "${WORKSPACE}/bin/prod/start_backend_uwsgi.sh" -E "${ENV}"

    # 启动前端
    "${WORKSPACE}/bin/prod/start_compile_frontend.sh" -E "${ENV}"
}

main $*