# Embedding Model Evaluation

The goal is to find a suitable model to create embeddings for short descriptions to power semantic search and similarity matching.

Typical Use Case:

- summarise short paragraphs, or e.g. database column descriptions (e.g., `"Email - contact email address..."`)
- speed is a key consideration factor
- small dimension count is ideal

## 1. Model Comparison Table

| **Model**                | **all-MiniLM-L6-v2**                                                         | **nomic-embed-text-v1**                                             | **EmbeddingGemma**                                                         |
|:-------------------------|:-----------------------------------------------------------------------------|:--------------------------------------------------------------------|:---------------------------------------------------------------------------|
| **Architecture & Size**  | 6-layer MiniLM, 22.7M params, 384-dim embeddings                             | BERT-based, 235M params, 768-dim embeddings                         | Gemma 3-based, 308M params, 768-dim (flexible down to 128)                 |
| **Accuracy**             | Good for general semantic similarity, may struggle with nuanced distinctions | Better accuracy than MiniLM (e.g., ~81.2% vs. ~80.04% on Banking77) | **State-of-the-art for its size**, outperforms larger models on some tasks |
| **Speed & Efficiency**   | **Very fast** (~14.7 ms/1K tokens), ideal for high-throughput applications   | Slower than MiniLM (~206 sec/1M tokens)                             | Optimized for on-device use, <22ms latency on EdgeTPU                      |
| **Context Length**       | 256 word pieces (truncates longer text)                                      | 2048 tokens                                                         | 2048 tokens                                                                |
| **Multilingual Support** | Limited to English                                                           | Supports multiple languages                                         | **Supports 100+ languages**                                                |
| **Customization**        | Can be fine-tuned but limited by size                                        | Supports task-specific prefixes (e.g., `search_query:`)             | **Matryoshka Learning**: Embedding size customizable (768 to 128)          |
| **Ideal Use Case**       | High-speed, low-resource environments with simple semantic matching          | General-purpose retrieval with better accuracy than MiniLM          | **On-device or multilingual applications** requiring high quality          |

**Verdict:**

- **EmbeddingGemma is likely the most powerful and flexible choice** for such use case (officially available on ollama)
- `all-MiniLM-L6-v2` remains a good option if pure speed is your top priority (no official model on ollama, custom docker may not use GPU)

## 2. How to Scale EmbeddingGemma to 128 Dimensions

You scale it down by **truncating the embedding vector**. The model is trained using **Matryoshka Representation Learning (MRL)**, which means the most important information is stored in the first dimensions.

* **Process:** Generate the full 768-dimensional vector, then simply **"chop off" everything from dimension 129 onward**.
* **Code Example:**
  ```python
  from sentence_transformers import SentenceTransformer
  model = SentenceTransformer("google/embeddinggemma-300m")
  full_embedding = model.encode("AddressLine1 - primary residential address")
  truncated_128d_embedding = full_embedding[:128]  # Keep only the first 128 dimensions
  ```

## 3. What You Lose by Scaling Down

By truncating to 128 dimensions, you sacrifice **~5% in accuracy** on standard benchmarks for a **6x reduction in storage and memory usage**.

* **Why it works:** The first 128 dimensions contain the "executive summary" – the core semantic meaning. This is often sufficient to tell the difference between a `"city name"` and an `"email address"`.
* **What you lose:** The finer-grained details in the later dimensions that help make **subtle distinctions** (e.g., between `"work email"` and `"personal email"`). You trade **nuance for efficiency**.

## 4. Context Length & Suitability

* **Context Length (2048 tokens):** Scaling the embedding dimensions down **has no effect** on the context length. You can still process text inputs up to **2048 tokens** long, even when outputting a 128-dimensional vector.
* **Suitability for Your Task:** For embedding database column descriptions, which are short text strings, **the 128-dimensional version of EmbeddingGemma is an excellent choice**. It offers a great balance of high efficiency and strong performance for this specific use case.