## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2026-05-13 - Fix IDOR in `list_sessions` API Endpoint
**Vulnerability:** The `/api/sessions` endpoint was previously retrieving data utilizing `get_system_client()`, a singleton that utilizes the `service_role` key to bypass Row-Level Security (RLS). This setup allowed any user capable of providing a valid `user_id` in the request to read any other user's session history, leading to an Insecure Direct Object Reference (IDOR).
**Learning:** Endpoints that serve user-specific data must not use system clients. When Supabase RLS policies are relied upon for authorization, they are completely bypassed by the `service_role` key.
**Prevention:** Endpoints returning user-specific data should extract the user's JWT from the `Authorization` header and instantiate a client contextually bound to that user via `get_user_client(user_jwt)`. This ensures database-level security policies (RLS) properly enforce data isolation.
