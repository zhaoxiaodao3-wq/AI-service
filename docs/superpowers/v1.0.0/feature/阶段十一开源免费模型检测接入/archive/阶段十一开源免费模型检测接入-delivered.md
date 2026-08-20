# 阶段十一开源免费模型检测接入 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-20
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

把 Guard 做成可切换 Provider：启发式快速拦截、免费 GLM 复核（`llm_judge`）、开源模型预留入口（`prompt_guard`），并提供模型下载脚本。

## 改动文件

| 操作 | 路径 |
|------|------|
| 新增 | `backend/app/services/guard_model.py`、`backend/scripts/download_prompt_guard.py` |
| 改 | `backend/app/services/guard_service.py`（Provider 切换与回退） |
| 改 | `backend/app/services/security_service.py`（is_suspicious） |
| 改 | `backend/app/core/config.py`、`.env*` |
| 改 | `backend/tests/test_security.py` |
| 新增 | `docs/learning/阶段11/05-开源免费模型检测接入.md` |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段十一开源免费模型检测接入/`（requirements/spec/plans/archive） |

## 验收结果

- [x] `heuristic` 快速拦截可用。
- [x] `llm_judge` 复核可用且失败回退。
- [x] `prompt_guard` 预留 Provider 可扩展。
- [x] 提供模型下载脚本。
- [x] `pytest -q`（37 passed）与 `pnpm build` 通过。
- [x] 学习文档 1 篇齐全。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 无模型/复核失败回退 safe |
| 常量/mock/真数据 | 通过 | llm_judge 容器实测返回 provider |
| 多入口 | 通过 | heuristic/llm_judge/prompt_guard 同一入口切换 |
| 失败/缺省 | 通过 | prompt_guard 未配置自动回退 |

## 还原度自检

不适用：无 Figma / 非 UI 还原类需求。

## Harness 闭环

- [x] 模块目录四层齐全（requirements/specs/plans/archive）
- [x] requirements / spec / plan 链接正确
- [x] 改 `src/` 前 validate-harness 已跑（阶段 READY_TO_DEV 后开发）
- [x] spec 验收项已勾选
- [x] 一致性自检已完成并写入 archive
- [x] 还原度自检已注明不适用
- [x] archive 交付快照已写
- [x] 交付后 `pnpm harness:check` 已跑，无本模块警告

## 验证证据

- 后端测试：`pytest -q` → 37 passed。
- 前端构建：`pnpm build` 通过。
- Docker 实测：`PROMPT_GUARD_PROVIDER=llm_judge` 下 `guard_user_input` 返回 `('safe', 'llm_judge')`，复核链路可用。
- 学习文档：`docs/learning/阶段11/05-开源免费模型检测接入.md`。

## 遗留风险

- `prompt_guard` 需先下载模型并安装 onnxruntime/transformers，当前未默认启用。
- `llm_judge` 增加一次模型调用，建议只对 suspicious 内容复核。
- hf-mirror 下载依赖网络，模型文件不提交仓库。
