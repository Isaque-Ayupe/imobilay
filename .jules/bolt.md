## 2026-03-26 - Chat Interface Re-renders with Active Indicators
**Learning:** In chat interfaces, maintaining state for "active" typing indicators or pipeline processing steps at the `MessageList` level causes all previous static messages to re-render continuously. This is an O(N) operation where N grows linearly with chat history, resulting in a noticeable performance bottleneck over long sessions.
**Action:** Always wrap immutable list items (like historical `MessageBubble` components) in `React.memo` when rendering them alongside frequently updating state items (like typing indicators or progress bars).

## 2026-05-01 - Semantic Router Matrix Vectorization
**Learning:** In the backend `SemanticRouter`, using Python list comprehensions and iterative per-intent vector dot products to calculate cosine similarities is a performance bottleneck. Computing similarities sequentially in Python prevents taking advantage of highly optimized C-level math libraries.
**Action:** Vectorizing cosine similarity calculations using NumPy matrix-vector multiplication (`np.dot` with a single 2D `_all_embeddings_matrix` stacked across all intents and an `_intent_indices` mask) significantly improves performance. Additionally, replacing $O(N \log N)$ full sorts with $O(N)$ `np.partition` for top-K extraction provides further speedup.
