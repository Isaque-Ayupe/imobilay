## 2026-03-26 - Chat Interface Re-renders with Active Indicators
**Learning:** In chat interfaces, maintaining state for "active" typing indicators or pipeline processing steps at the `MessageList` level causes all previous static messages to re-render continuously. This is an O(N) operation where N grows linearly with chat history, resulting in a noticeable performance bottleneck over long sessions.
**Action:** Always wrap immutable list items (like historical `MessageBubble` components) in `React.memo` when rendering them alongside frequently updating state items (like typing indicators or progress bars).

## 2026-03-27 - Frontend Property Iteration Bottleneck
**Learning:** When rendering chat messages that contain multiple properties and their associated analyses, using `.find()` inside a `.map()` loop creates an O(N * M) performance bottleneck (N properties * M analysis entries). In React, this runs on every render of the component. Similarly, instantiating `Intl.NumberFormat` inside the render function of the property card introduces unnecessary overhead on every render, which gets magnified by the number of properties displayed.
**Action:** Extract expensive instantiations (like `Intl.NumberFormat`) outside of React component render functions. Always replace O(N²) nested array `.find()` lookups within `.map()` loops with O(N) `Map` lookups created beforehand.

## 2024-05-06 - Vectorizing SemanticRouter embedding similarity calculation
**Learning:** Python list comprehensions with individual `np.dot` calls in a loop are significantly slower than a single `np.dot` matrix-vector multiplication in C when evaluating cosine similarity across all intent embeddings. Also, for finding top-k items in a numpy array, `np.partition` is O(N) compared to `sorted()` which is O(N log N).
**Action:** When computing similarity scores across multiple categories or intents, stack all vector examples into a single 2D matrix during initialization. Use a single matrix multiplication and `np.partition` for retrieval, then use slices to separate the results back into logical groups.
