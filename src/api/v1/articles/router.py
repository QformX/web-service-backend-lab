from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.api.v1.articles.schemas import ArticleCreate, ArticleOut, ArticleUpdate
from src.infrastructure.db.deps import get_db
from src.infrastructure.db.models import Article, Tag, ArticleTag, User
from src.common.utils.slugify import slugify
from src.common.security.deps import get_current_user


router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("", response_model=ArticleOut)
def create_article(payload: ArticleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ArticleOut:
    base_slug = slugify(payload.title)
    candidate = base_slug
    i = 1
    while db.query(Article).filter(Article.slug == candidate).first():
        i += 1
        candidate = f"{base_slug}-{i}"
    article = Article(
        slug=candidate,
        title=payload.title,
        description=payload.description,
        body=payload.body,
        author_id=current_user.id,
    )
    tags: list[Tag] = []
    for name in payload.tagList or []:
        t = db.query(Tag).filter(Tag.name == name).first()
        if not t:
            t = Tag(name=name)
            db.add(t)
        tags.append(t)
    article.tags = tags
    db.add(article)
    db.commit()
    db.refresh(article)
    return ArticleOut(slug=article.slug, title=article.title, description=article.description, body=article.body, tagList=[t.name for t in article.tags])


@router.get("", response_model=list[ArticleOut])
def list_articles(db: Session = Depends(get_db)) -> list[ArticleOut]:
    articles = db.query(Article).all()
    return [
        ArticleOut(slug=a.slug, title=a.title, description=a.description, body=a.body, tagList=[t.name for t in a.tags])
        for a in articles
    ]


@router.get("/{slug}", response_model=ArticleOut)
def get_article(slug: str, db: Session = Depends(get_db)) -> ArticleOut:
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return ArticleOut(slug=article.slug, title=article.title, description=article.description, body=article.body, tagList=[t.name for t in article.tags])


@router.put("/{slug}", response_model=ArticleOut)
def update_article(slug: str, payload: ArticleUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ArticleOut:
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    if article.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    if payload.title is not None:
        article.title = payload.title
    if payload.description is not None:
        article.description = payload.description
    if payload.body is not None:
        article.body = payload.body
    if payload.tagList is not None:
        new_tags: list[Tag] = []
        for name in payload.tagList:
            t = db.query(Tag).filter(Tag.name == name).first()
            if not t:
                t = Tag(name=name)
                db.add(t)
            new_tags.append(t)
        article.tags = new_tags
    db.add(article)
    db.commit()
    db.refresh(article)
    return ArticleOut(slug=article.slug, title=article.title, description=article.description, body=article.body, tagList=[t.name for t in article.tags])


@router.delete("/{slug}")
def delete_article(slug: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    if article.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    db.delete(article)
    db.commit()
    return {"status": "deleted", "slug": slug}


