prepare_django_config() {
    [ -f "${WORKSPACE}/code/${DJANGO_PROJECT_NAME}/config.yaml" ] && \
        rm -f "${WORKSPACE}/code/${DJANGO_PROJECT_NAME}/config.yaml"
    cp -a "${1}" "${WORKSPACE}/code/${DJANGO_PROJECT_NAME}/config.yaml"
}