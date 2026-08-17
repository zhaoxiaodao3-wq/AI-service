# 01 · Function Calling 原理

## 做了什么

阶段 8 加入 Function Calling：模型在回答前可以“请求调用工具”，后端执行工具后把结果回填，模型再基于结果回答。

## 为什么

普通聊天只能靠模型内部知识回答“现在几点、算一道题、查我的文档”这类问题。工具调用让模型能访问真实数据，是 Agent 的基础能力。

## 原理

### OpenAI 工具格式

```json
{
  "type": "function",
  "function": {
    "name": "calculator",
    "description": "计算数学表达式",
    "parameters": { "type": "object", "properties": { "expression": { "type": "string" } } }
  }
}
```

模型返回 `tool_calls` 后，代码执行工具，再把 `role: tool` 消息追加回去。

## 命令解释

```powershell
$body = '{"messages":[{"role":"user","content":"请计算 2+3*4"}],"model":"glm-4-flash","use_tools":true}'
Invoke-RestMethod -Uri http://localhost:8000/api/chat/stream -Method Post -ContentType "application/json" -Body $body -Headers @{Authorization="Bearer $token"}
```

## 避坑

- 工具参数必须是合法 JSON，解析失败要兜底。
- 工具执行结果要截断，防止超长内容占满上下文。
- 模型不支持 tools 时要降级为普通聊天。
