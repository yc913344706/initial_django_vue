check_dir_exists() {
    local dir_path="$1"
    [ -d "$dir_path" ] || die "can not find dir: $dir_path"
}

check_var_exists() {
    # 检查变量是否存在
    local var_name="$1"
    local var_value="${!var_name}"
    [ -n "$var_value" ] || die "请指定参数 $var_name"
}

check_file_exists() {
    local file_path="$1"
    [ -f "$file_path" ] || die "can not find file: $file_path"
}

check_command_exists() {
    local command_name="$1"
    command -v "$command_name" >/dev/null 2>&1 || die "请安装命令: $command_name"
}
