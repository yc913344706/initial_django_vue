#!/bin/bash

LOG_LEVEL=${LOG_LEVEL:-"INFO"}
_log_level=$(echo "${LOG_LEVEL}" | tr '[:upper:]' '[:lower:]')
case "${_log_level}" in
        ERROR)
               _log_level_num=4
               ;;
        WARN)
               _log_level_num=3
               ;;
        INFO)
               _log_level_num=2
               ;;
        DEBUG)
               _log_level_num=1
               set -x
               ;;
        ALL)
               _log_level_num=0
               set -x
               ;;
        *)
               _log_level_num=2
               ;;
esac

die()
{
    log_error "$*"
    exit 1
}

log()
{
    log_info "$*"
}

log_error()
{
        [ ${_log_level_num} -le 4 ] || return 0
        date +"[ERROR] %F %T $*" >&2
}

log_warn()
{
        [ ${_log_level_num} -le 3 ] || return 0
        date +"[WARN] %F %T $*" >&2
}

log_info()
{
        [ ${_log_level_num} -le 2 ] || return 0
        date +"[INFO] %F %T $*"
}

log_debug()
{
        [ ${_log_level_num} -le 1 ] || return 0
        date +"[DEBUG] %F %T $*"
}

