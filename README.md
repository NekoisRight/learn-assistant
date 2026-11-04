# Learn Assistant

文章驱动的沉浸式英语学习助手。

## 技术栈

- 前端：Vue3 + Vite + TypeScript + Pinia + Vue Router + Element Plus
- 后端：FastAPI + SQLalchemy + MySQL
- 包管理：前端 pnpm，后端 uv

## 运行

```bash
# 后端（8001；8000 可能被 ASUS Gear Link 等 HTTP.sys 服务占用）
cd backend-fastapi
uv run uvicorn app.main:app --reload --port 8001

# 前端（默认 5173，/api 已代理到 8001）
cd frontend
pnpm install
pnpm dev
```

启动后访问 http://localhost:5173，注册账号即可走通：

文章 → 生成场景 → 对话 → 结束学习 → 学习报告 → 生词本 / 错题本。

## LLM 配置

支持 Anthropic 与 OpenAI 两种兼容协议。`LLM_PROTOCOL` 留空时按 `LLM_BASE_URL` 自动识别（含 `anthropic` -> Anthropic，否则 OpenAI）。

阿里百炼 Anthropic 兼容（当前使用）：

```dotenv
LLM_API_KEY=sk-ws-xxx
LLM_MODEL_ID=deepseek-v4.1-flash-1017
LLM_BASE_URL=https://ws-xxxx.cn-beijing.maas.aliyuncs.com/apps/anthropic
LLM_PROTOCOL=anthropic
LLM_MAX_TOKENS=4096
```

OpenAI 兼容（DashScope / 智谱 GLM）：

```dotenv
LLM_API_KEY=sk-xxx
LLM_MODEL_ID=glm-4.5-flash
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_PROTOCOL=openai
```

`LLM_BASE_URL` 留空时会回退到 `GLM_BASE_URL`，再回退到 DashScope 兼容地址。
旧变量名 `DASHSCOPE_API_KEY` 仍兼容。

## 阶段 5 接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/reports/generate?session_id=` | 生成报告，拆存生词/错题；同一会话幂等 |
| GET | `/api/reports/{session_id}` | 按会话取报告（含用户隔离） |
| GET | `/api/vocabs?page=&page_size=&mastered=` | 当前用户生词本 |
| POST | `/api/vocabs/{id}/review?mastered=` | 复习/标记掌握 |
| GET | `/api/mistakes?page=&page_size=` | 当前用户错题本 |