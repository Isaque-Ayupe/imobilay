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
        # The optimized logic
        intent_embeddings = {}

        # Flatten all examples into a single list
        all_intents = []
        all_examples = []
        counts = []
        for intent_name, examples in examples_by_intent.items():
            all_intents.append(intent_name)
            all_examples.extend(examples)
            counts.append(len(examples))

        # Encode all examples in one batch
        embeddings = pre_loaded_model.encode(all_examples)

        # Reshape and normalize
        idx = 0
        for i, intent_name in enumerate(all_intents):
            count = counts[i]
            intent_emb = embeddings[idx:idx+count]
            intent_embeddings[intent_name] = [
                emb / __import__('numpy').linalg.norm(emb) for emb in intent_emb
            ]
            idx += count

    duration = time.time() - start
    print(f"OPTIMIZED: Time taken for 500 initializations (encoding only): {duration:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
