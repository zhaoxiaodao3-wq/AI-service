# 阶段十一开源免费模型检测接入 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** Guard Provider 可切换 + 免费模型复核。

**Architecture:** guard_service 分支 + guard_model 可选模型 + 下载脚本。

**Tech Stack:** FastAPI + GLM + ONNX/transformers（可选）。

---

### Task 1: Provider 与模型入口

**Files:**
- Modify: `backend/app/services/guard_service.py`、`security_service.py`
- Create: `backend/app/services/guard_model.py`、`backend/scripts/download_prompt_guard.py`
- Modify: `backend/app/core/config.py`、`.env*`

### Task 2: 测试、实测、文档、归档

**Files:**
- Modify: `backend/tests/test_security.py`
- Create: `docs/learning/阶段11/05-开源免费模型检测接入.md`
