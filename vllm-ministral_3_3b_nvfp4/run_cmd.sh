#!/bin/bash
set -e
cd "$(dirname "$0")"
source ../_common/common_cmd.sh

##############################################################

if [ $# -eq 0 ]; then
    help::show
    exit 1
fi

if [ "$1" == "curl" ]; then
    curl::test_model "30200" "Firworks/Ministral-3-3B-Instruct-2512-nvfp4"
fi

if [ "$1" == "log" ]; then
    docker::view_logs "vllm-ministral3-nvfp4"
fi

if [ "$1" == "save" ]; then
    docker::save_as_tar "vllm-ministral3-nvfp4:local" "vllm-ministral3-nvfp4.tar"
fi
