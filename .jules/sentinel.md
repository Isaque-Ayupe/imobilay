## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2026-03-26 - Insecure Direct Object Reference (IDOR) via system client usage
**Vulnerability:** The API endpoint `list_sessions` directly used `get_system_client()` with a user-provided `user_id` without verifying the caller's authorization. This enabled an attacker to fetch any user's session simply by providing their `user_id`.
**Learning:** Bypassing Supabase Row Level Security (RLS) policies by using a `service_role` key via `get_system_client()` on user-facing endpoints exposes user data to unauthorized access.
**Prevention:** Always extract the JWT from the incoming `Authorization` header and use `get_user_client(jwt)` to instantiate a database client. This ensures that the RLS policies are applied at the database level according to the authenticated user's context.
