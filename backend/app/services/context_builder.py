"""短期上下文构建器：拼接历史消息并手动做 Token 截断。"""


def estimate_tokens(text: str, model: str | None = None) -> int:
    """估算一段文本的 token 数。

    优先用 tiktoken（OpenAI 词表，按模型精确编码）；
    失败时用字符估算兜底：中文字符 1 个算 1 token，英文字母 4 个算 1 token，
    结果偏保守（偏大），宁可多截断也不溢出。
    """
    try:
        import tiktoken

        enc = (
            tiktoken.encoding_for_model(model)
            if model
            else tiktoken.get_encoding("cl100k_base")
        )
        return len(enc.encode(text))
    except Exception:
        cn = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
        en = sum(1 for ch in text if ch.isascii() and ch.isalpha())
        return cn + max(1, en // 4)


def truncate_messages(messages: list[dict], max_tokens: int) -> list[dict]:
    """按 token 上限截断消息列表。

    规则：
    - system 提示词单独保留，永远不参与删除；
    - 其余消息从最早开始删除，直到总 token 数不超过上限；
    - 若全部删完仍超限，保留最近一条消息。
    """
    if not messages:
        return messages
    system = [m for m in messages if m.get("role") == "system"]
    others = [m for m in messages if m.get("role") != "system"]
    # 只要整体估算超过上限，就删最早一条非 system 消息
    while others and estimate_tokens(str(system + others)) > max_tokens:
        others.pop(0)
    return system + others
