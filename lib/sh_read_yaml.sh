read_yaml_key_docker() {
    # key_path 支持点分隔的 key 路径，例如：
    # key_path="a.b.c" 表示读取 yaml 文件中 a 的 b 的 c 的值
    local yaml_file=$1
    local key_path=$2

    local read_yaml_py="${WORKSPACE}/lib/sh_read_yaml.py"
    local value=$(
        docker run --rm \
            -v "${WORKSPACE}:${WORKSPACE}" \
            -w "${WORKSPACE}" \
            -v "${yaml_file}:${yaml_file}" \
            ${DJANGO_IMAGE_NAME} \
            python3 "./lib/sh_read_yaml.py" "$yaml_file" "$key_path"
    )
    echo "$value"
}

read_yaml_key() {
    # key_path 支持点分隔的 key 路径，例如：
    # key_path="a.b.c" 表示读取 yaml 文件中 a 的 b 的 c 的值
    local yaml_file=$1
    local key_path=$2
    local read_yaml_py="${WORKSPACE}/lib/sh_read_yaml.py"
    if [ ! -f "$read_yaml_py" ]; then
        die "sh_read_yaml.py not found"
    fi
    python3 "$read_yaml_py" "$yaml_file" "$key_path"
}
