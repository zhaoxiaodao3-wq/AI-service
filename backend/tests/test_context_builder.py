from app.services.context_builder import estimate_tokens, truncate_messages


def test_estimate_tokens_works():
    """中文按字符估算，结果应大于等于字符数（保守偏大）。"""
    assert estimate_tokens("你好世界") >= 4


def test_truncate_keeps_system_and_drops_oldest():
    """超长上下文删除最早的非 system 消息，system 提示词必须保留。"""
    messages = [
        {"role": "system", "content": "你是助手"},
        {"role": "user", "content": "第1条"},
        {"role": "assistant", "content": "第2条"},
        {"role": "user", "content": "第3条"},
    ]
    result = truncate_messages(messages, max_tokens=2)
    assert result[0]["role"] == "system"
    assert all(m["content"] != "第1条" for m in result)


def test_truncate_short_messages_unchanged():
    """短对话不应被改动，原样返回。"""
    messages = [{"role": "user", "content": "你好"}]
    assert truncate_messages(messages, max_tokens=4000) == messages
