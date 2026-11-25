"""
Firebase Authentication & Rate Limiting Guard for FastAPI endpoints.
Cryptographically verifies Firebase ID tokens via Google's public certificates
using google-auth without requiring private service-account credentials.
"""

import os
import time
import threading
from collections import defaultdict, deque
from fastapi import Header, HTTPException, Request
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
import requests as http_requests

FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "lab-report-lagbe")

# Reuse a single HTTP session so Google public certificate cache headers work efficiently
_http_session = http_requests.Session()
_google_request = google_requests.Request(session=_http_session)


def _decode_token_claims(raw_token: str) -> dict:
    """Verify signature, issuer, audience, and expiry of a Firebase ID token."""
    project_id = os.getenv("FIREBASE_PROJECT_ID", FIREBASE_PROJECT_ID) or "lab-report-lagbe"
    try:
        claims = google_id_token.verify_firebase_token(
            raw_token,
            _google_request,
            audience=project_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid or expired auth token: {exc}")
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication verification failed.")

    uid = claims.get("sub") or claims.get("user_id")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid authentication claims.")

    sign_in_provider = (claims.get("firebase") or {}).get("sign_in_provider", "")
    return {
        "uid": uid,
        "email": claims.get("email", ""),
        "email_verified": bool(claims.get("email_verified", False)),
        "sign_in_provider": sign_in_provider,
    }


def _extract_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header format.")
    token = parts[1].strip()
    if not token or len(token) > 8192:
        raise HTTPException(status_code=401, detail="Malformed bearer token.")
    return token


async def require_verified_user(authorization: str | None = Header(default=None)) -> dict:
    """FastAPI dependency requiring an authenticated and email-verified Firebase user."""
    token = _extract_bearer(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required. Please sign in.")
    user = _decode_token_claims(token)
    if user["sign_in_provider"] == "password" and not user["email_verified"]:
        raise HTTPException(
            status_code=403,
            detail="Email verification required before generating or downloading reports.",
        )
    return user


async def get_optional_user(authorization: str | None = Header(default=None)) -> dict | None:
    """FastAPI dependency returning verified claims if Authorization header is supplied, else None."""
    if not authorization:
        return None
    token = _extract_bearer(authorization)
    if not token:
        return None
    return _decode_token_claims(token)


class SlidingWindowRateLimiter:
    """Thread-safe per-IP sliding window rate limiter."""

    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            dq = self._hits[client_ip]
            while dq and dq[0] < cutoff:
                dq.popleft()
            if len(dq) >= self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please wait a minute before trying again.",
                )
            dq.append(now)


exec_rate_limiter = SlidingWindowRateLimiter(max_requests=25, window_seconds=60)
ai_rate_limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=60)
