## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2024-06-24 - IDOR Vulnerability in Sessions API Endpoint
**Vulnerability:** The `/api/sessions` endpoint accepted a `user_id` query parameter but instantiated the Supabase client using `get_system_client()`. This bypassed Row-Level Security (RLS) entirely, meaning any user could supply any arbitrary `user_id` and successfully read other users' session histories.
**Learning:** Returning user-specific data from a database with an elevated privilege client (system/service role) causes Insecure Direct Object Reference (IDOR) vulnerabilities if proper ownership checks are absent.
**Prevention:** Always extract the user's JWT from the `Authorization` header on frontend-facing endpoints returning user data and instantiate the client using `get_user_client(user_jwt)`. This enforces RLS policies built into the database layer correctly.
