import json

from fastapi import HTTPException, status
from pydantic import ValidationError

from app.schemas.scene import SceneCard
from app.services.llm_client import chat_completion

SYSTEM_PROMPT = """
你是一位资深的英语口语训练场景设计师。
你需要根据给定的英语文章，设计一个「角色扮演场景卡」，让学习者在真实冲突中开口说英语。

严格要求：
1. 只输出一个 JSON 对象，不要输出解释、Markdown 代码块或任何多余文字。
2. JSON 必须包含且仅包含以下键：
   title, user_role, goal, ai_roles, conflict, task_chain, language_goals, final_output, difficulty
3. ai_roles 是数组，每项含 name / stance / example 三个字符串字段；
   task_chain 是数组，每项含 stage / task / user_action 三个字符串字段。
4. ai_roles 至少 2 个，立场要有差异甚至对立；task_chain 至少 3 步，形成递进。
5. 除 ai_roles[].example 使用英文（贴合文章难度）外，其余字段使用中文说明。
6. conflict 必须具体、有张力，不能是泛泛而谈。
""".strip()

USER_TEMPLATE = """
文章标题：{title}
文章难度：{level}

文章正文：
{content}

指定场景难度：{difficulty}
{extra}
请输出该文章对应的场景卡 JSON。
""".strip()


def _strip_code_fence(raw: str) -> str:
    """去掉 LLM 可能包上的 ```json ... ``` 围栏"""
    text = raw.strip()
    if not text.startswith("```"):
        return text
    text = text.split("\n", 1)[-1] if "\n" in text else ""
    if text.rstrip().endswith("```"):
        text = text.rstrip()[:-3]
    return text.strip()


async def generate_scene_card(
    *,
    article_title: str,
    article_content: str,
    article_level: str,
    difficulty: str = "standard",
    extra_instructions: str | None = None,
) -> SceneCard:
    """调用 LLM 生成场景卡，失败一律抛 HTTPException。"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": USER_TEMPLATE.format(
                title=article_title,
                level=article_level,
                content=article_content,
                difficulty=difficulty,
                extra=(
                    f"额外要求：{extra_instructions}\n"
                    if extra_instructions
                    else ""
                ),
            ),
        },
    ]

    raw = await chat_completion(
        messages,
        temperature=0.7,
        timeout=60.0,
        json_mode=True,
    )

    try:
        parsed = json.loads(_strip_code_fence(raw))
        return SceneCard(**parsed)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM 返回内容无法解析：{exc}; raw={raw[:300]}",
        ) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM 返回结构不符合场景卡格式：{exc.errors()}",
        ) from exc
