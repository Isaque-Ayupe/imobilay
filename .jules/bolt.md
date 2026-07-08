## 2026-03-26 - Chat Interface Re-renders with Active Indicators
**Learning:** In chat interfaces, maintaining state for "active" typing indicators or pipeline processing steps at the `MessageList` level causes all previous static messages to re-render continuously. This is an O(N) operation where N grows linearly with chat history, resulting in a noticeable performance bottleneck over long sessions.
**Action:** Always wrap immutable list items (like historical `MessageBubble` components) in `React.memo` when rendering them alongside frequently updating state items (like typing indicators or progress bars).

## 2026-03-27 - Frontend Property Iteration Bottleneck
**Learning:** When rendering chat messages that contain multiple properties and their associated analyses, using `.find()` inside a `.map()` loop creates an O(N * M) performance bottleneck (N properties * M analysis entries). In React, this runs on every render of the component. Similarly, instantiating `Intl.NumberFormat` inside the render function of the property card introduces unnecessary overhead on every render, which gets magnified by the number of properties displayed.
**Action:** Extract expensive instantiations (like `Intl.NumberFormat`) outside of React component render functions. Always replace O(N²) nested array `.find()` lookups within `.map()` loops with O(N) `Map` lookups created beforehand.

## 2026-07-08 - Extract Date Calculations from Loops
**Learning:** Extract invariant function outputs, such as current date calculations (e.g., `datetime.now().date()`), outside of iterative loops. Calling `datetime.now().date()` multiple times per iteration introduces unnecessary O(N) system call overhead, whereas pre-computing it once reduces the cost to O(1). Additionally, this prevents subtle edge-case bugs caused by time ticking over (e.g., crossing the midnight boundary) during loop execution.
**Action:** Always extract invariant data processing operations, such as dynamic calculations of the current date, outside of request loops and parsing functions to module-level or function-level pre-computed constants to avoid repeated processing overhead on every execution.
