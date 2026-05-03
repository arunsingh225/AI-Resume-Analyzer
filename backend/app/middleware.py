"""
Security & observability middleware for FastAPI — Pure ASGI.

All middleware here are pure ASGI (no BaseHTTPMiddleware) to avoid
the known Starlette bug where BaseHTTPMiddleware breaks response headers.

Includes:
  - Manual CORS handling (replaces broken CORSMiddleware)
  - Request-ID injection
  - Security headers
"""
import uuid
import time
import logging
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.datastructures import MutableHeaders

logger = logging.getLogger(__name__)

# ── Allowed CORS origins ────────────────────────────────────────────
ALLOWED_ORIGINS = {
    "https://ai-resume-analyzer-tawny-theta.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
}


class CORSMiddlewareManual:
    """
    Pure ASGI CORS middleware — replaces Starlette's CORSMiddleware entirely.

    Starlette's CORSMiddleware was not sending Access-Control-Allow-Origin
    headers on Render.com even when origins were correctly configured.
    This custom implementation handles CORS at the raw ASGI level.
    """

    def __init__(self, app: ASGIApp, extra_origins: set = None):
        self.app = app
        self.origins = ALLOWED_ORIGINS | (extra_origins or set())
        logger.info("CORSMiddlewareManual: allowed origins = %s", self.origins)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract origin from raw ASGI headers
        origin = ""
        for key, value in scope.get("headers", []):
            if key == b"origin":
                origin = value.decode("latin-1")
                break

        is_allowed = origin in self.origins

        # ── Handle OPTIONS preflight ────────────────────────────────
        if scope["method"] == "OPTIONS" and is_allowed:
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    (b"access-control-allow-origin", origin.encode()),
                    (b"access-control-allow-methods", b"GET, POST, PUT, DELETE, PATCH, OPTIONS"),
                    (b"access-control-allow-headers", b"Content-Type, Authorization, X-Request-ID, Accept"),
                    (b"access-control-allow-credentials", b"true"),
                    (b"access-control-max-age", b"86400"),
                    (b"vary", b"Origin"),
                    (b"content-length", b"0"),
                ],
            })
            await send({"type": "http.response.body", "body": b""})
            return

        # ── Regular requests — inject CORS headers into response ────
        async def send_wrapper(message):
            if message["type"] == "http.response.start" and is_allowed:
                # Copy existing headers and add CORS headers
                headers = list(message.get("headers", []))
                headers.append((b"access-control-allow-origin", origin.encode()))
                headers.append((b"access-control-allow-credentials", b"true"))
                headers.append((b"vary", b"Origin"))
                message = dict(message)
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)


class RequestIDMiddleware:
    """Pure ASGI middleware: inject X-Request-ID into every response."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

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
                    scope["method"], scope["path"],
                    message.get("status", "?"), elapsed_ms,
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
