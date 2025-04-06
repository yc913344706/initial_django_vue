ARG BASE_IMAGE=library/node:20-alpine
FROM ${BASE_IMAGE}
RUN npm config set registry https://registry.npmmirror.com
RUN npm install -g pnpm
# https://github.com/pnpm/pnpm/issues/5803
RUN npm install --global pnpm@latest \
    && SHELL=bash pnpm setup \
    && source /root/.bashrc \
    && pnpm config set store-dir /root/.local/share/pnpm/store
