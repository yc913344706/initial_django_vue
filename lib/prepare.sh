prepare_django_config() {
    cp -a "${WORKSPACE}/etc/django_config_dir/${ENV}.yaml" "${WORKSPACE}/code/${DJANGO_PROJECT_NAME}/config.yaml"
}