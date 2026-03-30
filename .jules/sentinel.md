## 2026-03-26 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** The API chat endpoint caught a generic `Exception` and directly returned `str(e)` in the `detail` parameter of the `HTTPException(status_code=500, detail=str(e))`.
**Learning:** This exposes internal error details, file paths, logic flaws, and stack traces to external users, enabling reconnaissance. The wildcard exception block combined with raw error string passing is an insecure pattern.
**Prevention:** Instead of sending detailed exception strings to the client, a generic fallback message like `"An internal server error occurred."` should be returned. The exact exception and traceback should be stored only in server-side logs using the Python `logging` module. Additionally, CORS settings were hardened by removing `"*"` from `allow_origins`.

## 2026-03-29 - Missing Rate Limiting on FastAPI Chat Endpoint
**Vulnerability:** The `/api/chat` endpoint was missing rate limiting, making it susceptible to DoS attacks and potential LLM abuse (excessive token consumption) by automated scripts or malicious actors.
**Learning:** High-value or computationally expensive endpoints (like those calling LLMs) should always be protected with rate limiting to prevent abuse and ensure system availability.
**Prevention:** Implemented a Redis-based rate limiting mechanism directly in `api.py` with an in-memory fallback. This ensures that users or IPs exceeding a specific threshold (e.g., 10 requests per minute) receive a `429 Too Many Requests` response.
