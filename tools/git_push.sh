#!/bin/bash

set -e


WORKSPACE="$(dirname $(dirname $(realpath $0)))"

. "${WORKSPACE}"/lib/log.sh

cd ${WORKSPACE}/

# 检查git status是否干净
[ -f ./grep_file.txt ] || die "grep_file.txt not found"
if grep -f ./grep_file.txt -r . | grep -v grep_file.txt; then
    die "git status is not clean"
else
    log_info "git status is clean"
fi

# 用户确认 git status
git status

read -p "Are you sure to push to remote? (y/n): " confirm
if [ "${confirm}" != "y" ]; then
  die "push to remote canceled"
fi

# 检查是否存在commit message
commit_message=$1

if [ -z "${commit_message}" ]; then
  die "commit message is required"
fi

log_info "start git push..."
git add .
git commit -m "${commit_message}"
git push
