## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2026-06-19 - Supabase Database Client Usage Vulnerability (IDOR)
**Vulnerability:** The API endpoint `list_sessions` previously used `get_system_client()` (which uses a service_role key to bypass Row-Level Security) to fetch user-specific sessions. This presented a high-risk IDOR (Insecure Direct Object Reference) vulnerability because any user could specify another user's `user_id` and gain access to their sessions without verifying authorization.
**Learning:** `get_system_client()` bypasses Row-Level Security (RLS) and is intended solely for internal pipeline agents that perform cross-user data operations. It should never be exposed in a frontend-facing API where a user accesses only their own private data.
**Prevention:** To prevent IDOR vulnerabilities in frontend endpoints that return user-specific data, the endpoint must extract the user's JWT from the `Authorization` header and pass it to `get_user_client(user_jwt)`. This enforces Row-Level Security directly on the database query.
