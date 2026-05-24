## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2026-05-24 - API Authorization Header Parsing for RLS Context Extraction
**Vulnerability:** The GET `/api/sessions` endpoint suffered from an Insecure Direct Object Reference (IDOR). It loaded chat sessions simply by relying on an unverified `user_id` query parameter using `get_system_client()`. This bypassed Row-Level Security (RLS) entirely, since `get_system_client()` uses the Supabase service role key instead of the user context. Any user could fetch another user's sessions by providing their UUID.
**Learning:** System database clients (`get_system_client`) must NEVER be used to serve user-facing endpoints that expose personal or sensitive data. User-facing routes need to run queries within the context of the user.
**Prevention:** Always require and parse an `Authorization` header containing a valid user JWT in user-facing endpoints. Instantiate a dedicated user database client (e.g., `get_user_client(user_jwt)`) for each request to properly enforce RLS.
