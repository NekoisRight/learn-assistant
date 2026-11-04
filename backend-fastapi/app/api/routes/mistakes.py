from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.mistake import Mistake
from app.models.user import User
from app.schemas.report import MistakeOut

router = APIRouter(prefix="/api/mistakes", tags=["mistakes"])


@router.get("", response_model=list[MistakeOut])
async def list_mistakes(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Mistake)
        .where(Mistake.user_id == current_user.id)
        .order_by(Mistake.created_at.desc(), Mistake.id.desc())
        .offset(offset)
        .limit(page_size)
    )
    return result.scalars().all()