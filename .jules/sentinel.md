## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.
## 2024-05-30 - Fix IDOR in list_sessions Endpoint
**Vulnerability:** The `list_sessions` endpoint was using `get_system_client()`, which uses a service role key that bypasses Row-Level Security (RLS) in Supabase. This creates an Insecure Direct Object Reference (IDOR) vulnerability, as users could potentially fetch sessions for any user ID.
**Learning:** Never use `get_system_client()` in user-facing API endpoints that return user-specific data. Using `get_system_client()` ignores user boundaries enforced by database policies.
**Prevention:** Always extract the user's JWT from the `Authorization` header and use `get_user_client(user_jwt)` to ensure database queries respect the authenticated user's RLS policies.
