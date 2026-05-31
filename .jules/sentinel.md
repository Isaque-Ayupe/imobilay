## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.
## 2025-05-31 - Fix Insecure Direct Object Reference (IDOR) and RLS Bypass in `/api/sessions`
**Vulnerability:** The `/api/sessions` endpoint used a `user_id` query parameter and instantiated the Supabase client via `get_system_client()`, which uses a service role key that bypasses Row-Level Security (RLS). This allowed any authenticated (or unauthenticated) user to query the chat sessions of any arbitrary `user_id`.
**Learning:** Instantiating the database client with system-level privileges bypasses RLS policies. It's critical to tie data-fetching logic explicitly to user credentials.
**Prevention:** Always extract user identity via authentication mechanisms (like a JWT in the `Authorization` header), and instantiate the user-context database client `get_user_client(jwt)` for operations tied to specific users, enabling proper RLS enforcement.
