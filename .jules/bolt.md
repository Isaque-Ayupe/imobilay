## 2026-03-26 - Chat Interface Re-renders with Active Indicators
**Learning:** In chat interfaces, maintaining state for "active" typing indicators or pipeline processing steps at the `MessageList` level causes all previous static messages to re-render continuously. This is an O(N) operation where N grows linearly with chat history, resulting in a noticeable performance bottleneck over long sessions.
**Action:** Always wrap immutable list items (like historical `MessageBubble` components) in `React.memo` when rendering them alongside frequently updating state items (like typing indicators or progress bars).

## 2026-03-27 - Frontend Property Iteration Bottleneck
**Learning:** When rendering chat messages that contain multiple properties and their associated analyses, using `.find()` inside a `.map()` loop creates an O(N * M) performance bottleneck (N properties * M analysis entries). In React, this runs on every render of the component. Similarly, instantiating `Intl.NumberFormat` inside the render function of the property card introduces unnecessary overhead on every render, which gets magnified by the number of properties displayed.
**Action:** Extract expensive instantiations (like `Intl.NumberFormat`) outside of React component render functions. Always replace O(N²) nested array `.find()` lookups within `.map()` loops with O(N) `Map` lookups created beforehand.

## 2026-03-28 - Unstable Dependencies in useCallback Re-rendering Memoized Components
**Learning:** When a `useCallback` hook depends on an unstable object like the full state of a complex hook (e.g. `pipeline` which changes on every step), the callback gets recreated continuously. If this callback is passed to a child component wrapped in `React.memo` (like `ChatInput`), the memoization is defeated and the child re-renders completely unnecessarily.
**Action:** Destructure stable functions from complex hook states (like `startPipeline`) and only use these stable functions in the `useCallback` dependency array. This ensures the callback remains stable across state updates and preserves the performance benefits of `React.memo` in child components.
