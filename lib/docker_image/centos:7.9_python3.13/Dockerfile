ARG BASE_IMAGE=centos:7.9
FROM ${BASE_IMAGE}

RUN mkdir /etc/yum.repos.d/bak
RUN mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/bak/
# 阿里云对 CentOS 7.9.2009 的 YUM 源支持方案
# https://www.cnblogs.com/sinlang5778/p/18764676
COPY root/etc/yum.repos.d/centos.repo /etc/yum.repos.d/centos.repo
RUN yum makecache

# 配置dns服务器
RUN bash -c 'echo "223.5.5.5 >> /etc/resolv.conf"'

RUN yum groupinstall -y "Development Tools"
RUN yum install -y gcc zlib-devel bzip2 bzip2-devel \
    readline-devel sqlite sqlite-devel openssl-devel \
    xz xz-devel libffi-devel wget make vim 

RUN yum clean all && yum makecache && yum repolist
RUN rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7

RUN yum install -y gcc-c++ \
    tk-devel gdbm-devel \
    libuuid-devel libnsl2-devel libtirpc-devel \
    findutils patch devtoolset-9

ENV PYTHON_VERSION=3.13.4

# 后续每个 RUN 前加
SHELL ["/bin/bash", "-c"]
RUN source /opt/rh/devtoolset-9/enable && \
    cd /usr/src && \
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


# RUN apt update
# RUN apt install -y python3 python3-pip


# # 解决问题: Can‘t start new thread
# RUN pip config --user set global.progress_bar off
# RUN bash -c 'pip3 config set global.trusted-host "pypi.tuna.tsinghua.edu.cn pypi.douban.com"'
# RUN bash -c 'pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple'
# #RUN bash -c 'pip3 config set global.extra-index-url http://pypi.douban.com/simple'
# RUN bash -c 'pip3 install --upgrade setuptools'
# RUN python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip

# 设置时区和中文
RUN yum install -y glibc-common tzdata wqy-zenhei-fonts && \
    localedef -c -f UTF-8 -i zh_CN zh_CN.UTF-8 && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo 'LANG=zh_CN.UTF-8' > /etc/locale.conf

ENV LANG=zh_CN.UTF-8
ENV LANGUAGE=zh_CN:zh
ENV LC_ALL=zh_CN.UTF-8

# 安装基础包
RUN yum install -y vim curl nc git iputils telnet net-tools wget

# 清理缓存
RUN yum clean all && rm -rf /var/cache/yum
