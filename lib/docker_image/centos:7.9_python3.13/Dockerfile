ARG BASE_IMAGE=centos:7.9
FROM ${BASE_IMAGE}

RUN mkdir /etc/yum.repos.d/bak
RUN mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/bak/
COPY root/etc/yum.repos.d/centos.repo /etc/yum.repos.d/centos.repo
RUN yum makecache

# 配置dns服务器
RUN bash -c 'echo "223.5.5.5 >> /etc/resolv.conf"'


# RUN apt update
# RUN apt install -y python3 python3-pip


# # 解决问题: Can‘t start new thread
# RUN pip config --user set global.progress_bar off
# RUN bash -c 'pip3 config set global.trusted-host "pypi.tuna.tsinghua.edu.cn pypi.douban.com"'
# RUN bash -c 'pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple'
# #RUN bash -c 'pip3 config set global.extra-index-url http://pypi.douban.com/simple'
# RUN bash -c 'pip3 install --upgrade setuptools'
# RUN python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip

# # 时区
# RUN apt-get install -y locales tzdata xfonts-wqy && \
#     locale-gen zh_CN.UTF-8 && \
#     update-locale LANG=zh_CN.UTF-8 LANGUAGE=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8 && \
#     ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
#     dpkg-reconfigure --frontend noninteractive tzdata
# ENV LANG=zh_CN.UTF-8 LANGUAGE=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8

# # 安装基础包
# RUN apt update
# RUN apt install -y vim curl netcat git inetutils-ping telnet net-tools wget

# # 清理缓存
# RUN apt clean all
# RUN find /var/lib/apt/lists -type f -delete && \
#     find /var/cache -type f -delete
