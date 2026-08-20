# 阶段十一开源免费模型检测接入 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 设计

### Provider

- `heuristic`：正则快速拦截，默认。
- `llm_judge`：`is_suspicious` 命中或 `PROMPT_GUARD_JUDGE_ALWAYS=true` 时用免费 GLM 复核。
- `prompt_guard`：配置模型目录后走 ONNX + transformers，未配置回退 heuristic。

### 下载脚本

`backend/scripts/download_prompt_guard.py` 通过 hf-mirror 下载开源模型到 `backend/guard_model/`。

## 验收标准

- [x] `heuristic` 快速拦截可用。
- [x] `llm_judge` 复核可用且失败回退。
- [x] `prompt_guard` 预留 Provider 可扩展。
- [x] 提供模型下载脚本。
- [x] `pytest -q`（37 passed）与 `pnpm build` 通过。
- [x] 学习文档 1 篇齐全。

## 非目标

- 默认不启用 `prompt_guard`，避免引入重型依赖。
