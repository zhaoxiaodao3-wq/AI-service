from app.models.entities import ModelCall


def get_stats(db) -> dict:
    """汇总模型调用统计：总次数、成功率、Token 与按模型分布。"""
    calls: list[ModelCall] = db.query(ModelCall).all()
    total = len(calls)
    success = sum(1 for c in calls if c.success)
    tokens = sum(c.token_count or 0 for c in calls)

    by_model: dict[str, dict[str, int]] = {}
    for c in calls:
        item = by_model.setdefault(
            c.model or "unknown", {"calls": 0, "success": 0, "tokens": 0}
        )
        item["calls"] += 1
        item["success"] += 1 if c.success else 0
        item["tokens"] += c.token_count or 0

    return {
        "total_calls": total,
        "success_rate": round(success / total, 4) if total else 0.0,
        "total_tokens": tokens,
        "by_model": by_model,
    }
