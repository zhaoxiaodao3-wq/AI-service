import asyncio

import pytest

from app.adapters.model_adapter import ChatRequest, ModelError, chat, stream_chat


def test_chat_returns_content(monkeypatch):
    """验证非流式 chat 返回统一 ChatResponse。

    用 mock 替换 litellm.acompletion，不真实调用模型，避免消耗额度。
    用 asyncio.run 执行协程，避免额外安装 pytest-asyncio 插件。
    """

    async def fake_acompletion(**kwargs):
        class FakeResp:
            choices = [
                type("C", (), {"message": type("M", (), {"content": "你好"})()})()
            ]
            usage = None

        return FakeResp()

    monkeypatch.setattr(
        "app.adapters.model_adapter.litellm.acompletion", fake_acompletion
    )

    async def run():
        return await chat(
            ChatRequest(
                model="glm-4-flash", messages=[{"role": "user", "content": "hi"}]
            )
        )

    resp = asyncio.run(run())
    assert resp.content == "你好"


def test_chat_no_key_raises_model_error(monkeypatch):
    """未配置 Key 时必须抛 ModelError，且 code 为 invalid_key。"""
    monkeypatch.setattr(
        "app.adapters.model_adapter._resolve_credentials", lambda: None
    )

    async def run():
        await chat(ChatRequest(model="glm-4-flash", messages=[]))

    with pytest.raises(ModelError) as exc:
        asyncio.run(run())
    assert exc.value.code == "invalid_key"


def test_stream_chat_yields_deltas(monkeypatch):
    """验证流式 stream_chat 逐段产出文本增量。"""

    async def fake_acompletion(**kwargs):
        class FakeChunk:
            choices = [
                type("C", (), {"delta": type("D", (), {"content": "你"})()})()
            ]

        # 返回一个异步生成器：模拟 litellm await 后得到的异步迭代器
        async def gen():
            yield FakeChunk()

        return gen()

    monkeypatch.setattr(
        "app.adapters.model_adapter.litellm.acompletion", fake_acompletion
    )

    async def run():
        return [
            c
            async for c in stream_chat(
                ChatRequest(model="glm-4-flash", messages=[])
            )
        ]

    chunks = asyncio.run(run())
    assert chunks == ["你"]
