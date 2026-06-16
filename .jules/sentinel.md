## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.
## 2025-06-16 - Prevent IDOR in Supabase Backend Endpoints
**Vulnerability:** The `/api/sessions` endpoint used `get_system_client()` (which uses the `service_role` key to bypass RLS) and accepted a `user_id` from the query string without any authentication checks. This allowed any user to fetch another user's session history just by knowing their `user_id`, resulting in an Insecure Direct Object Reference (IDOR).
**Learning:** `get_system_client()` should only be used for internal pipeline agents that strictly need to bypass RLS. Frontend-facing backend endpoints that return user-specific data must always extract the user's JWT from the `Authorization` header and use `get_user_client(user_jwt)` to ensure Row-Level Security (RLS) is enforced at the database level.
**Prevention:** Always validate the `Authorization` header, parse the Bearer token, and instantiate the Supabase client using `get_user_client()` in API endpoints dealing with user data to rely on Supabase's built-in RLS policies.
