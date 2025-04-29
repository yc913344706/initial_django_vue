ARG BASE_IMAGE=yc913344706/python:3.10_django
FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive

COPY tmp/requirements.txt /tmp/requirements.txt

RUN pip3 install --verbose -r /tmp/requirements.txt

# 清理缓存
RUN apt clean all
RUN find /var/lib/apt/lists -type f -delete && \
    find /var/cache -type f -delete
