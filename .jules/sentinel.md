## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2024-05-15 - Insecure Direct Object Reference (IDOR) via RLS Bypass
**Vulnerability:** The `/api/sessions` endpoint used the `get_system_client()` Supabase client (which uses the service_role key to bypass Row-Level Security) to fetch user sessions, exposing the system to potential IDOR attacks if user authorization logic was flawed or missing.
**Learning:** Frontend-facing backend endpoints returning user-specific data must extract the users JWT from the `Authorization` header and use `get_user_client(user_jwt)` to enforce RLS properly.
**Prevention:** Avoid using `get_system_client()` for endpoints that return user data to the frontend. Ensure endpoints expect an `Authorization` header and pass the JWT to `get_user_client(user_jwt)` so that Supabase Row-Level Security policies are inherently enforced.
