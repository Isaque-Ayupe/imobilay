## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.
## 2025-02-25 - Prevent IDOR by using RLS-enabled Supabase client
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `api.py` endpoint `/api/sessions`. It extracted `user_id` from query parameters and used the service-role `get_system_client()`, which bypassed Row-Level Security (RLS). Any unauthenticated user could request the chat sessions of any user by simply providing their `user_id`.
**Learning:** `get_system_client()` uses the `service_role` key and entirely bypasses database policies (RLS). It should only be used by background agents. Endpoints handling user-specific data must require an `Authorization` header containing a valid user JWT, which should then be passed to `get_user_client(user_jwt)` to ensure database queries only operate on rows authorized for that specific user.
**Prevention:** Do not default to `get_system_client()` for data fetches in web endpoints. Always enforce authentication via the `Authorization` header on API routes and instantiate `get_user_client()` to enable RLS protections automatically.
