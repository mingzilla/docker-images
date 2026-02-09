FROM nvcr.io/nvidia/pytorch:25.02-py3

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    ccache \
    cmake \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

# Install HuggingFace tools
RUN pip install --no-cache-dir huggingface-hub hf-transfer

# Set Blackwell environment
ENV TORCH_CUDA_ARCH_LIST=12.0
ENV VLLM_FLASH_ATTN_VERSION=2
ENV CUDA_HOME=/usr/local/cuda
ENV PATH="/usr/local/bin:$CUDA_HOME/bin:$PATH"
ENV HF_HOME=/app/models

# Create model directory
WORKDIR /app/models

# Download Qwen2.5 model
RUN python3 -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen2.5-32B-Instruct-NVFP4', local_dir='/app/models/Qwen2.5-32B-Instruct-NVFP4', local_dir_use_symlinks=False)"

# Build vLLM v0.15.1 from source
WORKDIR /workspace
RUN git clone --branch v0.15.1 --depth 1 https://github.com/vllm-project/vllm.git && \
    cd vllm && \
    pip install -r requirements/build.txt && \
    pip install setuptools_scm && \
    MAX_JOBS=4 pip install -e . --no-build-isolation

# Clean up
RUN rm -rf /root/.cache/pip /workspace/vllm/build /tmp/*

# Expose port
EXPOSE 8000

WORKDIR /app

CMD ["vllm", "serve", "/app/models/Qwen2.5-32B-Instruct-NVFP4", \
     "--quantization", "nvfp4", \
     "--dtype", "auto", \
     "--max-model-len", "8192", \
     "--gpu-memory-utilization", "0.99", \
     "--host", "0.0.0.0", \
     "--port", "8000"]