#!/bin/bash

echo "--- Starting Docker container in background ---"
docker-compose up -d

echo "--- Running benchmark script inside the container ---"
docker exec -it api_all-minilm-l6-v2 python benchmark.py
