import httpx
from fastapi import HTTPException, status

from app.core.config import settings


def _protocol() -> str:
    """优先读 LLM_PROTOCOL；否则按 base_url 自动识别。"""
    configured = settings.LLM_PROTOCOL.strip().lower()
    if configured in {"anthropic", "openai"}:
        return configured
    base = settings.llm_base_url.lower()
    return "anthropic" if "anthropic" in base else "openai"


def _anthropic_url() -> str:
    base = settings.llm_base_url.rstrip("/")
    # 兼容 base 已带 /v1 的写法
    return f"{base}/messages" if base.endswith("/v1") else f"{base}/v1/messages"


def _openai_url() -> str:
    return f"{settings.llm_base_url.rstrip('/')}/chat/completions"


def _split_system(messages: list[dict]) -> tuple[str, list[dict]]:
    system_parts: list[str] = []
    rest: list[dict] = []
    for message in messages:
        if message.get("role") == "system":
            system_parts.append(str(message.get("content", "")))
        else:
            rest.append(
                {
                    "role": message.get("role", "user"),
                    "content": message.get("content", ""),
                }
            )
    return "\n\n".join(part for part in system_parts if part), rest


async def chat_completion(
    messages: list[dict],
    *,
    temperature: float = 0.3,
    timeout: float = 60.0,
    json_mode: bool = False,
    max_tokens: int | None = None,
) -> str:
    """统一调用 OpenAI 或 Anthropic 兼容接口，返回纯文本内容。

    json_mode 仅对 OpenAI 协议生效；Anthropic 协议依赖 Prompt 约束 JSON。
    """
    if not settings.llm_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM_API_KEY 未配置，请在 .env 中填写",
        )

    protocol = _protocol()
    max_tokens = max_tokens or settings.LLM_MAX_TOKENS

    if protocol == "anthropic":
        system_prompt, chat_messages = _split_system(messages)
        payload: dict = {
            "model": settings.LLM_MODEL_ID,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": chat_messages,
        }
        if system_prompt:
            payload["system"] = system_prompt
        headers = {
            "x-api-key": settings.llm_api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        url = _anthropic_url()
    else:
        payload = {
            "model": settings.LLM_MODEL_ID,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        headers = {
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        }
        url = _openai_url()

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code in (401, 403):
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=(
                        "LLM 鉴权失败（401/403）：请检查 LLM_API_KEY、"
                        "LLM_BASE_URL 与 LLM_MODEL_ID"
                    ),
                )
            if resp.status_code >= 400:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"LLM 调用失败 {resp.status_code}: {resp.text[:300]}",
                )
    except HTTPException:
        raise
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"LLM 请求超时（{int(timeout)} 秒），请重试",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"调用 LLM 失败：{exc}",
        ) from exc

    try:
        data = resp.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM 返回非 JSON：{resp.text[:300]}",
        ) from exc

    if protocol == "anthropic":
        blocks = data.get("content")
        if isinstance(blocks, str) and blocks.strip():
            return blocks
        if not isinstance(blocks, list):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM 返回结构异常：缺少 content 数组",
            )
        text = "".join(
            block.get("text", "")
            for block in blocks
            if isinstance(block, dict) and block.get("type") == "text"
        )
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM 返回内容为空（可能只返回了 thinking 块）",
            )
        return text

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM 返回结构异常：缺少 choices[0].message.content",
        ) from exc