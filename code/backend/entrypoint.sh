#!/bin/bash

source /etc/profile
pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py create_admin_user
uwsgi \
  --set-placeholder UWSGI_CPU_PROCESSES=${UWSGI_CPU_PROCESSES} \
  --set-placeholder UWSGI_CPU_THREADS=${UWSGI_CPU_THREADS} \
  --ini uwsgi.ini:prod