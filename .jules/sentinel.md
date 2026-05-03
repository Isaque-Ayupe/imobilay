## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2024-05-16 - Fix IDOR Vulnerability in /api/sessions
**Vulnerability:** The `/api/sessions` endpoint accepted a `user_id` parameter and fetched the user's sessions using `get_system_client()`. This bypassed Row Level Security (RLS) and created an Insecure Direct Object Reference (IDOR) vulnerability where any user could fetch any other user's sessions simply by knowing their ID.
**Learning:** Endpoints returning user-specific data must extract the user's JWT from the `Authorization` header and instantiate the database client using `get_user_client(user_jwt)` rather than `get_system_client()`.
**Prevention:** To properly enforce Supabase Row-Level Security (RLS) policies and prevent Insecure Direct Object Reference (IDOR) vulnerabilities, backend endpoints returning user-specific data must require an `Authorization` header containing a JWT token, and use `get_user_client(user_jwt)` instead of `get_system_client()` so that Supabase RLS policies are properly enforced.
