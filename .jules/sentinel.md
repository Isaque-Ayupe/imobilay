## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2026-05-27 - IDOR Vulnerability via System Client in User Endpoints
**Vulnerability:** The API endpoint `list_sessions` incorrectly utilized `get_system_client()` (using `SUPABASE_SERVICE_ROLE_KEY`), bypassing Row-Level Security (RLS) policies completely. This allowed any requester who could guess or provide a user's UUID to read all of their sessions, an Insecure Direct Object Reference (IDOR).
**Learning:** Using system-level administrative privileges or service role keys in context-sensitive, user-facing endpoints breaks Supabase RLS and leads directly to IDOR vulnerabilities.
**Prevention:** Always require user authorization via a JWT in an `Authorization` header for endpoints accessing user data. Use `get_user_client(user_jwt)` to ensure queries are automatically scoped by database-level RLS policies, explicitly separating system and user responsibilities.
