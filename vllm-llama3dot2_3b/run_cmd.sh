#!/bin/bash
set -e
cd "$(dirname "$0")"
source ../_common/common_cmd.sh

##############################################################

if [ $# -eq 0 ]; then
    help::show "llama3"
    exit 1
fi

if [ "$1" == "curl_llama3" ]; then
    curl::test_model "30200" "neuralmagic/Llama-3.2-3B-Instruct-FP4"
fi

if [ "$1" == "log_llama3" ]; then
    docker::view_logs "vllm-llama-nvfp4"
fi

if [ "$1" == "save_llama3" ]; then
    docker::save_as_tar "vllm-llama3.2-nvfp4:local" "vllm-llama3.2-nvfp4.tar"
fi
