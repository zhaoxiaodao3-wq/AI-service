def split_text(
    text: str, chunk_size: int = 500, chunk_overlap: int = 50
) -> list[str]:
    """手动文本切片：固定窗口 + 步长重叠，返回非空片段列表。"""
    text = text.strip()
    if not text:
        return []

    step = max(1, chunk_size - chunk_overlap)
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        if start + chunk_size >= len(text):
            break
        start += step
    return [c.strip() for c in chunks if c.strip()]
