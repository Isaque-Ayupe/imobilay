## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2025-05-12 - Insecure Direct Object Reference (IDOR) via system client bypass in user-facing endpoints
**Vulnerability:** The `/api/sessions` REST endpoint used `get_system_client()` (which employs the Supabase service_role key to bypass Row-Level Security) to fetch a user's chat sessions, relying only on a provided `user_id` URL parameter for filtering. This created an IDOR vulnerability, allowing any user to read another user's sessions by guessing or brute-forcing the `user_id`.
**Learning:** Endpoints returning user-specific data must not use the system client because it ignores PostgreSQL Row-Level Security (RLS) policies. By bypassing RLS, the database cannot perform native, secure filtering based on the authenticated user's token.
**Prevention:** Always extract the user's JWT from the `Authorization` header in user-facing endpoints and pass it to `get_user_client(user_jwt)`. This instantiates a Supabase client that strictly respects RLS policies, ensuring users can only read their own data.
