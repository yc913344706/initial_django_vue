#! /bin/bash

WORKSPACE="$(dirname $(dirname $(realpath $0)))"

echo "WORKSPACE: ${WORKSPACE}"

cd "${WORKSPACE}/code/frontend"
pnpm store prune
pnpm install
pnpm dev
