## 2026-03-26 - Chat Interface Re-renders with Active Indicators
**Learning:** In chat interfaces, maintaining state for "active" typing indicators or pipeline processing steps at the `MessageList` level causes all previous static messages to re-render continuously. This is an O(N) operation where N grows linearly with chat history, resulting in a noticeable performance bottleneck over long sessions.
**Action:** Always wrap immutable list items (like historical `MessageBubble` components) in `React.memo` when rendering them alongside frequently updating state items (like typing indicators or progress bars).

## 2026-03-27 - Frontend Property Iteration Bottleneck
**Learning:** When rendering chat messages that contain multiple properties and their associated analyses, using `.find()` inside a `.map()` loop creates an O(N * M) performance bottleneck (N properties * M analysis entries). In React, this runs on every render of the component. Similarly, instantiating `Intl.NumberFormat` inside the render function of the property card introduces unnecessary overhead on every render, which gets magnified by the number of properties displayed.
**Action:** Extract expensive instantiations (like `Intl.NumberFormat`) outside of React component render functions. Always replace O(N²) nested array `.find()` lookups within `.map()` loops with O(N) `Map` lookups created beforehand.

## 2026-03-27 - WebScraper I/O Parallelization
**Learning:** In the WebScraperAgent, independent network requests to different property portals (e.g., ZAP and VivaReal) were being awaited sequentially (`await _fetch_zap` then `await _fetch_vivareal`). This caused the total agent execution time to be the sum of both network latencies, creating an unnecessary performance bottleneck for I/O-bound operations.
**Action:** Always use `asyncio.gather()` to execute independent I/O-bound coroutines concurrently (e.g., `await asyncio.gather(fetch_zap(), fetch_vivareal())`). This reduces the total execution time to the duration of the slowest single request.
