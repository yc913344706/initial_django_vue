ARG BASE_IMAGE=ubuntu:20.04_python3.8
FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND noninteractive

RUN apt update && apt install -y libldap2-dev libsasl2-dev

COPY tmp/requirements.txt /tmp/requirements.txt

RUN pip3 install --verbose -r /tmp/requirements.txt

# 清理缓存
RUN apt clean all
RUN find /var/lib/apt/lists -type f -delete && \
    find /var/cache -type f -delete
