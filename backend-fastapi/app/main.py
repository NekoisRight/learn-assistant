from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    articles,
    auth,
    mistakes,
    reports,
    scenes,
    sessions,
    users,
    vocabs,
)
from app.db.base import Base
from app.db.session import engine
from app.models import (  # noqa: F401 确保模型注册
    Article,
    Message,
    Mistake,
    Report,
    Scene,
    Session,
    User,
    Vocab,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="Learn Assistant API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(articles.router)
app.include_router(scenes.router)
app.include_router(sessions.router)
app.include_router(reports.router)
app.include_router(vocabs.router)
app.include_router(mistakes.router)

@app.get("/health")
async def health():
    return {"status": "ok"}

