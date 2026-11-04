from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.message import Message
from app.models.mistake import Mistake
from app.models.report import Report
from app.models.scene import Scene
from app.models.session import Session
from app.models.user import User
from app.models.vocab import Vocab
from app.schemas.report import ReportOut
from app.services.feedback_service import generate_feedback

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/generate", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
async def generate_report(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 越权防护
    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 幂等：已有报告直接返回
    existing = await db.execute(select(Report).where(Report.session_id == session_id))
    existing_report = existing.scalar_one_or_none()
    if existing_report:
        return existing_report

    scene = await db.get(Scene, session.scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    msg_result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc(), Message.id.asc())
    )
    messages = msg_result.scalars().all()

    conversation = [{"role": m.role, "content": m.content} for m in messages]

    feedback = await generate_feedback(scene.title, scene.goal, conversation)

    report = Report(
        session_id=session.id,
        user_id=current_user.id,
        grammar_issues=[g.model_dump() for g in feedback.grammar_issues],
        vocab_suggestions=[v.model_dump() for v in feedback.vocab_suggestions],
        expression_upgrades=[e.model_dump() for e in feedback.expression_upgrades],
        task_completion=feedback.task_completion.model_dump(),
        overall_score=feedback.overall_score,
        summary=feedback.summary,
    )
    db.add(report)

    for v in feedback.vocab_suggestions:
        db.add(
            Vocab(
                user_id=current_user.id,
                session_id=session.id,
                word=v.word,
                meaning=v.meaning,
                example=v.example,
            )
        )

    for g in feedback.grammar_issues:
        db.add(
            Mistake(
                user_id=current_user.id,
                session_id=session.id,
                original=g.original,
                corrected=g.corrected,
                reason=g.reason,
                category="grammar",
            )
        )

    try:
        await db.commit()
    except IntegrityError:
        # 并发重复生成时由 unique(session_id) 兜底，返回已存在报告
        await db.rollback()
        existing = await db.execute(
            select(Report).where(Report.session_id == session_id)
        )
        existing_report = existing.scalar_one_or_none()
        if existing_report:
            return existing_report
        raise HTTPException(status_code=409, detail="Report already exists")

    await db.refresh(report)
    return report


@router.get("/{session_id}", response_model=ReportOut)
async def get_report(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Report).where(
            Report.session_id == session_id,
            Report.user_id == current_user.id,
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report