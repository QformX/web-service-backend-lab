from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Any

from redis import asyncio as aioredis

logger = logging.getLogger(__name__)

_redis_client: aioredis.Redis | None = None
_queue_name: str | None = None


def _get_queue_name() -> str:
    global _queue_name
    if _queue_name is None:
        _queue_name = os.getenv("NOTIFICATIONS_QUEUE", "post_notifications")
    return _queue_name


async def _get_redis_client() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        # decode_responses=True to store JSON strings without manual decoding
        _redis_client = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    return _redis_client


async def enqueue_article_notification(author_id: int, article_id: int, article_title: str, extra_payload: dict[str, Any] | None = None) -> str:
    """Push a notification job into Redis-backed queue.

    Returns the generated job identifier for logging purposes.
    """
    job_id = str(uuid.uuid4())
    payload: dict[str, Any] = {
        "job_id": job_id,
        "author_id": author_id,
        "article_id": article_id,
        "article_title": article_title,
        "attempt": 1,
    }
    if extra_payload:
        payload.update(extra_payload)

    redis = await _get_redis_client()
    queue_name = _get_queue_name()
    await redis.rpush(queue_name, json.dumps(payload, ensure_ascii=False))
    logger.debug("Enqueued article notification job", extra={"job_id": job_id, "author_id": author_id, "article_id": article_id})
    return job_id
