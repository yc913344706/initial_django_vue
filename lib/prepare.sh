prepare_django_config() {
    cp -a "${1}" "${WORKSPACE}/code/${DJANGO_PROJECT_NAME}/config.yaml"
}