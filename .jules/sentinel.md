## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2024-06-04 - Enforce User Client and JWT Verification on API Endpoints
**Vulnerability:** Insecure Direct Object Reference (IDOR) / Authentication Bypass. The `/api/sessions` endpoint accepted a user_id from the query parameters without authenticating the caller. It then bypassed Supabase's Row-Level Security (RLS) policies by fetching data using `get_system_client()`, which uses the `service_role` key.
**Learning:** Endpoints returning sensitive or user-specific data must never instantiate the system client, as it unconditionally overrides all database RLS protections. The system client is strictly for internal agent operations or pipelines that handle their own authorization contexts.
**Prevention:** Always enforce the standard `Authorization` header containing a valid user JWT on external API routes via FastAPI dependencies (`authorization: str = Header(...)`). Extract this token and use `get_user_client(user_jwt)` to ensure all subsequent database operations run in the context of that specific user, inherently enforcing proper RLS.
