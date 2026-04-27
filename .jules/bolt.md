## 2026-03-26 - Chat Interface Re-renders with Active Indicators
**Learning:** In chat interfaces, maintaining state for "active" typing indicators or pipeline processing steps at the `MessageList` level causes all previous static messages to re-render continuously. This is an O(N) operation where N grows linearly with chat history, resulting in a noticeable performance bottleneck over long sessions.
**Action:** Always wrap immutable list items (like historical `MessageBubble` components) in `React.memo` when rendering them alongside frequently updating state items (like typing indicators or progress bars).

## 2026-03-27 - Frontend Property Iteration Bottleneck
**Learning:** When rendering chat messages that contain multiple properties and their associated analyses, using `.find()` inside a `.map()` loop creates an O(N * M) performance bottleneck (N properties * M analysis entries). In React, this runs on every render of the component. Similarly, instantiating `Intl.NumberFormat` inside the render function of the property card introduces unnecessary overhead on every render, which gets magnified by the number of properties displayed.
**Action:** Extract expensive instantiations (like `Intl.NumberFormat`) outside of React component render functions. Always replace O(N²) nested array `.find()` lookups within `.map()` loops with O(N) `Map` lookups created beforehand.

## 2026-03-27 - Vectorized Cosine Similarity
**Learning:** In the backend, vectorizing cosine similarity calculations in `SemanticRouter` using NumPy matrix-vector multiplication (`np.dot` with a 2D `embeddings_matrix` stacked from 1D vectors) and `np.partition` for top-K extraction significantly improves performance over Python list comprehensions and full sorting.
**Action:** When calculating similarities against multiple examples, stack vectors into a matrix and use `np.dot(matrix, vector)` instead of a loop. Use `np.partition(array, -k)[-k:]` instead of sorting when only the top-K unordered elements are needed.
