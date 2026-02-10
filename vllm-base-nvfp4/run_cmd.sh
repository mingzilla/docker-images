#!/bin/bash
set -e
cd "$(dirname "$0")"
source ../_common/common_cmd.sh

##############################################################

if [ $# -eq 0 ]; then
    help::show "vllm-base-nvfp4"
    exit 1
fi

if [ "$1" == "log" ]; then
    docker::view_logs "vllm-base-nvfp4"
fi

if [ "$1" == "save_tar" ]; then
    docker::save_as_tar "vllm-base-nvfp4:local" "vllm-base-nvfp4-blackwell-for-0.15.1.tar"
fi
