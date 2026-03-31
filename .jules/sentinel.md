## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2026-03-31 - RLS Performance Bottleneck (auth.uid() execution)
**Vulnerability:** Row Level Security (RLS) policies were using `auth.uid() = id` directly in the `USING` clause. This causes PostgreSQL to execute the `auth.uid()` function for every single row evaluated during a query. In large tables, this O(N) execution can cause severe performance degradation, effectively acting as a Denial-of-Service vector.
**Learning:** Functions in PostgreSQL `USING` clauses are evaluated per-row by default unless explicitly forced to be evaluated once. `auth.uid()` is a relatively expensive function call.
**Prevention:** Always wrap `auth.uid()` (and similar constant functions) in a subselect query inside RLS policies: `USING ((select auth.uid()) = id)`. This forces PostgreSQL to evaluate the function exactly once and cache the result for the entire query execution, improving performance by orders of magnitude and reducing DoS risk.
