## 2026-03-26 - Chat Interface Re-renders with Active Indicators
**Learning:** In chat interfaces, maintaining state for "active" typing indicators or pipeline processing steps at the `MessageList` level causes all previous static messages to re-render continuously. This is an O(N) operation where N grows linearly with chat history, resulting in a noticeable performance bottleneck over long sessions.
**Action:** Always wrap immutable list items (like historical `MessageBubble` components) in `React.memo` when rendering them alongside frequently updating state items (like typing indicators or progress bars).

## 2026-03-27 - Frontend Property Iteration Bottleneck
**Learning:** When rendering chat messages that contain multiple properties and their associated analyses, using `.find()` inside a `.map()` loop creates an O(N * M) performance bottleneck (N properties * M analysis entries). In React, this runs on every render of the component. Similarly, instantiating `Intl.NumberFormat` inside the render function of the property card introduces unnecessary overhead on every render, which gets magnified by the number of properties displayed.
**Action:** Extract expensive instantiations (like `Intl.NumberFormat`) outside of React component render functions. Always replace O(N²) nested array `.find()` lookups within `.map()` loops with O(N) `Map` lookups created beforehand.

## 2026-04-03 - Vectorized Cosine Similarity in SemanticRouter
**Learning:** In the backend, using list comprehensions with individual `np.dot` operations to calculate similarities between a message embedding and stored intent embeddings introduces significant overhead due to Python loop execution and function call overhead.
**Action:** Always vectorize cosine similarity calculations in `SemanticRouter` using NumPy matrix-vector multiplication (`np.dot` with a 2D `embeddings_matrix`). Furthermore, use `np.partition` instead of fully sorting arrays for top-K extraction, resulting in substantial (~10x) performance improvements over O(N log N) sorting.
