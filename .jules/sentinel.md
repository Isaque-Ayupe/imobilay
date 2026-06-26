## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2026-06-26 - Fix IDOR Vulnerability in Frontend-Facing API Endpoint
**Vulnerability:** The `/api/sessions` endpoint used the `get_system_client()` Supabase client, which bypasses Row Level Security (RLS). This allowed any user to potentially access session data of other users by simply querying the endpoint with a different `user_id`.
**Learning:** `get_system_client()` is meant strictly for internal agents or services requiring full access, not for endpoints accessed by end-users. Using it directly on frontend-facing endpoints creates Insecure Direct Object Reference (IDOR) vulnerabilities since it bypasses RLS protections.
**Prevention:** Always enforce RLS for user-facing API endpoints by validating the `Authorization` header and utilizing `get_user_client(user_jwt)`. This ensures that all database interactions occur securely within the authenticated user's context.
