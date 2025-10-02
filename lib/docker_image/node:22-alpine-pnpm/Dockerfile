ARG BASE_IMAGE=library/node:22-alpine
FROM ${BASE_IMAGE}

RUN /bin/sh -c "sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories"
RUN apk add --no-cache curl

RUN npm config set registry https://registry.npmmirror.com
RUN npm install -g pnpm


# https://github.com/pnpm/pnpm/issues/5803
RUN npm install --global pnpm@latest \
    && SHELL=bash pnpm setup \
    && source /root/.bashrc \
    && pnpm config set store-dir /root/.local/share/pnpm/store
