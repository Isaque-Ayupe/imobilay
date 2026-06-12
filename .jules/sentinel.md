## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2026-06-12 - Fix IDOR in list_sessions API
**Vulnerability:** The `/api/sessions` endpoint accepted a `user_id` query parameter and then retrieved sessions using `get_system_client()`. Since `get_system_client()` uses the Supabase service role key, it bypasses Row-Level Security (RLS), allowing an attacker to enumerate and access sessions belonging to any user simply by guessing or supplying their `user_id`. This is an Insecure Direct Object Reference (IDOR) vulnerability.
**Learning:** Using `get_system_client()` in frontend-facing API endpoints defeats the database's built-in RLS protections. The system client should be strictly reserved for internal pipeline agents or cron jobs where global access is required by design.
**Prevention:** For any frontend-facing endpoint that accesses or modifies user-specific data, explicitly require the user's JWT (e.g., via the `Authorization` header), and instantiate the database connection using `get_user_client(user_jwt)`. This ensures that all database operations are executed within the context of the authenticated user, automatically enforcing RLS policies.
