"""Shared rate limits, quotas, CORS origins, and admin auth helpers."""
from __future__ import annotations

import logging
import os
import re
import threading
import time
from collections import defaultdict, deque
from datetime import date, datetime, timezone
from typing import Any, Optional

from fastapi import Header, HTTPException, Request

logger = logging.getLogger(__name__)

DEFAULT_ORIGINS = [
    "https://justorai.com",
    "https://www.justorai.com",
    "https://justor.ai",
    "https://www.justor.ai",
    "https://justorai.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

ROLE_DAILY_QUOTA = {
    "General Public": 3,
    "Law Student": 30,
    "Legal Professional": 50,
}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
GUEST_ID_RE = re.compile(r"^guest[_-][A-Za-z0-9_-]{4,80}$")


def parse_allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "").strip()
    if not raw:
        return list(DEFAULT_ORIGINS)
    origins = [item.strip() for item in raw.split(",") if item.strip() and item.strip() != "*"]
    return origins or list(DEFAULT_ORIGINS)


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, limit: int, window_sec: int) -> bool:
        now = time.monotonic()
        cutoff = now - window_sec
        with self._lock:
            bucket = self._hits[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                return False
            bucket.append(now)
            return True


class DailyQuotaStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counts: dict[str, int] = {}
        self._day: str = date.today().isoformat()

    def _roll(self) -> None:
        today = date.today().isoformat()
        if today != self._day:
            self._counts.clear()
            self._day = today

    def peek(self, key: str) -> int:
        with self._lock:
            self._roll()
            return self._counts.get(key, 0)

    def consume(self, key: str, limit: int) -> tuple[int, int]:
        """Increment and return (remaining, limit). Raises 429 if exhausted."""
        with self._lock:
            self._roll()
            used = self._counts.get(key, 0)
            if used >= limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Daily research quota reached ({limit}). Try again tomorrow or sign in with a higher-allowance role.",
                )
            used += 1
            self._counts[key] = used
            return max(0, limit - used), limit


rate_limiter = SlidingWindowLimiter()
quota_store = DailyQuotaStore()
_pilot_emails: dict[str, float] = {}
_pilot_lock = threading.Lock()


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if forwarded:
        return forwarded
    return request.client.host if request.client else "anon"


def resolve_guest_id(request: Request, body_user_id: Optional[str]) -> str:
    header_id = (request.headers.get("X-Guest-Id") or "").strip()
    if GUEST_ID_RE.match(header_id):
        return header_id
    body = (body_user_id or "").strip()
    if GUEST_ID_RE.match(body):
        return body
    return f"guest-{client_ip(request)}"


def enforce_ip_rate_limit(request: Request, bucket: str, limit: int, window_sec: int) -> None:
    ip = client_ip(request)
    if not rate_limiter.allow(f"{bucket}:{ip}", limit, window_sec):
        raise HTTPException(status_code=429, detail="Too many requests. Please wait and try again.")


def quota_for_role(user_role: str) -> int:
    return ROLE_DAILY_QUOTA.get(user_role, ROLE_DAILY_QUOTA["General Public"])


def consume_chat_quota(user_id: str, user_role: str) -> dict[str, int]:
    limit = quota_for_role(user_role)
    remaining, limit = quota_store.consume(f"{user_id}:{date.today().isoformat()}", limit)
    return {"remaining": remaining, "limit": limit}


def admin_secret() -> str:
    return os.getenv("JUSTOR_ADMIN_SECRET", "").strip()


def require_admin_secret(authorization: Optional[str] = Header(None)) -> str:
    secret = admin_secret()
    if not secret:
        raise HTTPException(status_code=503, detail="Admin API is not configured.")
    token = (authorization or "").strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    if not token or token != secret:
        raise HTTPException(status_code=403, detail="Forbidden")
    return token


def valid_email(value: str) -> bool:
    return bool(EMAIL_RE.match((value or "").strip()))


def claim_pilot_email(email: str) -> None:
    normalized = email.strip().lower()
    now = time.time()
    with _pilot_lock:
        last = _pilot_emails.get(normalized)
        if last and now - last < 86400:
            raise HTTPException(status_code=409, detail="An application with this email was already received.")
        _pilot_emails[normalized] = now


def job_row(job_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": job_id,
        "status": payload.get("status"),
        "title": payload.get("title"),
        "user_id": payload.get("user_id"),
        "chunks_done": payload.get("chunks_done") or 0,
        "total_chunks": payload.get("total_chunks") or 0,
        "document_id": payload.get("document_id"),
        "error": payload.get("error"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
