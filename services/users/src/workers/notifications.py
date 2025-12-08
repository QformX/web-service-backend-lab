from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Sequence

import httpx
from redis import asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.db.config import get_database_url
from src.infrastructure.db.models import NotificationDelivery, Subscription, User

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("WORKER_LOG_LEVEL", "INFO"))

QUEUE_NAME = os.getenv("NOTIFICATIONS_QUEUE", "post_notifications")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
PUSH_SERVICE_URL = os.getenv("PUSH_SERVICE_URL", "http://push-notificator:8000/api/v1/notify")
MAX_ATTEMPTS = int(os.getenv("NOTIFICATION_MAX_ATTEMPTS", "5"))
BACKOFF_BASE_SECONDS = int(os.getenv("NOTIFICATION_BACKOFF_BASE", "2"))
BACKOFF_MAX_SECONDS = int(os.getenv("NOTIFICATION_BACKOFF_MAX", "30"))

DATABASE_URL = get_database_url()
engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
SessionFactory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
redis_client = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


@dataclass
class JobContext:
    job_id: str
    author_id: int
    article_id: int
    article_title: str
    attempt: int
    pending_subscribers: list[int] | None = None


class DeliveryError(Exception):
    def __init__(self, message: str, failed_subscribers: Sequence[int]):
        super().__init__(message)
        self.failed_subscribers = list(failed_subscribers)


def _build_message(author_id: int, article_title: str) -> str:
    preview = (article_title or "").strip()[:10]
    return f"Пользователь {author_id} выпустил новую статью: {preview}..."


async def _load_pending_subscribers(session: AsyncSession, author_id: int, requested: list[int] | None) -> list[int]:
    if requested is not None:
        return requested
    stmt = select(Subscription.subscriber_id).where(Subscription.target_user_id == author_id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def _fetch_users(session: AsyncSession, subscriber_ids: list[int]) -> dict[int, User]:
    if not subscriber_ids:
        return {}
    stmt = select(User).where(User.id.in_(subscriber_ids))
    result = await session.execute(stmt)
    return {user.id: user for user in result.scalars().all()}


async def _has_notification(session: AsyncSession, subscriber_id: int, article_id: int) -> bool:
    stmt = select(NotificationDelivery.id).where(
        NotificationDelivery.subscriber_id == subscriber_id,
        NotificationDelivery.article_id == article_id,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def _send_push(
    client: httpx.AsyncClient,
    subscription_key: str,
    message: str,
    *,
    job_id: str,
    author_id: int,
    subscriber_id: int,
) -> None:
    headers = {
        "Authorization": f"Bearer {subscription_key}",
        "Content-Type": "application/json",
    }
    payload = {"message": message}
    try:
        response = await client.post(PUSH_SERVICE_URL, headers=headers, json=payload)
        response.raise_for_status()
        logger.info(
            "Push delivered",
            extra={"job_id": job_id, "author_id": author_id, "subscriber_id": subscriber_id},
        )
    except httpx.TimeoutException as exc:
        logger.error(
            "Push delivery timeout",
            extra={"job_id": job_id, "author_id": author_id, "subscriber_id": subscriber_id},
        )
        raise exc
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Push delivery failed",
            extra={
                "job_id": job_id,
                "author_id": author_id,
                "subscriber_id": subscriber_id,
                "status_code": exc.response.status_code,
            },
        )
        raise exc
    except httpx.HTTPError as exc:
        logger.error(
            "Push delivery failed",
            extra={"job_id": job_id, "author_id": author_id, "subscriber_id": subscriber_id},
        )
        raise exc


async def _process_job(ctx: JobContext, client: httpx.AsyncClient) -> list[int]:
    async with SessionFactory() as session:
        subscriber_ids = await _load_pending_subscribers(session, ctx.author_id, ctx.pending_subscribers)
        if not subscriber_ids:
            logger.info("No subscribers to notify", extra={"job_id": ctx.job_id, "author_id": ctx.author_id})
            return []

        users = await _fetch_users(session, subscriber_ids)
        failed: list[int] = []
        message = _build_message(ctx.author_id, ctx.article_title)

        for subscriber_id in subscriber_ids:
            user = users.get(subscriber_id)
            if user is None:
                logger.warning(
                    "Subscriber not found",
                    extra={"job_id": ctx.job_id, "author_id": ctx.author_id, "subscriber_id": subscriber_id},
                )
                continue
            if not user.subscription_key:
                logger.warning(
                    "Subscriber missing subscription key",
                    extra={"job_id": ctx.job_id, "author_id": ctx.author_id, "subscriber_id": subscriber_id},
                )
                continue
            if await _has_notification(session, subscriber_id, ctx.article_id):
                logger.debug(
                    "Notification already sent",
                    extra={"job_id": ctx.job_id, "author_id": ctx.author_id, "subscriber_id": subscriber_id},
                )
                continue
            try:
                await _send_push(
                    client,
                    user.subscription_key,
                    message,
                    job_id=ctx.job_id,
                    author_id=ctx.author_id,
                    subscriber_id=subscriber_id,
                )
            except Exception:
                failed.append(subscriber_id)
                continue
            delivery = NotificationDelivery(
                subscriber_id=subscriber_id,
                author_id=ctx.author_id,
                article_id=ctx.article_id,
            )
            session.add(delivery)
        await session.commit()
        return failed


async def _schedule_requeue(payload: dict[str, Any], delay: int) -> None:
    await asyncio.sleep(delay)
    await redis_client.rpush(QUEUE_NAME, json.dumps(payload, ensure_ascii=False))
    logger.info(
        "Job requeued",
        extra={"job_id": payload.get("job_id"), "attempt": payload.get("attempt"), "delay": delay},
    )


def _compute_backoff(attempt: int) -> int:
    backoff = BACKOFF_BASE_SECONDS ** max(1, attempt - 1)
    return min(backoff, BACKOFF_MAX_SECONDS)


async def _handle_payload(raw_payload: str, client: httpx.AsyncClient) -> None:
    payload = json.loads(raw_payload)
    ctx = JobContext(
        job_id=payload["job_id"],
        author_id=payload["author_id"],
        article_id=payload["article_id"],
        article_title=payload.get("article_title", ""),
        attempt=int(payload.get("attempt", 1)),
        pending_subscribers=payload.get("pending_subscribers"),
    )

    try:
        failed_ids: list[int] | None = await _process_job(ctx, client)
    except Exception:
        logger.exception(
            "Job processing failed",
            extra={"job_id": ctx.job_id, "author_id": ctx.author_id, "attempt": ctx.attempt},
        )
        failed_ids = ctx.pending_subscribers

    needs_requeue = failed_ids is None or (isinstance(failed_ids, list) and len(failed_ids) > 0)

    if not needs_requeue:
        logger.info(
            "Job completed",
            extra={"job_id": ctx.job_id, "author_id": ctx.author_id, "article_id": ctx.article_id},
        )
        return

    if ctx.attempt >= MAX_ATTEMPTS:
        logger.error(
            "Job dropped after max attempts",
            extra={
                "job_id": ctx.job_id,
                "author_id": ctx.author_id,
                "article_id": ctx.article_id,
                "failed_subscribers": failed_ids,
            },
        )
        return

    next_payload = {
        "job_id": ctx.job_id,
        "author_id": ctx.author_id,
        "article_id": ctx.article_id,
        "article_title": ctx.article_title,
        "attempt": ctx.attempt + 1,
    }
    if isinstance(failed_ids, list):
        next_payload["pending_subscribers"] = failed_ids
    delay = _compute_backoff(ctx.attempt + 1)
    asyncio.create_task(_schedule_requeue(next_payload, delay))


async def run_worker() -> None:
    logger.info("Notifications worker started", extra={"queue": QUEUE_NAME, "redis_url": REDIS_URL})
    async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
        while True:
            try:
                _, raw_payload = await redis_client.blpop(QUEUE_NAME)
            except Exception:  # pragma: no cover - defensive logging
                logger.exception("Redis connection error, retrying in 5 seconds")
                await asyncio.sleep(5)
                continue
            await _handle_payload(raw_payload, client)


def main() -> None:
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:  # pragma: no cover - graceful shutdown
        logger.info("Worker stopped")


if __name__ == "__main__":
    main()
