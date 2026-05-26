## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2026-03-26 - Fix IDOR Vulnerability in API via Proper RLS Enforcement
**Vulnerability:** The `/api/sessions` endpoint used `get_system_client()`, which instantiated a Supabase client using the service role key. This key bypasses Row-Level Security (RLS) entirely, meaning any user could fetch any other user's sessions simply by guessing their `user_id`, leading to an Insecure Direct Object Reference (IDOR) vulnerability.
**Learning:** Endpoints that return user-specific data must not use `get_system_client()`. It should only be used internally by agents or systems where RLS bypass is intentionally designed.
**Prevention:** Always extract the user's JWT from the `Authorization` header and instantiate the client via `get_user_client(user_jwt)` for endpoints returning user data. This delegates data access enforcement to the database's RLS policies, ensuring users can only access their own data. Additionally, replace `traceback.print_exc()` with `logger.exception()` to keep tracebacks in the secure logging framework rather than leaking to standard error output.
