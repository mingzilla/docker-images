FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Set PYTHONPATH so imports work without src. prefix
ENV PYTHONPATH=/app/src

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py ./
COPY benchmark.py ./

# Copy src directory for batch embedding functionality
COPY src/ /app/src/

EXPOSE 8000

# Download and cache the model during build time
RUN python -c "from sentence_transformers import SentenceTransformer; print('Downloading model...'); model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); print('Model cached successfully')"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]