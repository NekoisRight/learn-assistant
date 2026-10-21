from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models._time import utcnow
from app.models.article import Article
from app.models.message import Message
from app.models.scene import Scene
from app.models.session import Session
from app.models.user import User
from app.schemas.message import MessageCreate, MessageOut, SendMessageResponse
from app.schemas.scene import SceneOut
from app.schemas.session import SessionCreate, SessionDetail, SessionOut
from app.services.chat_service import generate_ai_reply

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

@router.post("", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: SessionCreate,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    article = await db.get(Article, payload.article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
        
    scene = await db.get(Scene, payload.scene_id)
    if not scene or scene.article_id != payload.article_id:
        raise HTTPException(status_code=404, detail="Scene not found for this article")
    
    existing = await db.execute(
        select(Session).where(
            Session.user_id == current_user.id,
            Session.scene_id == payload.scene_id,
            Session.status == "active",
        )
    )
    session = existing.scalar_one_or_none()
    if session:
        # 复用已有活跃会话 -> 语义是 200 而非 201
        response.status_code = status.HTTP_200_OK
        return session
        
    session = Session(
        user_id=current_user.id,
        article_id=payload.article_id,
        scene_id=payload.scene_id,
        status="active",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

@router.get("/{session_id}", response_model=SessionDetail)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.user_id == current_user.id,  # 越权防护
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # 附带场景卡
    scene = await db.get(Scene, session.scene_id)
    scene_data = SceneOut.model_validate(scene).model_dump() if scene else None
    
    return SessionDetail(
        id=session.id,
        user_id=session.user_id,
        article_id=session.article_id,
        scene_id=session.scene_id,
        status=session.status,
        created_at=session.created_at,
        updated_at=session.updated_at,
        scene=scene_data, # pyright: ignore
    )

@router.post("/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: int,
    payload: MessageCreate,
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
        
    scene = await db.get(Scene, session.scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
        
    # 保存用户消息
    user_message = Message(session_id=session.id, role="user", content=payload.content)
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)
    
    # 调 LLM
    ai_content = await generate_ai_reply(db, session, scene)
    
    # 保存 AI 消息
    ai_message = Message(session_id=session.id, role="assistant", content=ai_content)
    db.add(ai_message)
    
    # 更新会话时间
    session.updated_at = utcnow()
    await db.commit()
    await db.refresh(ai_message)
    
    return SendMessageResponse(
        user_message=MessageOut.model_validate(user_message),
        ai_message=MessageOut.model_validate(ai_message),
    )

@router.patch("/{session_id}/end", response_model=SessionOut)
async def end_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Session).where(
            Session.user_id == current_user.id,  # 越权防护
            Session.id == session_id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session.status = "completed"
    await db.commit()
    await db.refresh(session)
    return session

@router.get("/{session_id}/messages", response_model=list[MessageOut])
async def list_messages(
    session_id: int,
    limit: int = Query(100, ge=1, le=500),
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
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Session not found")
        
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        # 同一秒写入的消息按 id 兜底排序，避免顺序抖动
        .order_by(Message.created_at.asc(), Message.id.asc())
        .limit(limit)
    )
    return result.scalars().all()
