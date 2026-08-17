# 03 · Agent 循环与前端展示

## 做了什么

聊天开启“工具”后，后端执行 Agent 循环：

```text
模型(带 tools) → 有 tool_calls → 执行工具 → 回填 tool 消息 → 再问模型（最多 3 轮）
                                  ↓ 无 tool_calls
                              直接输出回答
```

SSE 会输出 `tool_start` / `tool_done` 事件，前端显示“正在调用工具 / 工具完成”。

## 为什么

用户需要知道模型“做了什么”，否则看到突然出现的结果会困惑。展示工具调用过程既是可解释性，也是调试入口。

## 原理

```text
tool_start: {type, tool, arguments}
tool_done:  {type, tool, result}
```

前端 `chatStream` 增加 `onToolEvent` 回调，把提示渲染为工具气泡。

## 命令解释

```powershell
cd frontend
pnpm build
docker compose up -d --build frontend
```

聊天页打开“工具”开关，问“2+3*4 等于多少”，会看到工具调用过程。

## 避坑

- Agent 循环必须设最大轮数，防止死循环。
- 工具失败要降级为普通聊天，不能把错误暴露给用户。
- 工具调用日志要进 Loki/Grafana，方便排查。
