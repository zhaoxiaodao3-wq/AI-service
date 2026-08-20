from dataclasses import dataclass

from app.adapters.model_adapter import embed_texts, rerank
from app.core.config import get_settings
from app.repositories import document_chunk_repo, document_repo, vector_repo
from app.services.security_service import is_prompt_injection


@dataclass
class RagHit:
    doc_id: int
    chunk_index: int
    text: str
    score: float = 0.0
    filename: str = ""

    @property
    def payload(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "chunk_index": self.chunk_index,
            "text": self.text,
        }


async def hybrid_search(
    db, user_id: int, query: str, top_k: int = 3
) -> list[RagHit]:
    """向量 + 关键词混合检索，RRF 融合，可选 Rerank 精排。"""
    s = get_settings()
    vector = (await embed_texts([query]))[0]

    vector_hits = vector_repo.search_documents(
        user_id,
        vector,
        top_k=s.vector_retrieve_k,
        score_threshold=0.0,
    )
    keyword_rows = document_chunk_repo.search_keyword(
        db, user_id, query, limit=s.keyword_retrieve_k
    )

    candidates: dict[tuple[int, int], dict] = {}
    for rank, hit in enumerate(vector_hits):
        key = (hit.payload["doc_id"], hit.payload["chunk_index"])
        item = candidates.setdefault(
            key, {"text": hit.payload["text"], "vector_rank": None, "keyword_rank": None}
        )
        item["vector_rank"] = rank

    for rank, row in enumerate(keyword_rows):
        key = (row.document_id, row.chunk_index)
        item = candidates.setdefault(
            key, {"text": row.content, "vector_rank": None, "keyword_rank": None}
        )
        item["keyword_rank"] = rank

    hits: list[RagHit] = []
    for (doc_id, chunk_index), item in candidates.items():
        score = 0.0
        if item["vector_rank"] is not None:
            score += 1.0 / (s.rrf_k + item["vector_rank"] + 1)
        if item["keyword_rank"] is not None:
            score += 1.0 / (s.rrf_k + item["keyword_rank"] + 1)
        hits.append(
            RagHit(
                doc_id=doc_id,
                chunk_index=chunk_index,
                text=item["text"],
                score=score,
            )
        )

    hits.sort(key=lambda h: h.score, reverse=True)

    if s.rerank_enabled and hits:
        scores = await rerank(query, [h.text for h in hits])
        if scores is not None:
            for hit, score in zip(hits, scores):
                hit.score = score
            hits.sort(key=lambda h: h.score, reverse=True)

    hits = [h for h in hits if not is_prompt_injection(h.text)]
    hits = hits[:top_k]
    filenames = document_repo.get_filenames_by_ids(
        db, [h.doc_id for h in hits]
    )
    for hit in hits:
        hit.filename = filenames.get(hit.doc_id, "")
    return hits
