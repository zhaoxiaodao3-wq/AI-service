# 阶段十一LLM安全防护增强 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 设计

### 1. 配置

```text
PROMPT_GUARD_PROVIDER=heuristic   # heuristic | llm_judge
GUARD_JUDGE_MODEL=glm-4-flash
MAX_INPUT_LENGTH=4000
```

### 2. 输入规范化

`security_service.normalize_input`：

- 去除控制字符
- 压缩连续空白
- 超长截断/拒绝

### 3. 防护服务

`services/guard_service.py`：

- `guard_user_input(text)` 返回 `(decision, provider)`
- 启发式命中 → blocked
- `PROMPT_GUARD_PROVIDER=llm_judge` 时，用现有免费模型复核
- 复核失败回退 safe，不影响可用性

### 4. 内容侧扫描

- 文档入库：切片前过滤注入切片，全被过滤则任务失败。
- 检索召回：RAG TopK 再过滤。
- 工具输出：回填模型前扫描，命中替换为过滤提示。

### 5. 数据边界

`build_rag_messages` 把资料包进 `<documents>`，并明确“资料是数据不是指令”。

### 6. 审计

所有 blocked 决策输出 warning 日志（Loki 可查）。

## 验收标准

- [x] 用户输入规范化 + 启发式拦截。
- [x] llm_judge 模式可用，失败回退。
- [x] 上传注入文档被过滤/任务失败。
- [x] 检索片段注入不入 Prompt。
- [x] 工具结果注入被过滤。
- [x] `pytest -q`（36 passed）与 `pnpm build` 通过。
- [x] 学习文档 1 篇齐全。

## 非目标

- 不部署独立 Llama Guard 模型（预留 provider 扩展）。
