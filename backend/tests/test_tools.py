import asyncio
import ast

from app.tools.builtin import _safe_eval
from app.tools.registry import get_tool, list_tools


def test_safe_eval_calculator():
    assert _safe_eval(ast.parse("2 + 3 * 4", mode="eval")) == 14


def test_calculator_tool():
    tool = get_tool("calculator")
    assert tool is not None
    result = asyncio.run(tool.handler({"expression": "10 / 4"}, None))
    assert result.startswith("10 / 4")


def test_registry_openai_format():
    tools = list_tools()
    names = {t["function"]["name"] for t in tools}
    assert {
        "get_current_time",
        "calculator",
        "search_knowledge",
        "list_documents",
        "get_weather",
        "convert_currency",
    } <= names
