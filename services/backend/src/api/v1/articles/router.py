from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.api.v1.articles.schemas import ArticleCreate, ArticleOut, ArticleUpdate
from src.infrastructure.db.deps import get_db
from src.infrastructure.db.models import Article, Tag, ArticleTag
from src.common.utils.slugify import slugify
from src.common.security.deps import get_current_user, User


router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("", response_model=ArticleOut, status_code=status.HTTP_201_CREATED)
async def create_article(payload: ArticleCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> ArticleOut:
    base_slug = slugify(payload.title)
    candidate = base_slug
    i = 1
    while (await db.execute(select(Article).where(Article.slug == candidate))).scalar_one_or_none():
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
        result = await db.execute(select(Tag).where(Tag.name == name))
        t = result.scalar_one_or_none()
        if not t:
            t = Tag(name=name)
            db.add(t)
        tags.append(t)
    article.tags = tags
    db.add(article)
    await db.commit()
    await db.refresh(article)

    result = await db.execute(select(Article).options(selectinload(Article.tags)).where(Article.id == article.id))
    article_with_tags = result.scalar_one()
    
    return ArticleOut(slug=article_with_tags.slug, title=article_with_tags.title, description=article_with_tags.description, body=article_with_tags.body, tagList=[t.name for t in article_with_tags.tags])


@router.get("", response_model=list[ArticleOut])
async def list_articles(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[ArticleOut]:
    result = await db.execute(select(Article).options(selectinload(Article.tags)).offset(offset).limit(limit))
    articles = result.scalars().all()
    return [
        ArticleOut(slug=a.slug, title=a.title, description=a.description, body=a.body, tagList=[t.name for t in a.tags])
        for a in articles
    ]


@router.get("/{slug}", response_model=ArticleOut)
async def get_article(slug: str, db: AsyncSession = Depends(get_db)) -> ArticleOut:
    result = await db.execute(select(Article).options(selectinload(Article.tags)).where(Article.slug == slug))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return ArticleOut(slug=article.slug, title=article.title, description=article.description, body=article.body, tagList=[t.name for t in article.tags])


@router.put("/{slug}", response_model=ArticleOut)
async def update_article(slug: str, payload: ArticleUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> ArticleOut:
    # Загружаем статью С тегами заранее, чтобы избежать lazy loading
    result = await db.execute(
        select(Article)
        .options(selectinload(Article.tags))
        .where(Article.slug == slug)
    )
    article = result.scalar_one_or_none()
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
            result = await db.execute(select(Tag).where(Tag.name == name))
            t = result.scalar_one_or_none()
            if not t:
                t = Tag(name=name)
                db.add(t)
            new_tags.append(t)
        # Теперь присваивание безопасно, т.к. теги уже загружены
        article.tags = new_tags
    db.add(article)
    await db.commit()
    await db.refresh(article, ["tags"])
    
    # Перезагружаем с тегами для возврата
    result = await db.execute(
        select(Article)
        .options(selectinload(Article.tags))
        .where(Article.slug == slug)
    )
    article_with_tags = result.scalar_one()
    
    return ArticleOut(slug=article_with_tags.slug, title=article_with_tags.title, description=article_with_tags.description, body=article_with_tags.body, tagList=[t.name for t in article_with_tags.tags])


@router.delete("/{slug}")
async def delete_article(slug: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    result = await db.execute(select(Article).where(Article.slug == slug))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    if article.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    await db.delete(article)
    await db.commit()
    return {"status": "deleted", "slug": slug}


