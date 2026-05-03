"""
Security & observability middleware for FastAPI — Pure ASGI.

IMPORTANT: These are pure ASGI middleware, NOT BaseHTTPMiddleware subclasses.
BaseHTTPMiddleware is known to break CORSMiddleware in Starlette by wrapping
responses in StreamingResponse, which strips CORS headers.
See: https://github.com/encode/starlette/issues/1591

Includes:
  - Request-ID injection (X-Request-ID header on every response)
  - Security headers (HSTS, X-Content-Type, Referrer-Policy)
  - Request logging with timing
"""
import uuid
import time
import logging
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.datastructures import MutableHeaders

logger = logging.getLogger(__name__)


class RequestIDMiddleware:
    """Pure ASGI middleware: inject X-Request-ID into every response."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract or generate request ID
        request_headers = dict(scope.get("headers", []))
        request_id = request_headers.get(b"x-request-id", b"").decode() or str(uuid.uuid4())[:8]

        start = time.perf_counter()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append("X-Request-ID", request_id)
                elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
                logger.info(
                    "%s %s → %s (%sms)",
                    scope["method"],
                    scope["path"],
                    message.get("status", "?"),
                    elapsed_ms,
                )
            await send(message)

        await self.app(scope, receive, send_wrapper)


class SecurityHeadersMiddleware:
    """Pure ASGI middleware: add security headers to every response."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        is_https = scope.get("scheme") == "https"

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append("X-Content-Type-Options", "nosniff")
                headers.append("X-Frame-Options", "DENY")
                headers.append("Referrer-Policy", "strict-origin-when-cross-origin")
                headers.append("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
                if is_https:
                    headers.append("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
            await send(message)

        await self.app(scope, receive, send_wrapper)
