#!/bin/bash
set -e
cd "$(dirname "$0")"
source ../_common/common_cmd.sh

##############################################################

if [ $# -eq 0 ]; then
    help::show "qwen2.5"
    exit 1
fi

if [ "$1" == "curl_qwen2.5" ]; then
    curl::test_model "30200" "Qwen2.5-32B-Instruct-NVFP4"
fi

if [ "$1" == "log_qwen2.5" ]; then
    docker::view_logs "vllm-qwen2.5-nvfp4"
fi

if [ "$1" == "save_qwen2.5" ]; then
    docker::save_as_tar "vllm-qwen2.5-nvfp4:local" "vllm-qwen2.5-nvfp4.tar"
fi
