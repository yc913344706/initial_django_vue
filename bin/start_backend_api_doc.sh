#! /bin/bash

WORKSPACE="$(dirname $(dirname $(realpath $0)))"

cd "${WORKSPACE}"
mkdocs serve --dev-addr=0.0.0.0:8008
