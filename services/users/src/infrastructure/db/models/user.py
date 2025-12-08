from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.base import Base

if TYPE_CHECKING:
    from .notification_delivery import NotificationDelivery
    from .subscription import Subscription


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(String(512), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    subscription_key: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Subscriptions relationships are defined lazily via string references to avoid circular imports
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="subscriber",
        cascade="all, delete-orphan",
        foreign_keys="Subscription.subscriber_id",
    )
    subscribers: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="target",
        cascade="all, delete-orphan",
        foreign_keys="Subscription.target_user_id",
    )

    deliveries: Mapped[list["NotificationDelivery"]] = relationship(
        "NotificationDelivery",
        back_populates="subscriber",
        cascade="all, delete-orphan",
        foreign_keys="NotificationDelivery.subscriber_id",
    )



