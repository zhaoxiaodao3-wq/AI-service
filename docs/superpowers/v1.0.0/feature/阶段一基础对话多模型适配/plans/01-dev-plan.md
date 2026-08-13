# 阶段一：基础 AI 对话 + 多模型对接 + 短期记忆 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans 按本计划逐任务执行，每完成一个任务汇报一次。

**Spec:** [specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 打通核心对话链路：LiteLLM 二次封装适配层（官方/中转双模式）、SSE 流式对话接口、短期上下文 Token 截断、前端流式打字与模型切换，并用智谱 GLM-4-Flash 完成真实联调。

**Architecture:** 前端内存维护 messages → `POST /api/chat/stream`（SSE）→ `chat_service` 拼接并截断上下文 → `model_adapter`（LiteLLM 异步调用）→ 逐段 `delta` 事件回传。模型配置全部走 `.env`，Key 只写本地环境，不提交仓库。

**Tech Stack:** FastAPI StreamingResponse + SSE、LiteLLM（acompletion/stream）、tiktoken（兜底字符估算）、Vue3 + TS + Element Plus、fetch ReadableStream。

**全局硬性规则：** 所有代码写清中文注释（方法 docstring、逻辑块注释、不直观单行行内注释）；每步完成同步写 `docs/learning/阶段1/` 学习文档；密钥只放本地 `.env`。

---

## Task 1: 统一模型适配层（ModelAdapter）

**Files:**
- Modify: `backend/app/adapters/model_adapter.py`
- Create: `backend/tests/test_model_adapter.py`

**Step 1: 写失败测试 `backend/tests/test_model_adapter.py`**

```python
import pytest

from app.adapters.model_adapter import ChatRequest, ModelError, chat, stream_chat


@pytest.mark.asyncio
async def test_chat_returns_content(monkeypatch):
    # 用 mock 的 acompletion 模拟 LiteLLM 返回，避免真实调用消耗额度
    async def fake_acompletion(**kwargs):
        class FakeResp:
            choices = [type("C", (), {"message": type("M", (), {"content": "你好"})})()]
            usage = None
        return FakeResp()

    monkeypatch.setattr("app.adapters.model_adapter.litellm.acompletion", fake_acompletion)
    resp = await chat(ChatRequest(model="glm-4-flash", messages=[{"role": "user", "content": "hi"}]))
    assert resp.content == "你好"


@pytest.mark.asyncio
async def test_chat_no_key_raises_model_error(monkeypatch):
    # 未配置 Key 时应抛 ModelError 而不是其他异常
    monkeypatch.setattr("app.adapters.model_adapter._resolve_credentials", lambda: None)
    with pytest.raises(ModelError) as exc:
        await chat(ChatRequest(model="glm-4-flash", messages=[]))
    assert exc.value.code == "invalid_key"


@pytest.mark.asyncio
async def test_stream_chat_yields_deltas(monkeypatch):
    async def fake_acompletion(**kwargs):
        class FakeChunk:
            choices = [type("C", (), {"delta": type("D", (), {"content": "你"})()})()]
        for _ in range(1):
            yield FakeChunk()

    monkeypatch.setattr("app.adapters.model_adapter.litellm.acompletion", fake_acompletion)
    chunks = [c async for c in stream_chat(ChatRequest(model="glm-4-flash", messages=[]))]
    assert chunks == ["你"]
```

**Step 2: 运行确认失败**

Run（backend 目录）: `pytest tests/test_model_adapter.py -v`

Expected: FAIL（接口未实现 / 函数不存在）。

**Step 3: 实现 `model_adapter.py`**

```python
from dataclasses import dataclass
from typing import AsyncIterator

import litellm
import httpx

from app.core.config import get_settings


class ModelError(Exception):
    """模型调用统一异常：code 给前端分类，message 给用户看。"""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


@dataclass
class ChatRequest:
    model: str
    messages: list[dict]
    temperature: float = 0.7


@dataclass
class ChatResponse:
    content: str
    usage: dict | None = None


def _resolve_credentials():
    """返回 (api_key, base_url)：中转配置优先，其次官方直连。

    设计上保证「官方/中转」切换只改 .env，不改代码。
    """
    s = get_settings()
    if s.llm_proxy_api_key and s.llm_proxy_base_url:
        return s.llm_proxy_api_key, s.llm_proxy_base_url
    if s.llm_api_key:
        return s.llm_api_key, s.llm_base_url or None
    return None


def _map_error(exc: Exception) -> ModelError:
    """把 LiteLLM/底层异常映射成统一 ModelError。"""
    if isinstance(exc, httpx.TimeoutException):
        return ModelError("timeout", "模型响应超时，请重试")
    text = str(exc).lower()
    if "auth" in text or "401" in text or "invalid api key" in text:
        return ModelError("invalid_key", "API Key 无效，请检查配置")
    if "quota" in text or "429" in text or "insufficient" in text:
        return ModelError("insufficient_quota", "账户额度不足，请稍后重试")
    if "stream" in text or "connection" in text:
        return ModelError("stream_broken", "连接中断，请重新发送")
    return ModelError("unknown", f"模型调用失败：{exc}")


async def chat(request: ChatRequest) -> ChatResponse:
    """非流式对话：返回完整内容。"""
    creds = _resolve_credentials()
    if not creds:
        raise ModelError("invalid_key", "未配置 API Key，请先填写 .env")
    api_key, base_url = creds
    try:
        resp = await litellm.acompletion(
            model=request.model,
            messages=request.messages,
            temperature=request.temperature,
            api_key=api_key,
            api_base=base_url,
        )
        content = resp.choices[0].message.content
        return ChatResponse(content=content, usage=dict(resp.usage) if resp.usage else None)
    except Exception as exc:
        raise _map_error(exc) from exc


async def stream_chat(request: ChatRequest) -> AsyncIterator[str]:
    """流式对话：逐段产出文本增量。"""
    creds = _resolve_credentials()
    if not creds:
        raise ModelError("invalid_key", "未配置 API Key，请先填写 .env")
    api_key, base_url = creds
    try:
        stream = await litellm.acompletion(
            model=request.model,
            messages=request.messages,
            temperature=request.temperature,
            api_key=api_key,
            api_base=base_url,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as exc:
        raise _map_error(exc) from exc
```

> 注意：`litellm` 对 Zhipu 使用 OpenAI 兼容协议，`api_base` 传 `https://open.bigmodel.cn/api/paas/v4`，模型名 `glm-4-flash`。

**Step 4: 运行测试通过**

Run: `pytest tests/test_model_adapter.py -v`

Expected: 3 passed。

**Step 5: Commit**

```bash
git add backend/app/adapters/model_adapter.py backend/tests/test_model_adapter.py
git commit -m "feat: 阶段一实现多模型统一适配层"
```

---

## Task 2: 模型配置与列表接口

**Files:**
- Modify: `backend/app/core/config.py`
- Create: `backend/app/api/models.py`
- Modify: `backend/app/api/router.py`
- Create: `backend/tests/test_models.py`

**Step 1: 配置字段与模型清单**

`config.py` 追加：

```python
# 可用模型清单（阶段 2 后改入库，现在静态配置）
models: list[str] = ["glm-4-flash", "gpt-4o", "gpt-4o-mini", "deepseek-chat", "claude-3-5-sonnet-20241022"]
# 短期上下文 token 上限，超过后删除最早消息
max_context_tokens: int = 4000
```

**Step 2: 写失败测试 `backend/tests/test_models.py`**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_models_returns_list():
    client = TestClient(app)
    resp = client.get("/api/models")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert "models" in body["data"]
    assert body["data"]["default_model"]
```

**Step 3: 实现 `backend/app/api/models.py`**

```python
from fastapi import APIRouter

from app.core.config import get_settings
from app.core.response import ok

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models")
async def list_models():
    """返回当前模式、可用模型清单与默认模型，供前端下拉渲染。"""
    s = get_settings()
    mode = "proxy" if (s.llm_proxy_api_key and s.llm_proxy_base_url) else "official"
    return ok({
        "mode": mode,
        "models": s.models,
        "default_model": s.llm_model or s.models[0],
    })
```

`router.py` 追加：`from app.api.models import router as models_router` + `api_router.include_router(models_router)`。

**Step 4: 测试通过**

Run: `pytest tests/test_models.py -v`

Expected: PASS。

**Step 5: Commit**

```bash
git add backend/app/core/config.py backend/app/api/models.py backend/app/api/router.py backend/tests/test_models.py
git commit -m "feat: 阶段一新增模型配置与列表接口"
```

---

## Task 3: SSE 流式对话接口

**Files:**
- Create: `backend/app/schemas/__init__.py`（已有）
- Create: `backend/app/schemas/chat.py`
- Create: `backend/app/services/chat_service.py`
- Create: `backend/app/api/chat.py`
- Modify: `backend/app/api/router.py`
- Create: `backend/tests/test_chat_stream.py`

**Step 1: 写失败测试 `backend/tests/test_chat_stream.py`**

```python
import json

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_chat_stream_emits_delta_and_done(monkeypatch):
    # mock 适配层：不发真实请求
    async def fake_stream(request):
        yield "你"
        yield "好"

    monkeypatch.setattr("app.services.chat_service.stream_chat", fake_stream)
    client = TestClient(app)
    resp = client.post(
        "/api/chat/stream",
        json={"messages": [{"role": "user", "content": "hi"}], "model": "glm-4-flash"},
    )
    assert resp.status_code == 200
    events = [json.loads(line[5:]) for line in resp.text.splitlines() if line.startswith("data: ")]
    kinds = [e["type"] for e in events]
    assert kinds == ["delta", "delta", "done"]


def test_chat_stream_invalid_body_returns_422():
    client = TestClient(app)
    resp = client.post("/api/chat/stream", json={})
    assert resp.status_code == 422
```

**Step 2: 运行确认失败**

Run: `pytest tests/test_chat_stream.py -v`

Expected: FAIL（模块/路由不存在）。

**Step 3: 实现 schema `backend/app/schemas/chat.py`**

```python
from pydantic import BaseModel, Field


class ChatStreamRequest(BaseModel):
    """流式对话请求体。"""

    messages: list[dict] = Field(..., min_length=1, description="历史消息 + 最新用户消息")
    model: str | None = Field(None, description="模型名，缺省用默认模型")
```

**Step 4: 实现服务层 `backend/app/services/chat_service.py`**

```python
from typing import AsyncIterator

from app.adapters.model_adapter import ChatRequest, stream_chat
from app.core.config import get_settings
from app.services.context_builder import truncate_messages


async def stream_chat_events(messages: list[dict], model: str | None) -> AsyncIterator[dict]:
    """编排对话：截断上下文 → 调用适配层 → 产出 SSE 事件。"""
    s = get_settings()
    selected = model or s.llm_model or s.models[0]
    # 手动截断：超长上下文删除最早消息，防止窗口溢出
    safe_messages = truncate_messages(messages, s.max_context_tokens)
    async for delta in stream_chat(ChatRequest(model=selected, messages=safe_messages)):
        yield {"type": "delta", "content": delta}
    yield {"type": "done", "usage": None}
```

**Step 5: 实现路由 `backend/app/api/chat.py`**

```python
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.adapters.model_adapter import ModelError
from app.schemas.chat import ChatStreamRequest
from app.services.chat_service import stream_chat_events

router = APIRouter(prefix="/api", tags=["chat"])


def sse(data: dict) -> str:
    """把事件 dict 序列化成 SSE 格式。"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/chat/stream")
async def chat_stream(req: ChatStreamRequest):
    """SSE 流式对话接口：逐段返回 delta，结束返回 done，异常返回 error。"""

    async def event_stream():
        try:
            async for event in stream_chat_events(req.messages, req.model):
                yield sse(event)
        except ModelError as exc:
            yield sse({"type": "error", "code": exc.code, "message": exc.message})
        except Exception:
            yield sse({"type": "error", "code": "unknown", "message": "服务器内部错误，请稍后重试"})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
```

`router.py` 追加 chat 路由。

**Step 6: 测试通过**

Run: `pytest tests/test_chat_stream.py -v`

Expected: 2 passed。

**Step 7: Commit**

```bash
git add backend/app/schemas/chat.py backend/app/services/chat_service.py backend/app/api/chat.py backend/app/api/router.py backend/tests/test_chat_stream.py
git commit -m "feat: 阶段一实现 SSE 流式对话接口"
```

---

## Task 4: 短期上下文与 Token 截断

**Files:**
- Create: `backend/app/services/context_builder.py`
- Create: `backend/tests/test_context_builder.py`

**Step 1: 写失败测试 `backend/tests/test_context_builder.py`**

```python
from app.services.context_builder import estimate_tokens, truncate_messages


def test_estimate_tokens_works():
    # 中文按字符估算，结果大于 0 且合理
    assert estimate_tokens("你好世界") >= 4


def test_truncate_keeps_system_and_drops_oldest():
    messages = [
        {"role": "system", "content": "你是助手"},
        {"role": "user", "content": "第1条"},
        {"role": "assistant", "content": "第2条"},
        {"role": "user", "content": "第3条"},
    ]
    result = truncate_messages(messages, max_tokens=2)
    # system 必须保留
    assert result[0]["role"] == "system"
    # 最早的非 system 消息被删除
    assert all(m["content"] != "第1条" for m in result)


def test_truncate_short_messages_unchanged():
    messages = [{"role": "user", "content": "你好"}]
    assert truncate_messages(messages, max_tokens=4000) == messages
```

**Step 2: 运行确认失败**

Run: `pytest tests/test_context_builder.py -v`

Expected: FAIL（模块不存在）。

**Step 3: 实现 `backend/app/services/context_builder.py`**

```python
def estimate_tokens(text: str, model: str | None = None) -> int:
    """估算文本 token 数：优先 tiktoken，失败用字符估算兜底。"""
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model(model) if model else tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        # 兜底：中文按 1 字符 1 token，英文按 4 字符 1 token，保守偏大
        cn = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
        en = sum(1 for ch in text if ch.isascii() and ch.isalpha())
        return cn + max(1, en // 4)


def truncate_messages(messages: list[dict], max_tokens: int) -> list[dict]:
    """按 token 上限截断：保留 system，删除最早的非 system 消息。"""
    if not messages:
        return messages
    # 系统提示词单独拎出来，永远保留
    system = [m for m in messages if m.get("role") == "system"]
    others = [m for m in messages if m.get("role") != "system"]
    while others and estimate_tokens(str(system + others)) > max_tokens:
        others.pop(0)  # 删最早
        if not others:
            break
    return system + others
```

**Step 4: 测试通过**

Run: `pytest tests/test_context_builder.py -v`

Expected: 3 passed。

**Step 5: Commit**

```bash
git add backend/app/services/context_builder.py backend/tests/test_context_builder.py
git commit -m "feat: 阶段一实现短期上下文 Token 截断"
```

---

## Task 5: 前端流式对话对接

**Files:**
- Create: `frontend/src/api/chatStream.ts`
- Modify: `frontend/src/views/ChatView.vue`
- Modify: `frontend/src/layouts/MainLayout.vue`（豆包风格左右布局）

**Step 1: 创建 `frontend/src/api/chatStream.ts`**

```ts
// 流式对话：用 fetch 读取 SSE 事件（EventSource 不支持 POST，所以用 ReadableStream）
export async function chatStream(
  messages: { role: string; content: string }[],
  model: string,
  handlers: {
    onDelta: (content: string) => void
    onDone: () => void
    onError: (code: string, message: string) => void
  },
) {
  const resp = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages, model }),
  })
  if (!resp.ok || !resp.body) {
    handlers.onError('http', `请求失败（${resp.status}）`)
    return
  }

  const reader = resp.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    // SSE 事件以空行分隔，逐条解析
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''
    for (const part of parts) {
      const line = part.split('\n').find((l) => l.startsWith('data: '))
      if (!line) continue
      const event = JSON.parse(line.slice(6))
      if (event.type === 'delta') handlers.onDelta(event.content)
      else if (event.type === 'done') handlers.onDone()
      else if (event.type === 'error') handlers.onError(event.code, event.message)
    }
  }
}
```

**Step 2: 改造 `frontend/src/views/ChatView.vue`**

- 状态：`sessions`（内存会话列表）、`activeSessionId`、`messages`、`model`、`models`、`loading`、`errorMsg`、`attachments`。
- 挂载时 `request.get('/models')` 拉取模型列表。
- `newSession()`：创建新会话 `{id, title:"新会话 N", messages:[]}` 并激活。
- `switchSession(id)`：切换 `activeSessionId`，聊天区显示对应 messages。
- `send()`：追加用户消息 → 追加空 AI 消息 → `chatStream` → `onDelta` 追加内容 → 完成后 `loading=false`。
- 附件：`onFileSelected` / `onImageSelected` 读取文件并加入 `attachments`（图片用 `URL.createObjectURL` 预览），随消息携带 `attachments` 字段。
- `onError`：AI 消息内容改为 `[错误] message`，`loading=false`。
- 模板：左侧会话菜单（新会话按钮 + 历史会话列表）+ 右侧消息列表 + 输入框（上传文件/图片按钮、附件条、发送按钮）+ 顶部模型下拉。
- 所有逻辑块加中文注释。

**Step 2b: 改造 `frontend/src/layouts/MainLayout.vue` 为左右布局**

- `el-aside`（约 240px）：品牌 + 新会话按钮 + 历史会话列表。
- 右侧 `el-container`：header（模型下拉/会话标题）+ main（`router-view`）。
- 会话状态由 `ChatView` 管理；布局组件通过插槽/全局事件与 `ChatView` 协作（阶段 1 简化：会话 UI 直接放在 `ChatView` 内，`MainLayout` 只保留顶部导航）。

> 简化决策：为减少跨组件状态复杂度，阶段 1 将「左侧会话菜单」放在 `ChatView` 内部实现；`MainLayout` 保持顶部导航 + 内容区。

**Step 3: 验证**

Run: `pnpm build`

Expected: 类型检查与构建通过。

**Step 4: Commit**

```bash
git add frontend/src/api/chatStream.ts frontend/src/views/ChatView.vue
git commit -m "feat: 阶段一前端流式对话对接"
```

---

## Task 6: 异常容错完善与智谱真实联调

**Files:**
- Modify: `frontend/src/views/ChatView.vue`（错误态 UI）
- Modify: `backend/.env`（本地，不入库：智谱 Key/BaseURL/模型）

**Step 1: 本地配置智谱模型**

在 `backend/.env` 填入（**不提交 Git**）：

```dotenv
LLM_PROVIDER=zhipu
LLM_API_KEY=<用户提供的智谱 Key>
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4-flash
```

**Step 2: 真实联调**

启动后端后调用：

```bash
curl -N -X POST http://localhost:8000/api/chat/stream -H "Content-Type: application/json" -d "{\"messages\":[{\"role\":\"user\",\"content\":\"用一句话介绍你自己\"}],\"model\":\"glm-4-flash\"}"
```

Expected: 逐段 `data: {"type":"delta",...}` 输出，最后 `done`。

**Step 3: 前端浏览器验证**

- http://localhost:5173/chat 发送消息，观察打字效果。
- 切换模型下拉、发送错误消息（如清空 Key 后）验证错误提示。

**Step 4: 修正发现的问题并提交**

```bash
git add frontend backend
git commit -m "fix: 阶段一异常容错与流式联调修正"
```

---

## Task 7: 学习文档、注释自检与交付归档

**Files:**
- Create: `docs/learning/阶段1/01~06` 六篇
- Create: 模块 archive 交付快照

**Step 1: 写六篇学习文档**

```text
01-LiteLLM与模型适配层原理.md
02-官方Key与中转Key的区别.md
03-SSE流式传输原理.md
04-LLM上下文窗口与Token截断.md
05-前端流式渲染与打字效果.md
06-对话异常容错设计.md
```

每篇五小节：做了什么 / 为什么 / 原理 / 命令解释 / 避坑。

**Step 2: 全量验收**

Run:
```bash
cd backend && pytest -q
cd ../frontend && pnpm build
```

Expected: 全部通过。

**Step 3: 写交付归档**

`docs/superpowers/v1.0.0/feature/阶段一基础对话多模型适配/archive/阶段一基础对话多模型适配-delivered.md`，含：改动摘要、改动文件、验收勾选、一致性自检、还原度自检（不适用：无 Figma / 非 UI）、Harness 闭环。

**Step 4: Harness 校验与提交**

```bash
pnpm harness:check
pnpm harness:status -- --match 阶段一
git add .
git commit -m "docs: 阶段一交付归档"
```

Expected: 状态变为 `DELIVERED`，无警告。

---

## Spec 覆盖自检

| Spec 章节 | 对应 Task |
|-----------|-----------|
| 5 模型适配层协议 | Task 1 |
| 4.1 模型列表接口 | Task 2 |
| 4.2 SSE 流式接口 | Task 3 |
| 6 上下文与 Token 截断 | Task 4 |
| 7 前端流式渲染 | Task 5 |
| 8 错误处理 | Task 3、Task 6 |
| 12 学习文档清单 | Task 7 |
