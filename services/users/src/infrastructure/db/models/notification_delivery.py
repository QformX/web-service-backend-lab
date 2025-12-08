from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.base import Base

if TYPE_CHECKING:
    from .user import User


class NotificationDelivery(Base):

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subscriber_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)
    author_id: Mapped[int] = mapped_column(index=True, nullable=False)
    article_id: Mapped[int] = mapped_column(index=True, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    subscriber: Mapped["User"] = relationship("User", foreign_keys=[subscriber_id], back_populates="deliveries")

    __table_args__ = (UniqueConstraint("subscriber_id", "article_id", name="uq_notification_delivery_subscriber_article"),)