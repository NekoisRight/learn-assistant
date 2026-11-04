import json

from fastapi import HTTPException, status
from pydantic import ValidationError

from app.schemas.report import FeedbackResult
from app.services.llm_client import chat_completion

SYSTEM_PROMPT = """你是一位专业的英语老师。根据用户在一个沉浸式英语学习场景中的全部对话，生成一份学习反馈报告。
必须返回合法 JSON，不要包含 Markdown 代码块标记，不要包含任何解释文字。
JSON 字段如下：
- grammar_issues: 数组，每项含 original（用户原句）、corrected（修正后）、reason（中文说明）
- vocab_suggestions: 数组，每项含 word（英文单词或短语）、meaning（中文释义）、example（英文例句）
- expression_upgrades: 数组，每项含 original（用户原表达）、upgraded（升级后的表达）、reason（中文理由）
- task_completion: 对象，含 goal_achieved (bool) 、score (0-100 整数) 、comment（中文评语）
- overall_score: 整数，0-100，综合评分
- summary: 字符串，不超过 500 字，中文总结

规则：
1. 只分析用户的发言，不分析 AI 的发言。
2. grammar_issues 最多 5 条，vocab_suggestions 最多 8 条，expression_upgrades 最多 5 条。
3. 如果用户没有明显错误，grammar_issues 返回空数组。
4. 所有中文说明要简洁，鼓励为主。
5. 如果对话为空或用户几乎没发言，overall_score 给 0，summary 说明原因。"""


def _format_conversation(messages: list[dict]) -> str:
    lines = []
    for m in messages:
        role = "用户" if m["role"] == "user" else "AI"
        lines.append(f"{role}: {m['content']}")
    return "\n".join(lines)


def _strip_code_fence(raw: str) -> str:
    text = raw.strip()
    if not text.startswith("```"):
        return text
    text = text.split("\n", 1)[-1] if "\n" in text else ""
    if text.rstrip().endswith("```"):
        text = text.rstrip()[:-3]
    return text.strip()


async def generate_feedback(
    scene_title: str,
    scene_goal: str,
    conversation: list[dict],
) -> FeedbackResult:
    user_prompt = f"""场景名: {scene_title}
核心目标: {scene_goal}

完整对话:
{_format_conversation(conversation)}

请生成学习反馈 JSON。"""

    raw = await chat_completion(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        timeout=90.0,
        json_mode=True,
    )

    try:
        parsed = json.loads(_strip_code_fence(raw))
        return FeedbackResult(**parsed)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Invalid feedback JSON: {exc}; raw={raw[:300]}",
        ) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Invalid feedback JSON schema: {exc.errors()}",
        ) from exc