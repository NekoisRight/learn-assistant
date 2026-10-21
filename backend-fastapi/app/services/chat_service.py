import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.message import Message
from app.models.scene import Scene
from app.models.session import Session

HISTORY_LIMIT = 10


def build_system_prompt(scene: Scene) -> str:
    ai_roles = "\n".join(
        f"- {r['name']} ({r['stance']}) : {r['example']}"
        for r in (scene.ai_roles or [])
    )
    task_chain = "\n".join(
        f"- {t['stage']}: {t['task']} (用户:{t['user_action']})"
        for t in (scene.task_chain or [])
    )
    return f"""你是一个沉浸式英语学习场景的AI 角色扮演者。请始终使用英文与用户对话(用户用中文时也尽量用简单英文回应,并在必要时给中文提示)。
【场景名】{scene.title}
【用户身份】{scene.user_role}
【核心目标】{scene.goal}
【核心冲突】{scene.conflict}
【语言目标】{scene.language_goals}
【最终产出】{scene.final_output}
【难度】{scene.difficulty}
【AI角色】
{ai_roles}
【任务链】
{task_chain}
规则:
1. 你是场景中的角色,不是通用助手。
2. 每次回复不超过3句,语言简洁,符合用户当前难度。
3. 适时引导用户完成下一个任务。
4. 如果用户语法错误明显,可在回复末尾用 [Hint] 给一句简短提示。"""


async def generate_ai_reply(
    db: AsyncSession,
    session: Session,
    scene: Scene,
) -> str:
    """基于最近历史生成 AI 回复。

    调用前用户消息必须已落库 —— 历史查询已包含它，这里不再重复追加。
    """
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session.id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(HISTORY_LIMIT)
    )
    recent = list(reversed(result.scalars().all()))

    messages = [{"role": "system", "content": build_system_prompt(scene)}]
    messages.extend({"role": m.role, "content": m.content} for m in recent)

    payload = {
        "model": settings.LLM_MODEL_ID,
        "messages": messages,
        "temperature": 0.7,
    }
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{settings.LLM_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            if resp.status_code in (401, 403):
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="LLM 鉴权失败（401/403）：请检查 LLM_API_KEY 与 LLM_BASE_URL",
                )
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"调用 LLM 失败：{exc}",
        ) from exc

    try:
        return resp.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM 返回结构异常：缺少 choices[0].message.content",
        ) from exc
