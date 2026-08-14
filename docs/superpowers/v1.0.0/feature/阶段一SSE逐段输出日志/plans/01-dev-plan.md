# 阶段一SSE逐段输出日志 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 让 Grafana Live Tail 实时看到 AI 每段输出，同时保留末尾完整汇总。

**Architecture:** 在现有 SSE 事件循环中为每个 delta 输出 INFO 日志，汇总逻辑保持不变。

**Tech Stack:** Python FastAPI + logging。

---

### Task 1: 逐段日志实现

**Files:**
- Modify: `backend/app/api/chat.py`

**Step 1:** 在 `kind == "delta"` 分支增加：
```python
chunk = event.get("content", "")
chars += len(chunk)
preview = (preview + chunk)[:80]
logger.info(
    "chat_stream delta chunk='%s' chunk_chars=%d total_chars=%d",
    chunk.replace("\n", " ")[:80],
    len(chunk),
    chars,
)
```

**Step 2:** 保留 finish 汇总日志。

### Task 2: 测试更新

**Files:**
- Modify: `backend/tests/test_access_log.py`

**Step 1:** 在 chat 日志测试中追加断言两条 `chat_stream delta` 存在且 `total_chars` 递增。

**Step 2:** 运行：
```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
```
期望：全部通过。

### Task 3: Docker 重建与 Loki 实测

**Step 1:** 重建并重启后端：
```powershell
docker compose up -d --build backend
```

**Step 2:** 发一条聊天请求，用 Loki `query_range {container="aigc-backend"}` 确认逐段 delta 与 finish 汇总都在。

### Task 4: 归档

**Step 1:** 勾选 spec 验收项，写 archive，跑 `pnpm harness:check`。
