# 阶段零：环境搭建与架构初始化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans 按本计划逐任务执行，每完成一个任务汇报一次。

**Spec:** [specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 在当前仓库根目录 `D:\code\AI-agent` 下完成阶段零地基：`backend/`（FastAPI 分层骨架 + PG/Qdrant 连通）、`frontend/`（Vue3+TS 三页面骨架）、Docker Compose 双数据库、多环境配置，并为每个步骤产出面向小白的学习解释文档。

**Architecture:** 单仓库双子项目布局；后端按 api → core → adapters → services → repositories → utils 分层，前端按 api/router/layouts/views/stores/components 分层；根级 `docker-compose.yml` 编排 PostgreSQL 16 与 Qdrant；后端健康检查接口统一输出 `{code,message,data}` 并探测双数据库连通；前端通过 Vite 代理 `/api` 联调。

**Tech Stack:** Python 3.11+ / FastAPI / SQLAlchemy 2.x / psycopg / qdrant-client / Docker Compose / PostgreSQL 16 / Qdrant / Vue3 + TypeScript + Vite / Element Plus / vue-router / axios / pinia / pnpm。

**全局硬性规则（spec 6.8）：** 所有代码必须写清中文注释——方法/函数有 docstring 或头部注释，独立逻辑代码块前有注释，不直观单行有行内注释，前端模板区块与 script 逻辑均注释。本规则从当前任务起对所有代码生效。

---

## Task 0: 前置环境检查

**Files:** 无（只读检查）

**Step 1: 确认本机工具版本**

Run:
```bash
docker --version
docker compose version
python --version
node --version
pnpm --version
```

Expected: Docker 24+、Compose v2、Python 3.11+、Node 20+、pnpm 9+。任何一项缺失，先安装再继续。

**Step 2: 检查端口占用**

Run: `netstat -ano | findstr ":5432 :6333 :8000 :5173"`

Expected: 无输出（端口空闲）。若被占用，在后续 `.env` 中改用其他端口。

**Step 3: 检查 Docker 可用**

Run: `docker ps`

Expected: 正常列出容器（可能为空），无权限/守护进程错误。

---

## Task 1: 根级 Docker Compose 编排 PostgreSQL + Qdrant

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `.gitignore`

**Step 1: 创建根级 `.env.example`**

```dotenv
# 环境：development / production
APP_ENV=development

# PostgreSQL
POSTGRES_DB=aigc_chat
POSTGRES_USER=aigc_user
POSTGRES_PASSWORD=change_me_strong_password
POSTGRES_PORT=5432

# Qdrant
QDRANT_PORT=6333

# LLM（阶段 0 只预留，不调用）
LLM_PROVIDER=
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
LLM_PROXY_BASE_URL=
LLM_PROXY_API_KEY=
```

复制为本地 `.env`：`Copy-Item .env.example .env`，并把 `POSTGRES_PASSWORD` 改成自己的强密码。

**Step 2: 创建 `docker-compose.yml`**

```yaml
services:
  postgres:
    image: postgres:16
    container_name: aigc-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "${POSTGRES_PORT}:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 3s
      retries: 10

  qdrant:
    image: qdrant/qdrant:v1.12.4
    container_name: aigc-qdrant
    restart: unless-stopped
    ports:
      - "${QDRANT_PORT}:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD-SHELL", "bash -c ':> /dev/tcp/127.0.0.1/6333' || exit 1"]
      interval: 5s
      timeout: 3s
      retries: 10

volumes:
  pg_data:
  qdrant_data:
```

**Step 3: 创建根级 `.gitignore`**

```gitignore
# 密钥与环境
.env

# 本地工具目录
.harness/

# Python
__pycache__/
*.pyc
venv/
.venv/

# Node
node_modules/
dist/

# 编辑器
.idea/
.vscode/
```

**Step 4: 启动并验证**

Run:
```bash
docker compose up -d
docker compose ps
```

Expected: `aigc-postgres` 与 `aigc-qdrant` 均 `healthy`。

**Step 5: 写学习文档**

Create: `docs/learning/阶段0/02-Docker与PostgreSQL原理.md`，包含：容器与镜像区别、`docker compose up -d` 每个参数含义、volume 为什么能持久化、healthcheck 原理、为什么数据库用容器而代码不用。

**Step 6: Commit**

```bash
git add docker-compose.yml .env.example .gitignore docs/learning/阶段0/02-Docker与PostgreSQL原理.md
git commit -m "feat: 阶段零编排 PostgreSQL 与 Qdrant 环境"
```

---

## Task 2: 后端项目骨架与依赖

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/app/__init__.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/logging.py`
- Create: `backend/app/core/response.py`
- Create: `backend/app/core/exceptions.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/repositories/__init__.py`
- Create: `backend/app/adapters/__init__.py`
- Create: `backend/app/adapters/model_adapter.py`
- Create: `backend/app/utils/__init__.py`
- Create: `backend/tests/__init__.py`

**Step 1: 创建虚拟环境并安装依赖**

Run:
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Create `backend/requirements.txt`：

```txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
litellm==1.55.2
sqlalchemy==2.0.36
psycopg[binary]==3.2.3
pydantic==2.10.4
pydantic-settings==2.7.0
python-dotenv==1.0.1
cryptography==44.0.0
python-multipart==0.0.20
qdrant-client==1.12.1
pytest==8.3.4
httpx==0.28.1
```

Run: `pip install -r requirements.txt`

Expected: 全部安装成功，无冲突报错。

**Step 2: 创建配置模块 `backend/app/core/config.py`**

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "aigc-backend"
    app_env: str = "development"
    database_url: str = (
        "postgresql+psycopg://aigc_user:change_me@localhost:5432/aigc_chat"
    )
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_doc: str = "document_vectors"
    qdrant_collection_memory: str = "memory_vectors"
    llm_provider: str = ""
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""
    llm_proxy_base_url: str = ""
    llm_proxy_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

**Step 3: 创建日志模块 `backend/app/core/logging.py`**

```python
import logging
import sys


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
```

**Step 4: 创建统一响应 `backend/app/core/response.py`**

```python
from typing import Any

from fastapi.responses import JSONResponse


def ok(data: Any = None, message: str = "ok") -> JSONResponse:
    return JSONResponse({"code": 0, "message": message, "data": data})


def fail(code: int, message: str, data: Any = None, http_status: int = 400) -> JSONResponse:
    return JSONResponse(
        {"code": code, "message": message, "data": data},
        status_code=http_status,
    )
```

**Step 5: 创建异常处理 `backend/app/core/exceptions.py`**

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .response import fail


class AppError(Exception):
    def __init__(self, code: int = 400, message: str = "请求错误") -> None:
        self.code = code
        self.message = message


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return fail(exc.code, exc.message)

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_request: Request, _exc: Exception) -> JSONResponse:
        return fail(500, "服务器内部错误", http_status=500)
```

**Step 6: 创建模型适配器占位 `backend/app/adapters/model_adapter.py`**

```python
"""LiteLLM 二次封装占位层。

阶段 1 将在此实现统一入参/出参、官方 Key 与中转 Key 切换、流式接口。
本阶段只定义协议，不调用任何真实模型。
"""

from dataclasses import dataclass
from typing import AsyncIterator


class ModelError(Exception):
    """模型调用异常的统一类型。"""


@dataclass
class ChatRequest:
    model: str
    messages: list[dict]
    temperature: float = 0.7


@dataclass
class ChatResponse:
    content: str
    usage: dict | None = None


async def chat(request: ChatRequest) -> ChatResponse:
    raise NotImplementedError("阶段 1 实现")


async def stream_chat(request: ChatRequest) -> AsyncIterator[str]:
    raise NotImplementedError("阶段 1 实现")
```

**Step 7: 创建 `backend/.env.example`**

```dotenv
APP_ENV=development
DATABASE_URL=postgresql+psycopg://aigc_user:change_me@localhost:5432/aigc_chat
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_DOC=document_vectors
QDRANT_COLLECTION_MEMORY=memory_vectors
LLM_PROVIDER=
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
LLM_PROXY_BASE_URL=
LLM_PROXY_API_KEY=
```

复制为 `backend/.env`：`Copy-Item .env.example .env`（密码与根级 `.env` 保持一致）。

**Step 8: 验证导入**

Run: `python -c "from app.core.config import get_settings; print(get_settings().app_name)"`

Expected: 输出 `aigc-backend`。

**Step 9: 写学习文档**

Create: `docs/learning/阶段0/01-FastAPI分层架构为什么这样拆.md`，解释 api/core/models/schemas/services/adapters/repositories/utils 各层职责、为什么分层、venv 与 requirements.txt 的作用、为什么装 cryptography（阶段 2 加密预留）。

**Step 10: Commit**

```bash
git add backend docs/learning/阶段0/01-FastAPI分层架构为什么这样拆.md
git commit -m "feat: 阶段零搭建 FastAPI 分层骨架"
```

---

## Task 3: 数据库连接层（SQLAlchemy）

**Files:**
- Create: `backend/app/db/__init__.py`
- Create: `backend/app/db/session.py`

**Step 1: 创建 `backend/app/db/session.py`**

```python
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
```

**Step 2: 启动容器并验证连接**

Run: `docker compose up -d`（根目录）

Run: `python -c "from app.db.session import check_database; print(check_database())"`

Expected: 输出 `True`。

**Step 3: Commit**

```bash
git add backend/app/db
git commit -m "feat: 阶段零接入 SQLAlchemy 数据库连接"
```

---

## Task 4: Qdrant 连接与集合初始化

**Files:**
- Create: `backend/app/db/qdrant.py`
- Create: `backend/scripts/__init__.py`
- Create: `backend/scripts/init_qdrant.py`
- Create: `backend/scripts/check_connections.py`

**Step 1: 创建 `backend/app/db/qdrant.py`**

```python
from qdrant_client import QdrantClient

from app.core.config import get_settings

settings = get_settings()

DISTANCE = "Cosine"
VECTOR_SIZE = 1536  # 阶段 3/4 按实际 Embedding 模型调整


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def ensure_collections() -> list[str]:
    client = get_qdrant_client()
    names = [settings.qdrant_collection_doc, settings.qdrant_collection_memory]
    for name in names:
        existing = client.get_collections().collections
        if name not in [c.name for c in existing]:
            client.create_collection(
                collection_name=name,
                vectors_config={
                    "size": VECTOR_SIZE,
                    "distance": DISTANCE,
                },
            )
    return names


def check_qdrant() -> bool:
    try:
        get_qdrant_client().get_collections()
        return True
    except Exception:
        return False
```

**Step 2: 创建 `backend/scripts/init_qdrant.py`**

```python
from app.db.qdrant import ensure_collections


def main() -> None:
    names = ensure_collections()
    print("Qdrant Collections 就绪:", ", ".join(names))


if __name__ == "__main__":
    main()
```

**Step 3: 创建 `backend/scripts/check_connections.py`**

```python
from app.db.qdrant import check_qdrant
from app.db.session import check_database


def main() -> None:
    print(f"PostgreSQL: {'ok' if check_database() else 'error'}")
    print(f"Qdrant: {'ok' if check_qdrant() else 'error'}")


if __name__ == "__main__":
    main()
```

**Step 4: 运行初始化与检查（幂等验证）**

Run（backend 目录，venv 激活）:
```bash
python scripts/init_qdrant.py
python scripts/init_qdrant.py
python scripts/check_connections.py
```

Expected: 第一次创建两个 Collection，第二次提示已存在不重复创建；`PostgreSQL: ok`、`Qdrant: ok`。

**Step 5: 写学习文档**

Create: `docs/learning/阶段0/03-Qdrant向量库原理.md`，解释传统数据库与向量库区别、向量/维度/余弦相似度是什么、Collection 是什么、为什么文档向量与记忆向量分两个集合。

**Step 6: Commit**

```bash
git add backend/app/db/qdrant.py backend/scripts docs/learning/阶段0/03-Qdrant向量库原理.md
git commit -m "feat: 阶段零初始化 Qdrant 集合与连通检查"
```

---

## Task 5: 健康检查接口（TDD）

**Files:**
- Create: `backend/app/api/health.py`
- Create: `backend/app/api/router.py`
- Create: `backend/app/main.py`
- Test: `backend/tests/test_health.py`

**Step 1: 写失败测试 `backend/tests/test_health.py`**

> 所有新建代码（含测试）按 spec 6.8 注释规范编写。

```python
from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_unified_format() -> None:
    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["service"] == "aigc-backend"
    assert "database" in body["data"]
    assert "qdrant" in body["data"]
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_health.py -v`

Expected: FAIL，`ModuleNotFoundError: app.main`。

**Step 3: 创建 `backend/app/api/health.py`**

```python
from datetime import datetime

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.response import ok
from app.db.qdrant import check_qdrant
from app.db.session import check_database

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health():
    settings = get_settings()
    return ok(
        {
            "service": settings.app_name,
            "time": datetime.now().astimezone().isoformat(),
            "database": "ok" if check_database() else "error",
            "qdrant": "ok" if check_qdrant() else "error",
        }
    )
```

**Step 4: 创建 `backend/app/api/router.py`**

```python
from fastapi import APIRouter

from app.api.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
```

**Step 5: 创建 `backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging

setup_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)
app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "aigc-backend is running"}
```

**Step 6: 运行测试确认通过**

Run: `pytest tests/test_health.py -v`

Expected: PASS。

**Step 7: 手动启动验证**

Run: `uvicorn app.main:app --reload --port 8000`

浏览器访问 `http://localhost:8000/api/health`，Expected: 200 且 `database=ok`、`qdrant=ok`。

**Step 8: Commit**

```bash
git add backend/app/api backend/app/main.py backend/tests
git commit -m "feat: 阶段零实现统一健康检查接口"
```

---

## Task 5b: 已交付代码注释补全（spec 6.8）

**Files:**
- Modify: `backend/app/core/config.py`、`logging.py`、`response.py`、`exceptions.py`
- Modify: `backend/app/adapters/model_adapter.py`
- Modify: `backend/app/db/session.py`、`qdrant.py`
- Modify: `backend/scripts/init_qdrant.py`、`check_connections.py`

**Step 1: 逐文件补注释**

按 spec 6.8 为每个方法补 docstring/头部注释，为每个独立逻辑块补中文注释，为魔法数字等不直观单行补行内注释。注释要说明“做什么 + 为什么”，不写“设置变量”类废话。

**Step 2: 验证无回归**

Run: `python -m scripts.check_connections`

Expected: `PostgreSQL: ok`、`Qdrant: ok`。

**Step 3: Commit**

```bash
git add backend/app backend/scripts
git commit -m "docs: 阶段零补全代码注释规范"
```

---

## Task 6: 前端工程初始化

**Files:**
- Create: `frontend/`（Vite 脚手架）
- Create: `frontend/vite.config.ts`
- Create: `frontend/.env.development`
- Create: `frontend/.env.production`

**Step 1: 创建 Vite 工程**

Run（仓库根目录）:
```bash
pnpm create vite frontend --template vue-ts
cd frontend
pnpm install
pnpm add element-plus vue-router axios pinia
```

Expected: 安装完成，`frontend/package.json` 含上述依赖。

**Step 2: 配置 `frontend/vite.config.ts` 代理**

```ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

**Step 3: 创建环境文件**

`frontend/.env.development`：
```dotenv
VITE_API_BASE=/api
```

`frontend/.env.production`：
```dotenv
VITE_API_BASE=/api
```

**Step 4: 启动验证**

Run: `pnpm dev`

Expected: `http://localhost:5173` 可访问，默认 Vite 页面正常。

**Step 5: 写学习文档**

Create: `docs/learning/阶段0/05-Vue3工程结构说明.md`，解释 SPA 是什么、Vite 与开发服务器、TS 的作用、vue-ts 模板目录、pnpm 与 node_modules、为什么用 Element Plus。

**Step 6: Commit**

```bash
git add frontend docs/learning/阶段0/05-Vue3工程结构说明.md
git commit -m "feat: 阶段零初始化 Vue3 前端工程"
```

---

## Task 7: 前端请求封装、路由与布局

**Files:**
- Create: `frontend/src/api/request.ts`
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/layouts/MainLayout.vue`
- Modify: `frontend/src/main.ts`
- Modify: `frontend/src/App.vue`

**Step 1: 创建 `frontend/src/api/request.ts`**

```ts
import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  timeout: 30000,
})

request.interceptors.request.use((config) => {
  // 阶段 2 接入登录后在此注入 Token
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    ElMessage.error(error?.response?.data?.message || '网络异常，请稍后重试')
    return Promise.reject(error)
  },
)

export default request
```

**Step 2: 创建 `frontend/src/router/index.ts`**

```ts
import { createRouter, createWebHistory } from 'vue-router'

import MainLayout from '../layouts/MainLayout.vue'
import HomeView from '../views/HomeView.vue'
import ChatView from '../views/ChatView.vue'
import UploadView from '../views/UploadView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', name: 'home', component: HomeView },
        { path: 'chat', name: 'chat', component: ChatView },
        { path: 'upload', name: 'upload', component: UploadView },
      ],
    },
  ],
})

export default router
```

**Step 3: 创建 `frontend/src/layouts/MainLayout.vue`**

```vue
<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="brand">AIGC 对话平台</div>
      <el-menu mode="horizontal" :router="true" :default-active="$route.path">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/chat">聊天</el-menu-item>
        <el-menu-item index="/upload">文档上传</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>
```

**Step 4: 修改 `frontend/src/main.ts` 注册路由与 Element Plus**

```ts
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import App from './App.vue'
import router from './router'

createApp(App).use(router).use(ElementPlus).mount('#app')
```

**Step 5: 修改 `frontend/src/App.vue` 只保留路由出口**

```vue
<template>
  <router-view />
</template>
```

**Step 6: 启动验证**

Run: `pnpm dev`

Expected: 页面出现顶部导航，点击首页/聊天/文档上传可切换路由且导航高亮。

**Step 7: 写学习文档**

Create: `docs/learning/阶段0/06-前后端如何联调.md`，解释 HTTP/JSON 通信、REST 风格、axios 拦截器、Vite 代理 `/api` 解决跨域的原理、Element Plus 菜单路由模式。

**Step 8: Commit**

```bash
git add frontend/src docs/learning/阶段0/06-前后端如何联调.md
git commit -m "feat: 阶段零封装前端请求与路由布局"
```

---

## Task 8: 三个基础页面骨架

**Files:**
- Create: `frontend/src/views/HomeView.vue`
- Create: `frontend/src/views/ChatView.vue`
- Create: `frontend/src/views/UploadView.vue`

**Step 1: 创建 `frontend/src/views/HomeView.vue`**

```vue
<template>
  <div class="home">
    <h1>AIGC 对话 + RAG + AI 记忆项目</h1>
    <p>阶段零：环境搭建与架构初始化</p>
    <el-space>
      <el-button type="primary" @click="$router.push('/chat')">进入聊天</el-button>
      <el-button @click="$router.push('/upload')">文档上传</el-button>
    </el-space>
  </div>
</template>
```

**Step 2: 创建 `frontend/src/views/ChatView.vue`**

```vue
<template>
  <div class="chat">
    <el-empty description="聊天功能将在阶段 1 接入" />
    <div class="chat-input">
      <el-input
        v-model="message"
        type="textarea"
        :rows="3"
        placeholder="输入你的问题（静态占位）"
      />
      <el-button type="primary" disabled>发送</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const message = ref('')
</script>
```

**Step 3: 创建 `frontend/src/views/UploadView.vue`**

```vue
<template>
  <div class="upload">
    <el-empty description="文件上传将在阶段 3 接入" />
  </div>
</template>
```

**Step 4: 启动验证**

Run: `pnpm dev`

Expected: 三个页面均可访问，页面文案与占位控件正常显示。

**Step 5: 提交**

```bash
git add frontend/src/views
git commit -m "feat: 阶段零搭建三个基础页面骨架"
```

---

## Task 9: 多环境配置、README 与文档收尾

**Files:**
- Create: `README.md`
- Create: `docs/learning/阶段0/07-多环境配置与密钥安全.md`
- Modify: `backend/.gitignore`、`frontend/.gitignore`（如缺失则创建）

**Step 1: 创建根级 `README.md`**

内容包含：项目简介、目录结构（backend/frontend/docs）、快速启动（复制 .env → 改密码 → `docker compose up -d` → 启动后端 → 启动前端）、端口一览、学习文档索引、阶段规划表。

**Step 2: 补 `.gitignore`**

`backend/.gitignore`：
```gitignore
venv/
__pycache__/
*.pyc
.env
.pytest_cache/
```

`frontend/.gitignore`（Vite 模板已生成，补充确认包含 `.env`）：
```gitignore
.env
.env.local
node_modules/
dist/
```

**Step 3: 写学习文档**

Create: `docs/learning/阶段0/07-多环境配置与密钥安全.md`，解释为什么代码不写死密钥、`.env` 与 `.env.example` 的区别、development/production 环境、`.gitignore` 机制、阶段 2 将如何用 cryptography 加密存储。

**Step 4: 全量启动自测**

Run:
```bash
docker compose ps
cd backend && python scripts/check_connections.py
cd ../frontend && pnpm dev
```

Expected: 双容器 healthy、后端打印 `PostgreSQL: ok` / `Qdrant: ok`、前端页面可访问。

**Step 5: Commit**

```bash
git add README.md backend/.gitignore frontend/.gitignore docs/learning/阶段0/07-多环境配置与密钥安全.md
git commit -m "docs: 阶段零补充启动文档与环境安全说明"
```

---

## Task 10: 全量验收

**Files:** 无（只做验证）

**Step 1: 后端验收**

Run: `cd backend && pytest -q && python scripts/check_connections.py`

Expected: `1 passed`，`PostgreSQL: ok`、`Qdrant: ok`。

**Step 2: 基础设施验收**

Run: `docker compose ps`

Expected: 两个容器均为 `healthy`。

**Step 3: 前端验收**

Run: `cd frontend && pnpm build`

Expected: TypeScript 类型检查与构建成功，无报错。

**Step 4: 联调验收**

启动后端与前端后，浏览器访问 `http://localhost:5173`，Network 面板请求 `http://localhost:5173/api/health`。

Expected: 返回 200，`{code:0, message:"ok", data:{...}}`，证明代理链路通。

**Step 5: 学习文档验收**

检查 `docs/learning/阶段0/` 下七篇文档齐全，每篇含五个小节，术语有解释，命令逐条讲解。

**Step 5b: 注释验收**

抽查 `backend/app/` 与 `frontend/src/`：每个方法/函数有 docstring 或头部注释，每个独立逻辑块有中文注释，不直观单行有行内注释。

**Step 6: Harness 自检**

Run（仓库根目录）: `pnpm harness:check && pnpm harness:status -- --match 阶段零`

Expected: 无警告，模块阶段变为 `READY_TO_DEV`（已完成开发）后按交付流程归档。

---

## Spec 覆盖自检

| Spec 章节 | 对应 Task |
|-----------|-----------|
| 6.1 后端基础搭建 | Task 2 |
| 6.2 PostgreSQL 环境 | Task 1、Task 3 |
| 6.3 Qdrant 环境 | Task 1、Task 4 |
| 6.4 前端基础工程 | Task 6 |
| 6.5 基础页面骨架 | Task 7、Task 8 |
| 6.6 配置与规范 | Task 1、Task 9 |
| 6.7 学习解释文档 | Task 1/2/4/6/7/9 内嵌 |
| 8. 测试与验收 | Task 0/3/5/10 |
