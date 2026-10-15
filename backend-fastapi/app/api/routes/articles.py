from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.article import Article
from app.models.user import User
from app.schemas.article import ArticleBrief, ArticleCreate, ArticleOut

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.post("", response_model=ArticleOut, status_code=status.HTTP_201_CREATED)
async def create_article(
    payload: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    article = Article(
        title=payload.title,
        content=payload.content,
        level=payload.level,
        source=payload.source,
    )

    db.add(article)
    await db.commit()
    await db.refresh(article)

    return article


@router.get("", response_model=list[ArticleBrief])
async def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    result = await db.execute(
        select(Article)
        .order_by(Article.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    return list(result.scalars().all())


@router.get("/{article_id}", response_model=ArticleOut)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Article)
        .where(Article.id == article_id)
    )

    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return article
