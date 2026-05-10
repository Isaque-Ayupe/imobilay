## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2024-05-10 - Prevent IDOR in API Endpoints
**Vulnerability:** The `list_sessions` API endpoint in `api.py` was vulnerable to Insecure Direct Object Reference (IDOR). It used the `get_system_client()` (which relies on the `service_role` key and bypasses RLS) to query the Supabase database. This allowed any user to fetch another user's sessions by simply providing their `user_id`.
**Learning:** In the backend, passing a user-provided identifier (like `user_id`) to a database query running with admin privileges bypasses Row-Level Security (RLS). Endpoints returning user-specific data must extract the user's JWT from the request.
**Prevention:** Always require an `Authorization` header on endpoints serving user-specific data. Extract the JWT and instantiate the database client using `get_user_client(user_jwt)` rather than `get_system_client()`. This ensures the queries are executed within the user's context and RLS policies are strictly enforced by the database.
