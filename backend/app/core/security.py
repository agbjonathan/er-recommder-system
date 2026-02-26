from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"

        return response