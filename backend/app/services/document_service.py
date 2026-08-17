import io

from app.core.exceptions import AppError
from app.models.entities import Document
from app.repositories import document_repo, user_repo

ALLOWED_TYPES = {".txt", ".md", ".pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def parse_file(content: bytes, filename: str) -> str:
    """按扩展名解析文档内容：txt/md 直接解码，pdf 用 pypdf 提取。"""
    name = filename.lower()
    if not any(name.endswith(t) for t in ALLOWED_TYPES):
        raise AppError(400, "仅支持 PDF/TXT/MD 文件")
    if name.endswith(".txt") or name.endswith(".md"):
        return content.decode("utf-8", errors="replace")
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def build_rag_messages(
    messages: list[dict], hits: list | None = None, memories: list | None = None
) -> list[dict]:
    """把检索片段与历史记忆拼进系统提示词，保留用户上下文。"""
    parts = []
    if memories:
        memory_text = "\n".join(
            f"[记忆{i + 1}] {m.payload.get('text', '')}"
            for i, m in enumerate(memories)
        )
        parts.append(f"历史记忆（跨会话）：\n{memory_text}")
    if hits:
        document_text = "\n".join(
            f"[片段{i + 1}] {hit.payload.get('text', '')}"
            for i, hit in enumerate(hits)
        )
        parts.append(f"知识库资料：\n{document_text}")
    context = "\n\n".join(parts)
    system = {
        "role": "system",
        "content": (
            "你是 AI 助手。请结合以下历史记忆与知识库资料回答用户问题，"
            f"资料不足时如实说明：\n\n{context}"
        ),
    }
    return [system] + [m for m in messages if m.get("role") != "system"]


def get_document(db, document_id: int) -> Document:
    user = user_repo.get_default_user(db)
    document = document_repo.get_document(db, document_id, user.id)
    if document is None:
        raise AppError(404, "文档不存在")
    return document
