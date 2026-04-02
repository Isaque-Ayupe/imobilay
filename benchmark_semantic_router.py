import asyncio
import time
from sentence_transformers import SentenceTransformer
import layer_1_input.semantic_router

async def run_benchmark():
    # Pre-load model to avoid measuring load time
    pre_loaded_model = SentenceTransformer(layer_1_input.semantic_router.MODEL_NAME)

    # Mock initialization logic manually to only test the specific encoding block
    examples_by_intent = layer_1_input.semantic_router.DEFAULT_INTENT_EXAMPLES

    start = time.time()
    for _ in range(500):
        # The logic we are optimizing
        intent_embeddings = {}
        for intent_name, examples in examples_by_intent.items():
            embeddings = pre_loaded_model.encode(examples)
            intent_embeddings[intent_name] = [
                emb / __import__('numpy').linalg.norm(emb) for emb in embeddings
            ]
    duration = time.time() - start
    print(f"BASELINE: Time taken for 500 initializations (encoding only): {duration:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
