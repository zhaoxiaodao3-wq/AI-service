import ast
import datetime
import operator
from urllib.parse import quote

import httpx

from app.adapters.model_adapter import embed_texts
from app.db.session import SessionLocal
from app.repositories import document_repo, vector_repo


async def get_current_time(arguments: dict, user_id: int | None) -> str:
    """返回当前本地时间。"""
    return datetime.datetime.now().astimezone().isoformat()


_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _safe_eval(node: ast.AST):
    """只允许常量与基础四则运算的 AST 求值，禁止 eval/import。"""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        op = _BINOPS.get(type(node.op))
        if op is None:
            raise ValueError("不支持的运算符")
        return op(_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op = _UNARYOPS.get(type(node.op))
        if op is None:
            raise ValueError("不支持的运算符")
        return op(_safe_eval(node.operand))
    raise ValueError("只支持数字四则运算表达式")


async def calculator(arguments: dict, user_id: int | None) -> str:
    """安全计算数学表达式。"""
    expr = str(arguments.get("expression", ""))
    try:
        result = _safe_eval(ast.parse(expr, mode="eval"))
        return f"{expr} = {result}"
    except Exception as exc:
        return f"计算失败：{exc}"


async def search_knowledge(arguments: dict, user_id: int | None) -> str:
    """检索当前用户知识库，返回最相关的片段。"""
    if user_id is None:
        return "无权限：缺少用户上下文"
    query = str(arguments.get("query", ""))
    if not query:
        return "请提供查询内容"
    vector = (await embed_texts([query]))[0]
    hits = vector_repo.search_documents(user_id, vector, top_k=3, score_threshold=0.2)
    if not hits:
        return "知识库中没有找到相关内容"
    return "\n".join(
        f"[{score:.3f}] {hit.payload.get('text', '')}"
        for hit, score in [(h, h.score) for h in hits]
    )


async def list_documents(arguments: dict, user_id: int | None) -> str:
    """返回当前用户的文档列表。"""
    if user_id is None:
        return "无权限：缺少用户上下文"
    with SessionLocal() as db:
        docs = document_repo.list_documents(db, user_id)
    if not docs:
        return "当前用户暂无文档"
    return "\n".join(f"- {d.filename}（{d.chunk_count} 切片）" for d in docs)


async def get_weather(arguments: dict, user_id: int | None) -> str:
    """按城市查询当前天气（wttr.in，免费无 Key）。"""
    city = str(arguments.get("city") or "北京").strip()
    try:
        async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
            resp = await client.get(f"https://wttr.in/{quote(city)}?format=j1")
            data = resp.json()
        current = data["current_condition"][0]
        description = current["weatherDesc"][0]["value"]
        return (
            f"{city} 当前天气：{description}，{current['temp_C']}°C，"
            f"体感 {current['FeelsLikeC']}°C，湿度 {current['humidity']}%，"
            f"风速 {current['windspeedKmph']} km/h"
        )
    except Exception as exc:
        return f"天气查询失败：{exc}"


async def convert_currency(arguments: dict, user_id: int | None) -> str:
    """按实时汇率换算（open.er-api.com，免费无 Key）。"""
    try:
        amount = float(arguments.get("amount", 1))
        source = str(arguments.get("from", "USD")).upper()
        target = str(arguments.get("to", "CNY")).upper()
    except (TypeError, ValueError):
        return "汇率参数无效"
    try:
        async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
            resp = await client.get(f"https://open.er-api.com/v6/latest/{source}")
            data = resp.json()
        rate = data["rates"][target]
        return f"{amount} {source} = {amount * rate:.4f} {target}（汇率 {rate}）"
    except Exception as exc:
        return f"汇率查询失败：{exc}"
