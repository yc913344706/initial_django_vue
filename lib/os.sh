get_os_arch() {
  OS_ARCH=""
  case "$(uname -m)" in
    x86_64) OS_ARCH="amd64" ;;
    aarch64) OS_ARCH="arm64" ;;
    arm64) OS_ARCH="arm64" ;;
    *) die "unsupported architecture: $(uname -m)" ;;
  esac
}
