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

push_image_with_manifest_for_arch() {
  check_command_exists "jq"

  # 获取当前架构
  get_os_arch
  check_var_exists "OS_ARCH"

  _image_name=$1
  _image_tag=$2

  # 先推送当前架构的镜像
  docker tag ${_image_name}:${_image_tag} ${_image_name}:${OS_ARCH}_${_image_tag}
  docker push ${_image_name}:${OS_ARCH}_${_image_tag}

  # 检查是否已存在 manifest
  amend_str="--amend"
  docker manifest inspect ${_image_name}:${_image_tag} || amend_str=""

  # 获取所有已存在的架构镜像
  already_known_archs="arm64 amd64"
  _manifest_args=""
  _archs_to_annotate=""
  
  for _arch in ${already_known_archs}; do
    if docker manifest inspect ${_image_name}:${_arch}_${_image_tag} >/dev/null 2>&1; then
      _manifest_args="${_manifest_args} ${_image_name}:${_arch}_${_image_tag}"
      _archs_to_annotate="${_archs_to_annotate} ${_arch}"
    fi
  done

  # 如果没有找到任何架构的镜像，使用当前架构
  if [ -z "${_manifest_args}" ]; then
    _manifest_args="${_image_name}:${OS_ARCH}_${_image_tag}"
    _archs_to_annotate="${OS_ARCH}"
  fi

  # 创建或更新 manifest
  docker manifest create ${amend_str} \
    ${_image_name}:${_image_tag} \
    ${_manifest_args}

  # 为每个架构添加注解
  for _arch in ${_archs_to_annotate}; do
    if [ "${_arch}" = "arm64" ]; then
      docker manifest annotate ${_image_name}:${_image_tag} \
        ${_image_name}:${_arch}_${_image_tag} \
        --os linux --arch ${_arch} --variant v8
    else
      docker manifest annotate ${_image_name}:${_image_tag} \
        ${_image_name}:${_arch}_${_image_tag} \
        --os linux --arch ${_arch}
    fi
  done

  # 推送更新后的 manifest
  docker manifest push ${_image_name}:${_image_tag}
}

push_image()
{
  need_push=false

  _docker_image_name=$1
  read -p "do you want to push this? [y|yes]" ans

  ans=$(echo "$ans" | tr '[:upper:]' '[:lower:]')
  [ "${ans}" == "yes"  ] && need_push=true
  [ "${ans}" == "y"  ] && need_push=true


  "${need_push}" || {
    log_info "skip push image"
    return
  }

  docker push "${_docker_image_name}"
}

stop_rm_docker_container() {
  if docker ps | grep ${DOCKER_CONTAINER_NAME}; then
    log_info "old docker container ${DOCKER_CONTAINER_NAME} is running, stop it..."

    docker stop ${DOCKER_CONTAINER_NAME}
    sleep 2
    log_info "stop over..."
  fi

  if docker ps -a | grep ${DOCKER_CONTAINER_NAME}; then
    log_info "old docker container ${DOCKER_CONTAINER_NAME} is exist, remove it..."
    docker rm ${DOCKER_CONTAINER_NAME}
    log_info "remove over..."
  fi
}

check_docker_image_exist() {
  _image_name=$1
  _image_tag=$2

  docker images | grep "${_image_name}" | grep "${_image_tag}" || die "docker image ${_image_name}:${_image_tag} not found"
}
