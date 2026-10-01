from __future__ import annotations

import asyncio
import hashlib
import time
from dataclasses import dataclass

from redis.asyncio import Redis

from app.config import settings


@dataclass(frozen=True)
class RateLimitRule:
    scope: str
    limit: int
    window_seconds: int


class RateLimitExceeded(Exception):
    def __init__(self, *, retry_after: int) -> None:
        super().__init__("rate limit exceeded")
        self.retry_after = retry_after


_memory_lock = asyncio.Lock()
_memory_buckets: dict[str, tuple[int, float]] = {}
_redis_client: Redis | None = None


def _subject_hash(subject: str) -> str:
    return hashlib.sha256(subject.encode("utf-8")).hexdigest()[:24]


def _bucket_key(rule: RateLimitRule, subject: str, now: float) -> tuple[str, int]:
    bucket = int(now // rule.window_seconds)
    return (
        f"gb:rate:{rule.scope}:{_subject_hash(subject)}:{bucket}",
        bucket,
    )


async def _memory_increment(key: str, *, expires_at: float) -> int:
    async with _memory_lock:
        now = time.time()
        expired = [name for name, (_count, expiry) in _memory_buckets.items() if expiry <= now]
        for name in expired:
            _memory_buckets.pop(name, None)
        count, _expiry = _memory_buckets.get(key, (0, expires_at))
        count += 1
        _memory_buckets[key] = (count, expires_at)
        return count


def _redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def enforce_rate_limit(rule: RateLimitRule, *, subject: str) -> None:
    if not settings.rate_limit_enabled:
        return

    now = time.time()
    key, bucket = _bucket_key(rule, subject, now)
    bucket_end = (bucket + 1) * rule.window_seconds
    retry_after = max(1, int(bucket_end - now) + 1)

    if settings.rate_limit_backend == "redis":
        client = _redis()
        pipe = client.pipeline(transaction=True)
        pipe.incr(key)
        pipe.expire(key, rule.window_seconds + 2)
        result = await pipe.execute()
        count = int(result[0])
    else:
        count = await _memory_increment(key, expires_at=bucket_end + 2)

    if count > rule.limit:
        raise RateLimitExceeded(retry_after=retry_after)


async def reset_memory_rate_limits() -> None:
    async with _memory_lock:
        _memory_buckets.clear()
