from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.v1.comments.schemas import CommentCreate, CommentOut
from src.infrastructure.db.deps import get_db
from src.infrastructure.db.models import Article, Comment, User
from src.common.security.deps import get_current_user


router = APIRouter(prefix="/articles", tags=["comments"])


@router.post("/{slug}/comments", response_model=CommentOut)
def add_comment(slug: str, payload: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> CommentOut:
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    comment = Comment(body=payload.body, article_id=article.id, author_id=current_user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return CommentOut.model_validate(comment)


@router.get("/{slug}/comments", response_model=list[CommentOut])
def list_comments(slug: str, db: Session = Depends(get_db)) -> list[CommentOut]:
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    comments = db.query(Comment).filter(Comment.article_id == article.id).all()
    return [CommentOut.model_validate(c) for c in comments]


@router.delete("/{slug}/comments/{comment_id}")
def delete_comment(slug: str, comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.article_id == article.id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.author_id != current_user.id and article.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    db.delete(comment)
    db.commit()
    return {"status": "deleted", "slug": slug, "comment_id": comment_id}



