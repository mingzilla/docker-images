FROM vllm/vllm-openai:v0.16.0

# Install HuggingFace tools
RUN pip install --no-cache-dir huggingface-hub hf-transfer

# Set environment
ENV HF_HOME=/app/models

# Create model directory
WORKDIR /app/models

# Download model
RUN python3 -c "from huggingface_hub import snapshot_download; snapshot_download('Firworks/Ministral-3-3B-Instruct-2512-nvfp4', local_dir='/app/models/Ministral-3-3B-Instruct-2512-nvfp4', local_dir_use_symlinks=False)"

# Expose port
EXPOSE 8000

WORKDIR /app

ENV MAX_MODEL_LEN=8192
ENV GPU_MEMORY_UTILIZATION=0.90

ENTRYPOINT []
CMD vllm serve /app/models/Ministral-3-3B-Instruct-2512-nvfp4 \
    --served-model-name Firworks/Ministral-3-3B-Instruct-2512-nvfp4 \
    --dtype auto \
    --max-model-len ${MAX_MODEL_LEN} \
    --gpu-memory-utilization ${GPU_MEMORY_UTILIZATION} \
    --host 0.0.0.0 \
    --port 8000
