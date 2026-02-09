FROM vllm/vllm-openai:v0.6.6

# Install any additional dependencies if needed
RUN pip install --no-cache-dir hf-transfer

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

# Expose port
EXPOSE 8000

# Default command
CMD ["vllm", "serve", "Qwen2.5-32B-Instruct-NVFP4", \
     "--quantization", "nvfp4", \
     "--dtype", "auto", \
     "--max-model-len", "8192", \
     "--gpu-memory-utilization", "0.99", \
     "--host", "0.0.0.0", \
     "--port", "8000"]