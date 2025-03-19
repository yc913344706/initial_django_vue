get_docker_current_arch() {
  docker_current_arch=""
  if uname -a | grep -i arm64; then
    docker_current_arch="arm64"
  elif uname -a | grep -i x86_64; then
    docker_current_arch="amd64"
  fi
}

create_manifest() {
  need_create_manifest=false
  read -p "do you want to create this manifest? [y|yes]" ans

  ans=$(echo "$ans" | tr '[:upper:]' '[:lower:]')
  [ "${ans}" == "yes"  ] && need_create_manifest=true
  [ "${ans}" == "y"  ] && need_create_manifest=true

  "${need_create_manifest}" || {
    log_info "skip push manifest"
    return
  }

  # https://blog.csdn.net/linmengmeng_1314/article/details/123231087
  # https://yeasy.gitbook.io/docker_practice/image/manifest

  [ -n "${TARGET_IMAGE_USER}" ] || die "param less: TARGET_IMAGE_USER"
  [ -n "${TARGET_IMAGE_NAME}" ] || die "param less: TARGET_IMAGE_NAME"
  [ -n "${TARGET_IMAGE_TAG}" ] || die "param less: TARGET_IMAGE_TAG"

  amend_str="--amend"
  docker manifest inspect ${TARGET_IMAGE_USER}/${TARGET_IMAGE_NAME} || amend_str=""

  for i in "arm64" "amd64"
  do
    _image_name="${TARGET_IMAGE_USER}/${TARGET_IMAGE_NAME}:${i}_${TARGET_IMAGE_TAG}"
    docker images --format "{{.Repository}}:{{.Tag}}" | grep -w ${_image_name} || die "can not find image: ${_image_name}"
  done

  set -x
  docker manifest create ${amend_str} \
    ${TARGET_IMAGE_USER}/${TARGET_IMAGE_NAME}:${TARGET_IMAGE_TAG} \
    ${TARGET_IMAGE_USER}/${TARGET_IMAGE_NAME}:arm64_${TARGET_IMAGE_TAG} \
    ${TARGET_IMAGE_USER}/${TARGET_IMAGE_NAME}:amd64_${TARGET_IMAGE_TAG}

  docker manifest annotate ${TARGET_IMAGE_USER}/${TARGET_IMAGE_NAME}:${TARGET_IMAGE_TAG} \
        ${TARGET_IMAGE_USER}/${TARGET_IMAGE_NAME}:arm64_${TARGET_IMAGE_TAG} \
        --os linux --arch arm64 --variant v8

  docker manifest annotate ${TARGET_IMAGE_USER}/${TARGET_IMAGE_NAME}:${TARGET_IMAGE_TAG} \
        ${TARGET_IMAGE_USER}/${TARGET_IMAGE_NAME}:amd64_${TARGET_IMAGE_TAG} \
        --os linux --arch amd64

  docker manifest push ${TARGET_IMAGE_USER}/${TARGET_IMAGE_NAME}:${TARGET_IMAGE_TAG}
  set +x
}

push_image()
{
  need_push=false
  read -p "do you want to push this? [y|yes]" ans

  ans=$(echo "$ans" | tr '[:upper:]' '[:lower:]')
  [ "${ans}" == "yes"  ] && need_push=true
  [ "${ans}" == "y"  ] && need_push=true


  "${need_push}" || {
    log_info "skip push image"
    return
  }

  docker push "${DOCKER_IMAGE_NAME}"
}

stop_old_docker_container() {
  if docker ps | grep ${DOCKER_CONTAINER_NAME}; then
    log_info "old docker container ${DOCKER_CONTAINER_NAME} is running, stop it..."

    docker stop ${DOCKER_CONTAINER_NAME}
    sleep 2
    log_info "stop over..."
  fi
}
