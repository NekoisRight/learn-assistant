from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.article import Article
from app.models.scene import Scene
from app.models.user import User
from app.schemas.scene import SceneGenerateRequest, SceneOut
from app.services.scene_generator import generate_scene_card

router = APIRouter(prefix="/api/scenes", tags=["scenes"])


@router.post(
    "/generate",
    response_model=SceneOut,
    status_code=status.HTTP_201_CREATED,
)
async def generate_scene(
    payload: SceneGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. 查询文章
    result = await db.execute(
        select(Article).where(Article.id == payload.article_id)
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    # 2. 调用 Qwen -> 3. Pydantic 校验（校验失败在 service 内抛 502）
    card = await generate_scene_card(
        article_title=article.title,
        article_content=article.content,
        article_level=article.level,
        difficulty=payload.difficulty,
        extra_instructions=payload.extra_instructions,
    )

    # 4. 落库
    scene = Scene(
        article_id=article.id,
        title=card.title,
        user_role=card.user_role,
        goal=card.goal,
        ai_roles=[role.model_dump() for role in card.ai_roles],
        conflict=card.conflict,
        task_chain=[step.model_dump() for step in card.task_chain],
        language_goals=card.language_goals,
        final_output=card.final_output,
        # 难度以请求参数为准，避免模型回显漂移
        difficulty=payload.difficulty,
    )

    db.add(scene)
    await db.commit()
    await db.refresh(scene)

    return scene


@router.get("", response_model=list[SceneOut])
async def list_scenes(
    article_id: int | None = Query(None, description="按文章过滤"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    stmt = select(Scene).order_by(Scene.created_at.desc())
    if article_id is not None:
        stmt = stmt.where(Scene.article_id == article_id)

    result = await db.execute(stmt.offset(offset).limit(page_size))

    return list(result.scalars().all())


@router.get("/{scene_id}", response_model=SceneOut)
async def get_scene(
    scene_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Scene).where(Scene.id == scene_id)
    )

    scene = result.scalar_one_or_none()

    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found",
        )

    return scene
