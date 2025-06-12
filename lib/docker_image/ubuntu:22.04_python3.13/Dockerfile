ARG BASE_IMAGE=ubuntu:22.04
FROM ${BASE_IMAGE}

# 拉取基础镜像、海外镜像、海外基础镜像
# [root@k8s-server-45-151 ~/yuc7]#./download_common_image.sh

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt install -y ca-certificates

# 配置dns服务器
RUN bash -c 'echo "223.5.5.5 >> /etc/resolv.conf"'

COPY root/etc/apt/sources.list /etc/apt/sources.list

RUN apt update

ENV PYTHON_VERSION=3.13.4

# 后续每个 RUN 前加
RUN cd /usr/src && \
    wget https://mirrors.aliyun.com/python-release/source/Python-$PYTHON_VERSION.tgz && \
    tar xvf Python-$PYTHON_VERSION.tgz && \
    rm -f Python-$PYTHON_VERSION.tgz && \
    cd Python-$PYTHON_VERSION && \
    ./configure \
        --prefix=/opt/python$PYTHON_VERSION \
        --enable-optimizations \
        --disable-test-modules && \
    make -j$(nproc) && \
    make install
    # --without-pymalloc \
    # --without-static-libpython && \

RUN ln -sf /opt/python$PYTHON_VERSION/bin/python3 /usr/local/sbin/python$PYTHON_VERSION && \
    ln -sf /opt/python$PYTHON_VERSION/bin/pip3 /usr/local/sbin/pip$PYTHON_VERSION && \
    ln -sf /opt/python$PYTHON_VERSION/bin/python3 /usr/local/sbin/python3 && \
    ln -sf /opt/python$PYTHON_VERSION/bin/pip3 /usr/local/sbin/pip3 && \
    ln -sf /opt/python$PYTHON_VERSION/bin/python3 /usr/local/sbin/python && \
    ln -sf /opt/python$PYTHON_VERSION/bin/pip3 /usr/local/sbin/pip


# 解决问题: Can‘t start new thread
RUN pip config --user set global.progress_bar off
RUN bash -c 'pip3 config set global.trusted-host "pypi.tuna.tsinghua.edu.cn pypi.douban.com"'
RUN bash -c 'pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple'
#RUN bash -c 'pip3 config set global.extra-index-url http://pypi.douban.com/simple'
RUN bash -c 'pip3 install --upgrade setuptools'
RUN python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip

# 时区
RUN apt-get install -y locales tzdata xfonts-wqy && \
    locale-gen zh_CN.UTF-8 && \
    update-locale LANG=zh_CN.UTF-8 LANGUAGE=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8 && \
    ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata
ENV LANG=zh_CN.UTF-8 LANGUAGE=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8

# 安装基础包
RUN apt update
RUN apt install -y vim curl netcat git inetutils-ping telnet net-tools wget

# 清理缓存
RUN apt clean all
RUN find /var/lib/apt/lists -type f -delete && \
    find /var/cache -type f -delete
