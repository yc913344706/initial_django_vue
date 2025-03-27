prepare_config_file() {
    _src_config_file="$1"
    _dest_config_file="$2"
    [ -f "${_dest_config_file}" ] && \
        rm -f "${_dest_config_file}"
    cp -a "${_src_config_file}" "${_dest_config_file}"
}