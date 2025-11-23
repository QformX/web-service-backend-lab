from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.api.v1.comments.schemas import CommentCreate, CommentOut
from src.infrastructure.db.deps import get_db
from src.infrastructure.db.models import Article, Comment
from src.common.security.deps import get_current_user, User


router = APIRouter(prefix="/articles", tags=["comments"])


@router.post("/{slug}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def add_comment(slug: str, payload: CommentCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> CommentOut:
    result = await db.execute(select(Article).where(Article.slug == slug))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    comment = Comment(body=payload.body, article_id=article.id, author_id=current_user.id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return CommentOut.model_validate(comment)


@router.get("/{slug}/comments", response_model=list[CommentOut])
async def list_comments(
    slug: str,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[CommentOut]:
    result = await db.execute(select(Article).where(Article.slug == slug))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    result = await db.execute(select(Comment).where(Comment.article_id == article.id).offset(offset).limit(limit))
    comments = result.scalars().all()
    return [CommentOut.model_validate(c) for c in comments]


@router.delete("/{slug}/comments/{comment_id}")
async def delete_comment(slug: str, comment_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    result = await db.execute(select(Article).where(Article.slug == slug))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    result = await db.execute(select(Comment).where(Comment.id == comment_id, Comment.article_id == article.id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.author_id != current_user.id and article.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    await db.delete(comment)
    await db.commit()
    return {"status": "deleted", "slug": slug, "comment_id": comment_id}



