
import time
import torch
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def run_benchmark(batch_size: int):
    """
    Benchmarks the sentence-transformers library for a given batch size.
    """
    print(f"\n--- Running benchmark for batch size: {batch_size} ---")

    # 1. Load model (it will be cached after the first run)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(MODEL_NAME, device=device)
    print(f"Model is on: {device}")

    # 2. Create a dummy dataset
    texts = ["This is a sample sentence for benchmarking."] * batch_size

    # 3. Run the encoding and time it
    start_time = time.time()
    embeddings = model.encode(texts, convert_to_tensor=False, normalize_embeddings=True)
    end_time = time.time()

    duration = end_time - start_time
    items_per_second = batch_size / duration

    print(f"Processed {batch_size} items in {duration:.3f} seconds.")
    print(f"Throughput: {items_per_second:.2f} items/second")
    return items_per_second

def main():
    """
    Runs benchmarks for different batch sizes to find the sweet spot.
    """
    print("Starting benchmark to isolate embedding performance from API overhead...")
    
    batch_sizes = [5000, 10000, 15000, 20000, 25000, 30000]
    results = {}

    for size in batch_sizes:
        try:
            throughput = run_benchmark(size)
            results[size] = throughput
        except torch.cuda.OutOfMemoryError:
            print(f"CUDA out of memory at batch size {size}. Stopping benchmark.")
            break
        except Exception as e:
            print(f"An error occurred at batch size {size}: {e}")
            break

    print("\n--- Benchmark Summary ---")
    for size, throughput in results.items():
        print(f"Batch Size: {size:<8} Throughput: {throughput:.2f} items/s")
    print("\nBenchmark finished.")
    print("This shows the performance of the model without any API overhead.")
    print("If this scales better than your API calls, the bottleneck is in the API layer (JSON handling).")

if __name__ == "__main__":
    main()
