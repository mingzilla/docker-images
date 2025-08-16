import logging
import time
from typing import List, Union, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
import torch
import tiktoken

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
model = None
tokenizer = None

class OpenAIEmbeddingRequest(BaseModel):
    model: str
    input: Union[str, List[str]]
    encoding_format: Optional[str] = "float"
    dimensions: Optional[int] = None
    user: Optional[str] = None

class OpenAIEmbeddingData(BaseModel):
    object: str = "embedding"
    embedding: List[float]
    index: int

class OpenAIUsage(BaseModel):
    prompt_tokens: int
    total_tokens: int

class OpenAIEmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[OpenAIEmbeddingData]
    model: str
    usage: OpenAIUsage

class OllamaEmbedRequest(BaseModel):
    model: str
    input: Union[str, List[str]]
    truncate: Optional[bool] = True
    options: Optional[dict] = None
    keep_alive: Optional[str] = "5m"

class OllamaEmbedResponse(BaseModel):
    model: str
    embeddings: List[List[float]]

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "sentence-transformers"

class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]

def estimate_tokens(text: str) -> int:
    try:
        if tokenizer:
            return len(tokenizer.encode(text))
        else:
            return len(text.split())
    except:
        return len(text.split())

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, tokenizer
    logger.info("Loading sentence-transformers model...")
    
    try:
        model = SentenceTransformer(MODEL_NAME)
        logger.info(f"Model loaded successfully on CPU")
        
        try:
            tokenizer = tiktoken.get_encoding("cl100k_base")
        except:
            logger.warning("Could not load tiktoken tokenizer, using simple word counting")
            tokenizer = None
            
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise
    
    yield
    
    logger.info("Shutting down...")

app = FastAPI(
    title="all-MiniLM-L6-v2 Embedding API",
    description="OpenAI-compatible embedding API using sentence-transformers/all-MiniLM-L6-v2",
    version="1.0.1",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.get("/v1/models")
async def list_models():
    return ModelsResponse(
        data=[
            ModelInfo(
                id="all-MiniLM-L6-v2",
                created=int(time.time())
            )
        ]
    )

@app.post("/v1/embeddings", response_model=OpenAIEmbeddingResponse)
async def create_embeddings(request: OpenAIEmbeddingRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        if isinstance(request.input, str):
            texts = [request.input]
        else:
            texts = request.input
        
        embeddings = model.encode(texts, convert_to_tensor=False, normalize_embeddings=True)
        
        if len(embeddings.shape) == 1:
            embeddings = [embeddings.tolist()]
        else:
            embeddings = embeddings.tolist()
        
        total_tokens = sum(estimate_tokens(text) for text in texts)
        
        data = [
            OpenAIEmbeddingData(
                embedding=embedding,
                index=i
            )
            for i, embedding in enumerate(embeddings)
        ]
        
        return OpenAIEmbeddingResponse(
            data=data,
            model="all-MiniLM-L6-v2",
            usage=OpenAIUsage(
                prompt_tokens=total_tokens,
                total_tokens=total_tokens
            )
        )
        
    except Exception as e:
        logger.error(f"Error creating embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/embed", response_model=OllamaEmbedResponse)
async def ollama_embed(request: OllamaEmbedRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        if isinstance(request.input, str):
            texts = [request.input]
        else:
            texts = request.input
        
        embeddings = model.encode(texts, convert_to_tensor=False, normalize_embeddings=True)
        
        if len(embeddings.shape) == 1:
            embeddings = [embeddings.tolist()]
        else:
            embeddings = embeddings.tolist()
        
        return OllamaEmbedResponse(
            model="all-MiniLM-L6-v2",
            embeddings=embeddings
        )
        
    except Exception as e:
        logger.error(f"Error creating embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)