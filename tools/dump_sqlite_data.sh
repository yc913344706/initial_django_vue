#!/bin/bash

set -e

WORKSPACE="$(dirname $(dirname $(realpath $0)))"

# 导出sqlite3数据

sqlite3 ${WORKSPACE}/code/backend/db.sqlite3 .dump > ${WORKSPACE}/output/sqlite3_dump.sql
