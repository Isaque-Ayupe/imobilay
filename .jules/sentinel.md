## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2024-05-14 - IDOR in API Endpoints via get_system_client()
**Vulnerability:** The `/api/sessions` endpoint used the database client instantiated via `get_system_client()`, which operates with a `service_role` key. This allowed it to bypass Supabase's Row-Level Security (RLS) policies, permitting any user to request the session history of any other user merely by providing their `user_id` in the API call.
**Learning:** Instantiating database queries using a service role key directly in a user-facing API completely invalidates database-level RLS protections, turning what should be a robust authorization model into a gaping IDOR vulnerability.
**Prevention:** For endpoints returning user-specific data, always extract the user's JWT from the `Authorization` header and instantiate the database client using `get_user_client(user_jwt)`. This preserves the user context and properly enforces RLS rules on every database query.
