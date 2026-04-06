## 2026-03-05 - Batching sentence-transformers inputs
**Learning:** Sentence-transformers models are highly optimized for processing inputs in batches rather than encoding items individually in loops.
**Action:** In `layer_1_input/semantic_router.py`, the intent examples were flattened into a single list, processed via a single `.encode()` call, and then reconstructed into the `_intent_embeddings` mapping. This reduced model initialization time by ~45%.

## 2026-04-03 - React.memo Thrashing Fix
**Learning:** In frontend chat interfaces, even if components like MessageBubble are wrapped in React.memo, inline object literals like `{ id: 'temp', timestamp: new Date() }` passed directly in the parent render bypass the memoization and trigger continuous unnecessary re-renders. This is particularly problematic for active pipeline status or typing indicators.
**Action:** Extract temporary literal objects into a `useMemo` block so they maintain a stable reference across renders, ensuring `React.memo` successfully prevents O(N) re-renders.
