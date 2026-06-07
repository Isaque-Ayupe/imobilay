## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2024-06-07 - IDOR in User Sessions Endpoint
**Vulnerability:** The `/api/sessions` endpoint used the bypass-RLS `get_system_client()` without verifying the user's authorization, allowing any user to fetch another user's sessions simply by knowing their `user_id`.
**Learning:** Backend endpoints returning user-specific data must extract the user's JWT from the `Authorization` header and instantiate the database client using `get_user_client(user_jwt)` to properly enforce Supabase Row-Level Security (RLS) policies.
**Prevention:** Always require and validate an authorization header containing the user's JWT when fetching user-specific records. Avoid using `get_system_client()` for frontend-facing data retrieval endpoints.
