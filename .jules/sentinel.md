## 2024-04-24 - FastAPI Security Headers Middleware
**Vulnerability:** The FastAPI application in `api.py` was missing standard security headers (like X-Content-Type-Options, X-Frame-Options), which are critical for defense-in-depth against MIME-sniffing and clickjacking attacks.
**Learning:** Security headers should be consistently applied across all endpoints in the Python backend. While a proxy/load-balancer can add these, applying them in the application layer guarantees they exist regardless of deployment architecture.
**Prevention:** Always implement a custom `@app.middleware("http")` to inject strict security headers for all API responses during initial setup.
