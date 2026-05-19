## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2026-05-19 - Fix Insecure Direct Object Reference (IDOR) in /api/sessions endpoint
**Vulnerability:** The API endpoint to list user sessions used `get_system_client()`, which has `service_role` privileges and bypasses Row Level Security (RLS). Furthermore, it accepted a `user_id` parameter without verifying if the user requesting the data was actually the owner of that `user_id`, leading to an IDOR vulnerability where any user could fetch any other user's sessions.
**Learning:** Endpoints returning user-specific data must never use the system client as it breaks the backend security posture where data segregation relies heavily on database RLS policies.
**Prevention:** Always extract the user's JWT from the `Authorization` header and instantiate the database client using `get_user_client(user_jwt)`. This ensures that all database queries are constrained by the Supabase RLS policies tied to the authenticated user.
