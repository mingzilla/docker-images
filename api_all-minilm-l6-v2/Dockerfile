FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
# Install CPU-only PyTorch first for smaller image size
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

EXPOSE 8000

# Download and cache the model during build time
RUN python -c "from sentence_transformers import SentenceTransformer; print('Downloading model...'); model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); print('Model cached successfully')"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]