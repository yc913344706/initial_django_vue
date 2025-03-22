ARG BASE_IMAGE=yc913344706/ubuntu:20.04_python3.8
FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND noninteractive

# 安装uwsgi
RUN apt update && apt install -y libldap2-dev libsasl2-dev uwsgi

# 安装python-mysql所需包
RUN apt install -y python3.10-dev python3-mysqldb libmysqlclient-dev

COPY tmp/requirements.txt /tmp/requirements.txt

RUN pip3 install --verbose -r /tmp/requirements.txt

# 清理缓存
RUN apt clean all
RUN find /var/lib/apt/lists -type f -delete && \
    find /var/cache -type f -delete
