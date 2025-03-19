analyze_params() {
    # Reset OPTIND
    OPTIND=1
    while getopts ':E:dh' OPTION; do
        case "$OPTION" in
            "E")
                ENV="$OPTARG"
                [ -n "$OPTARG" ] && log_debug "Option $OPTION has value $OPTARG"
                ;;
            "d")
                set -x
                [ -n "$OPTARG" ] && log_debug "Option $OPTION has value $OPTARG"
                ;;
            "h")
                usage
                exit 0
                ;;
            ?)
                die "Invalid parameter"
                ;;
            *)
                # Should not occur
                die "Unknown error while processing options"
                ;;
        esac
    done
    shift $((OPTIND-1))
}

base_analyze_params() {
    OPTIND=1
    while getopts ':dh' OPTION; do
        case "$OPTION" in
            "d")
                set -x
                [ -n "$OPTARG" ] && log_debug "Option $OPTION has value $OPTARG"
                ;;
            "h")
                usage
                exit 0
                ;;
            ?)
                die "Invalid parameter"
                ;;
            *)
                # Should not occur
                die "Unknown error while processing options"
                ;;
        esac
    done
    shift $((OPTIND-1))
}