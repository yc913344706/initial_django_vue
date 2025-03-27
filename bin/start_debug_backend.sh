#! /bin/bash

WORKSPACE="$(dirname $(dirname $(realpath $0)))"

echo "WORKSPACE: ${WORKSPACE}"

cd "${WORKSPACE}/code/backend"
python manage.py runserver 0.0.0.0:8000
