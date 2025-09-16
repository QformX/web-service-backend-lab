from __future__ import annotations

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.base import Base


class Article(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)

    author: Mapped["User"] = relationship(back_populates="articles")
    comments: Mapped[list["Comment"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    tags: Mapped[list["Tag"]] = relationship(secondary="articletag", back_populates="articles")


class Tag(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    articles: Mapped[list["Article"]] = relationship(secondary="articletag", back_populates="tags")


class ArticleTag(Base):
    __tablename__ = "articletag"

    article_id: Mapped[int] = mapped_column(ForeignKey("article.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True)


