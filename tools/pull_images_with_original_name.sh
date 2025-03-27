#!/bin/bash

set -xe

WORKSPACE="$(dirname $(dirname $(realpath $0)))"

. "${WORKSPACE}"/etc/global_config.sh

IS_FOR_K8S=false

docker_images=(
certbot/certbot
langgenius/dify-api:0.15.3
langgenius/dify-sandbox:0.2.10
langgenius/dify-web:0.15.3
langgenius/qdrant:v1.7.3
milvusdb/milvus:v2.5.0-beta
minio/minio:RELEASE.2023-03-20T20-16-18Z
myscale/myscaledb:1.6.4
nginx:latest
opensearchproject/opensearch-dashboards:latest
opensearchproject/opensearch:latest
pgvector/pgvector:pg16
pingcap/tidb:v8.4.0
postgres:15-alpine
redis:6-alpine
semitechnologies/weaviate:1.19.0
tensorchord/pgvecto-rs:pg16-v0.3.0
ubuntu/squid:latest

container-registry.oracle.com/database/free:latest
docker.elastic.co/elasticsearch/elasticsearch:8.14.3
docker.elastic.co/kibana/kibana:8.14.3

# https://github.com/Unstructured-IO/unstructured-api/issues/480#issuecomment-2571564395
robwilkes/unstructured-api:latest

ghcr.io/chroma-core/chroma:0.5.20
quay.io/coreos/etcd:v3.5.5
quay.io/oceanbase/oceanbase-ce:4.3.3.0-100000142024101215
)

k8s_docker_pull_image() {
    command -v ctr > /dev/null 2>&1 && {
        ctr -n k8s.io image pull $1
        return
    }
    command -v docker > /dev/null 2>&1 && {
        docker pull $1
        return
    }
    die "docker or ctr not found"
}

k8s_docker_tag_image() {
    command -v ctr > /dev/null 2>&1 && {
        ctr -n k8s.io image tag $1 $2
        return
    }
    command -v docker > /dev/null 2>&1 && {
        docker tag $1 $2
        return
    }
    die "docker or ctr not found"
}

for i in "${docker_images[@]}"
do
    sleep 1

    new_i=$i
    # 检测是否包含命名空间（以是否包含 "/" 判断）
    if [[ "$i" == */*/* ]]; then
        # 如果 不是 docker.io 不使用代理
        proxy_image="$i"
    elif [[ "$i" == */* ]]; then
        # 如果 是 docker.io 使用代理
        proxy_image="${PRIVATE_HARBOR_PREFIX}$i"
    else
        # 如果没有命名空间，增加 library 作为命名空间
        proxy_image="${PRIVATE_HARBOR_PREFIX}library/$i"
    fi

    if [ "$IS_FOR_K8S" = true ]; then
        k8s_docker_pull_image $proxy_image
        k8s_docker_tag_image $proxy_image "${i}"
    else
        docker pull $proxy_image
        docker tag $proxy_image "${i}"
    fi

done
