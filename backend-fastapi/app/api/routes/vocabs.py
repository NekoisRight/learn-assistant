from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.vocab import Vocab
from app.schemas.report import VocabOut

router = APIRouter(prefix="/api/vocabs", tags=["vocabs"])


@router.get("", response_model=list[VocabOut])
async def list_vocabs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    mastered: int | None = Query(None, ge=0, le=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    offset = (page - 1) * page_size
    stmt = (
        select(Vocab)
        .where(Vocab.user_id == current_user.id)
        .order_by(Vocab.created_at.desc(), Vocab.id.desc())
        .offset(offset)
        .limit(page_size)
    )
    if mastered is not None:
        stmt = stmt.where(Vocab.mastered == mastered)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{vocab_id}/review", response_model=VocabOut)
async def review_vocab(
    vocab_id: int,
    mastered: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Vocab).where(
            Vocab.id == vocab_id,
            Vocab.user_id == current_user.id,
        )
    )
    vocab = result.scalar_one_or_none()
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocab not found")

    vocab.review_count += 1
    if mastered:
        vocab.mastered = 1

    await db.commit()
    await db.refresh(vocab)
    return vocab