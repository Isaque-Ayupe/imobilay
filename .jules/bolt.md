## 2026-03-26 - Chat Interface Re-renders with Active Indicators
**Learning:** In chat interfaces, maintaining state for "active" typing indicators or pipeline processing steps at the `MessageList` level causes all previous static messages to re-render continuously. This is an O(N) operation where N grows linearly with chat history, resulting in a noticeable performance bottleneck over long sessions.
**Action:** Always wrap immutable list items (like historical `MessageBubble` components) in `React.memo` when rendering them alongside frequently updating state items (like typing indicators or progress bars).

## 2026-03-27 - Frontend Property Iteration Bottleneck
**Learning:** When rendering chat messages that contain multiple properties and their associated analyses, using `.find()` inside a `.map()` loop creates an O(N * M) performance bottleneck (N properties * M analysis entries). In React, this runs on every render of the component. Similarly, instantiating `Intl.NumberFormat` inside the render function of the property card introduces unnecessary overhead on every render, which gets magnified by the number of properties displayed.
**Action:** Extract expensive instantiations (like `Intl.NumberFormat`) outside of React component render functions. Always replace O(N²) nested array `.find()` lookups within `.map()` loops with O(N) `Map` lookups created beforehand.

## 2024-05-09 - Vectorized Semantic Routing with NumPy
**Learning:** Python list comprehensions and iterative inner product calculations (like `[np.dot(a, b) for a in list_of_arrays]`) are significantly slower than true vectorized matrix operations (`np.dot(matrix, vector)`). Furthermore, extracting the top-K elements using `sorted()[:K]` is O(N log N) which is computationally wasteful when N is large and K is small.
**Action:** Always pre-stack arrays into a single NumPy matrix (`np.stack`) during initialization if they are going to be repeatedly evaluated via dot product against a single vector. Use `np.partition(array, -k)[-k:]` to extract the top-K elements in O(N) time instead of sorting the whole array.
