## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2024-05-14 - Fix auth.uid() usage in Supabase RLS Policies
**Vulnerability:** Performance degradation and potential DoS vulnerability due to `auth.uid()` being called per-row in Row Level Security (RLS) policies. In a large table, this would mean executing the function repeatedly for every scanned row.
**Learning:** `auth.uid()` evaluates per row when used directly in the `USING` clause, turning what should be a fast indexed query into a slow sequential scan.
**Prevention:** Always wrap `auth.uid()` (and similar functions) in a subselect `(select auth.uid())` when writing RLS policies. This ensures the function is evaluated only once and its result is cached for the entire query execution.

## 2024-05-15 - FastAPI Security Headers and Exception Handling
**Vulnerability:** Missing standard HTTP security headers and direct traceback printing to standard output via `traceback.print_exc()`, which could expose internal stack traces to environment logs accessible by unintended parties.
**Learning:** `traceback.print_exc()` writes directly to sys.stderr, bypassing standard logging frameworks which might sanitize or securely route logs. Missing security headers in FastAPI leaves the API susceptible to basic browser-based attacks (MIME-sniffing, clickjacking, XSS).
**Prevention:** Always use `logger.exception()` within `except Exception as e:` blocks in FastAPI to ensure tracebacks are handled by the application's secure logging pipeline. Standardize the application of security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Strict-Transport-Security) via a global HTTP middleware.
