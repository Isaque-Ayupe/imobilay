## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2026-05-06 - Insecure Direct Object Reference (IDOR) and RLS Bypass in API Endpoints
**Vulnerability:** The `/api/sessions` endpoint used `get_system_client()`, which accesses the database via `service_role` and bypasses Row-Level Security (RLS). This allowed any user to list another user's sessions merely by providing their `user_id`, leading to an IDOR vulnerability. Additionally, `/api/chat` lacked authentication.
**Learning:** Using system-level clients for user-specific data retrieval completely negates the protections provided by Supabase's RLS policies, opening up critical IDOR and data exposure vulnerabilities.
**Prevention:** Always require and validate an Authorization header containing the user's JWT on endpoints returning user-specific data. Use `get_user_client(user_jwt)` to instantiate the database client so that RLS policies are properly enforced per request.
