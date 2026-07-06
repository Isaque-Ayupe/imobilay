## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2024-07-06 - Safe Exception Logging in FastAPI Endpoints
**Vulnerability:** The application was using `traceback.print_exc()` to log exceptions in FastAPI endpoints.
**Learning:** Using `traceback.print_exc()` directly prints tracebacks to stderr, potentially exposing sensitive stack trace information outside of configured application logging frameworks and creating inconsistencies in structured log collection.
**Prevention:** Always use standard logging frameworks with `logger.exception(msg)` within except blocks. This ensures exception tracebacks are safely captured, structured, and routed according to application-wide security and logging policies.
