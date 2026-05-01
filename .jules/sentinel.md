## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2026-05-01 - IDOR Vulnerability in Sessions Endpoint
**Vulnerability:** The `/api/sessions` endpoint used `get_system_client()` to retrieve user sessions based on the `user_id` query parameter without checking the caller's identity. Since `get_system_client()` bypasses Row-Level Security (RLS), any authenticated or unauthenticated user could read any other user's sessions by guessing their UUID.
**Learning:** Using a system-level database client with `service_role` keys in user-facing data retrieval endpoints causes critical Insecure Direct Object Reference (IDOR) vulnerabilities, as the database relies on RLS to enforce access control.
**Prevention:** Always extract the user's JWT from the `Authorization` header and instantiate a user-specific database client using `get_user_client(token)`. This ensures that RLS policies are strictly evaluated and users can only access their own data.
