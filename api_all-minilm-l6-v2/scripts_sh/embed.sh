#!/bin/bash

set -e

export IMAGE_NAME=api_all-minilm-l6-v2:latest
export WORK_DIR=$(pwd)

docker run --rm --gpus all -v $WORK_DIR:/app/data $IMAGE_NAME python -m embed
