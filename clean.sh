#!/bin/bash

# initial_django_vue 项目的清理脚本
# 此脚本用于删除 Docker 容器、网络、卷，并清理 data/logs 目录

set -e  # 如果命令以非零状态退出，则立即退出

echo "开始清理 initial_django_vue 项目..."

# 停止并删除与此项目相关的所有容器
echo "正在停止并删除容器..."
docker-compose -f docker-compose.dev.yaml down --remove-orphans || true
docker-compose -f docker-compose.prod.yaml down --remove-orphans || true

# 删除任何剩余的项目名称容器
docker ps -aq --filter=name=initial_django_vue_ | xargs -r docker rm -f

# 删除所有项目网络
echo "正在删除网络..."
docker network ls --format='{{.ID}} {{.Name}}' | grep initial_django_vue_ | awk '{print $1}' | xargs -r docker network rm

# 删除任何悬空的卷
echo "正在删除未使用的卷..."
docker volume prune -f

# 清理数据目录（不包括目录本身）
echo "正在清理数据目录..."
if [ -d "./data" ]; then
    for dir in ./data/*/; do
        if [ -d "$dir" ] && [ "$dir" != "./data/" ]; then
            echo "正在清空 $dir"
            rm -rf "$dir"/*
        fi
    done
fi

# 清理日志目录（不包括目录本身）
echo "正在清理日志目录..."
if [ -d "./logs" ]; then
    for dir in ./logs/*/; do
        if [ -d "$dir" ] && [ "$dir" != "./logs/" ]; then
            echo "正在清空 $dir"
            rm -rf "$dir"/*
        fi
    done
fi

# 清理可能与此项目相关的任何悬空 Docker 镜像
echo "正在删除悬空的镜像..."
docker image prune -f

echo "清理完成！"
echo ""
echo "要重新启动项目，请运行:"
echo "  docker-compose -f docker-compose.dev.yaml up -d"