## 2026-03-26 - Chat Interface Re-renders with Active Indicators
**Learning:** In chat interfaces, maintaining state for "active" typing indicators or pipeline processing steps at the `MessageList` level causes all previous static messages to re-render continuously. This is an O(N) operation where N grows linearly with chat history, resulting in a noticeable performance bottleneck over long sessions.
**Action:** Always wrap immutable list items (like historical `MessageBubble` components) in `React.memo` when rendering them alongside frequently updating state items (like typing indicators or progress bars).

## 2024-05-24 - React Component Array Re-renders with Unoptimized `.find()`
**Learning:** Rendering a list of items using `.map()` and calling `.find()` on multiple arrays for each item creates an O(N*M) operation on every re-render. In scenarios like `MessageBubble.tsx` where an active pipeline indicator frequently triggers re-renders, this severely degrades performance.
**Action:** Pre-compute lookup maps (dictionaries) using `useMemo` outside the mapping loop. Change $O(M)$ array lookups with `.find()` to $O(1)$ dictionary lookups with `Map.get()`, reducing overall complexity to O(N).
