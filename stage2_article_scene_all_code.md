# 阶段2：文章与场景卡（课时2-1 \~ 2-7）代码整合

来源：阶段2：文章与场景卡（课时2-1 \~ 2-7）PDF。

## 项目代码路径总览

    app/
    ├── models/
    │   ├── __init__.py
    │   ├── article.py
    │   └── scene.py
    ├── schemas/
    │   ├── article.py
    │   └── scene.py
    ├── api/
    │   └── routes/
    │       ├── articles.py
    │       └── scenes.py
    ├── services/
    │   ├── __init__.py
    │   └── scene_generator.py
    ├── core/
    │   └── config.py
    └── main.py

------------------------------------------------------------------------

# 2-1 创建文章表与场景表

## app/models/article.py

``` python
from datetime import datetime
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str] = mapped_column(String(20), default="B1")
    source: Mapped[str] = mapped_column(String(200), default="user_upload")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    scenes = relationship(
        "Scene",
        back_populates="article",
        cascade="all, delete-orphan"
    )
```

## app/models/scene.py

``` python
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Scene(Base):
    __tablename__ = "scenes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id"),
        index=True
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    user_role: Mapped[str] = mapped_column(String(100))
    goal: Mapped[str] = mapped_column(Text)
    ai_roles: Mapped[list] = mapped_column(JSON)
    conflict: Mapped[str] = mapped_column(Text)
    task_chain: Mapped[list] = mapped_column(JSON)
    language_goals: Mapped[str] = mapped_column(Text)
    final_output: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(
        String(20),
        default="standard"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    article = relationship(
        "Article",
        back_populates="scenes"
    )
```

## app/models/**init**.py

``` python
from app.models.user import User
from app.models.article import Article
from app.models.scene import Scene
```

------------------------------------------------------------------------

# 2-2 文章上传接口

## app/schemas/article.py

``` python
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=20)
    level: str = Field(default="B1", max_length=20)
    source: str = Field(default="user_upload", max_length=200)


class ArticleOut(BaseModel):
    id: int
    title: str
    content: str
    level: str
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArticleBrief(BaseModel):
    id: int
    title: str
    level: str
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

------------------------------------------------------------------------

# app/api/routes/articles.py

核心接口：

-   POST /api/articles
-   GET /api/articles
-   GET /api/articles/{id}

主要依赖：

``` python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.article import Article
```

创建：

``` python
article = Article(
    title=payload.title,
    content=payload.content,
    level=payload.level,
    source=payload.source
)

db.add(article)
await db.commit()
await db.refresh(article)

return article
```

列表：

``` python
offset = (page - 1) * page_size

result = await db.execute(
    select(Article)
    .order_by(Article.created_at.desc())
    .offset(offset)
    .limit(page_size)
)

return result.scalars().all()
```

详情：

``` python
result = await db.execute(
    select(Article)
    .where(Article.id == article_id)
)

article = result.scalar_one_or_none()

if not article:
    raise HTTPException(
        status_code=404,
        detail="Article not found"
    )

return article
```

------------------------------------------------------------------------

# 2-4 场景卡结构

## app/schemas/scene.py

包含：

-   AIRole
-   TaskStep
-   SceneCard
-   SceneGenerateRequest
-   SceneOut

核心字段：

``` python
class AIRole(BaseModel):
    name: str
    stance: str
    example: str


class TaskStep(BaseModel):
    stage: str
    task: str
    user_action: str
```

------------------------------------------------------------------------

# 2-5 Qwen生成服务

## app/core/config.py

新增：

``` python
DASHSCOPE_API_KEY: str = ""
LLM_MODEL_ID: str = "qwen-plus"
LLM_BASE_URL: str = (
    "https://dashscope.aliyuncs.com/compatible-mode/v1"
)
```

------------------------------------------------------------------------

## app/services/scene_generator.py

创建：

``` bash
mkdir -p app/services
touch app/services/__init__.py
```

调用：

``` python
async with httpx.AsyncClient(timeout=60.0) as client:
    resp = await client.post(
        f"{settings.LLM_BASE_URL}/chat/completions",
        headers=headers,
        json=payload
    )
```

解析：

``` python
data = resp.json()

raw = data["choices"][0]["message"]["content"]

parsed = json.loads(raw)

return SceneCard(**parsed)
```

------------------------------------------------------------------------

# app/api/routes/scenes.py

接口：

    POST /api/scenes/generate
    GET  /api/scenes/{scene_id}
    GET  /api/scenes

生成流程：

    查询文章
     ↓
    调用Qwen
     ↓
    Pydantic校验
     ↓
    Scene模型保存
     ↓
    返回结果

------------------------------------------------------------------------

# 2-7 测试启动

启动：

``` bash
uv run uvicorn app.main:app --reload --port 8000
```

注册：

``` python
from app.api.routes import auth, users, articles, scenes

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(articles.router)
app.include_router(scenes.router)
```

数据库验证：

``` sql
USE learn_assistant;

SELECT id,title,level,created_at FROM articles;

SELECT id,article_id,title,user_role,difficulty FROM scenes;
```
