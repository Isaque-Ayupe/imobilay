import mock_setup
import asyncio
import time
from sentence_transformers import SentenceTransformer
import layer_1_input.semantic_router
import numpy as np

async def run_benchmark():
    # Pre-load model to avoid measuring load time
    pre_loaded_model = SentenceTransformer(layer_1_input.semantic_router.MODEL_NAME)

    # Mock initialization logic manually to only test the specific encoding block
    examples_by_intent = layer_1_input.semantic_router.DEFAULT_INTENT_EXAMPLES

    intent_embeddings = {}
    for intent_name, examples in examples_by_intent.items():
        embeddings = pre_loaded_model.encode(examples)
        intent_embeddings[intent_name] = [
            emb / np.linalg.norm(emb) for emb in embeddings
        ]

    msg_embedding = pre_loaded_model.encode(["quero investir em um apartamento"])[0]
    msg_embedding = msg_embedding / np.linalg.norm(msg_embedding)

    start = time.time()
    for _ in range(5000):
        # The logic we are optimizing
        raw_scores = {}
        for intent_name, embeddings in intent_embeddings.items():
            similarities = [
                float(np.dot(msg_embedding, emb))
                for emb in embeddings
            ]
            # Top-3 para robustez (menos sensível a outliers)
            top_k = sorted(similarities, reverse=True)[:3]
            raw_scores[intent_name] = sum(top_k) / len(top_k)

    duration = time.time() - start
    print(f"BASELINE: Time taken for 5000 routings: {duration:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
