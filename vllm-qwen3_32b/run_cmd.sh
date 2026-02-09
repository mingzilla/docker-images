#!/bin/bash
set -e
cd "$(dirname "$0")"
source ../_common/common_cmd.sh

##############################################################

if [ $# -eq 0 ]; then
    help::show "qwen3"
    exit 1
fi

if [ "$1" == "curl_qwen3" ]; then
    curl::test_model "30200" "nvidia/Qwen3-32B-NVFP4"
fi

if [ "$1" == "log_qwen3" ]; then
    docker::view_logs "vllm-qwen3-nvfp4"
fi
