# 阶段五工程化完善与双模式兼容 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-17
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

完成工程化收口：模型按 `ai_models` 表独立配置（无配置回退 .env）、chat 接口 IP 限流（默认 30 次/分）、流式调用未出内容自动重试，并新增 `model_calls` 统计表与 `GET /api/stats` 汇总接口。

## 改动文件

| 操作 | 路径 |
|------|------|
| 改 | `backend/app/adapters/model_adapter.py`（按模型读 DB 配置 + 流式重试） |
| 新增 | `backend/app/core/rate_limit.py`（chat 限流中间件） |
| 新增 | `backend/app/repositories/model_call_repo.py`、`backend/app/services/stats_service.py`、`backend/app/api/stats.py` |
| 改 | `backend/app/models/entities.py`（ModelCall 表）、`backend/app/api/chat.py`（写统计）、`backend/app/api/router.py` |
| 改 | `backend/app/main.py`、`backend/app/core/config.py`、`.env*` |
| 改 | `backend/tests/test_persistence.py`、`backend/tests/test_model_adapter.py` |
| 新增 | `docs/learning/阶段5/01~04` 共 4 篇学习文档 |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段五工程化完善与双模式兼容/`（requirements/spec/plans/archive） |

## 验收结果

- [x] 聊天按 `ai_models` 配置调用模型，无配置回退 `.env`。
- [x] 流式失败在未输出内容时自动重试。
- [x] chat 接口限流返回 429。
- [x] `GET /api/stats` 返回调用次数/成功率/Token/按模型统计。
- [x] `pytest -q`（24 passed）与 `pnpm build` 通过。
- [x] 学习文档 4 篇齐全。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 无调用时 stats 返回 0/空；有调用时按模型聚合 |
| 常量/mock/真数据 | 通过 | 配置读取为真实 DB；测试 mock 凭证与统计 |
| 多入口 | 通过 | 官方/中转/DB 三路凭证统一收敛到 `_resolve_credentials` |
| 失败/缺省 | 通过 | 无 Key 返回 invalid_key；限流 429；流式中途断流不再重试 |

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

- 后端测试：`pytest -q` → 24 passed（统计接口、限流 429、模型适配、既有持久化/RAG/记忆）。
- 容器实测：聊天后 `GET /api/stats` 返回 `{"total_calls":1,"success_rate":1.0,"total_tokens":9,"by_model":{"glm-4-flash":{"calls":1,"success":1,"tokens":9}}}`。
- 学习文档：`docs/learning/阶段5/01~04` 四篇齐全。

## 遗留风险

- 限流/统计为单机内存实现，多实例部署需换 Redis 等共享方案。
- Token 为估算值（字符数/2），精确 usage 统计留待后续接入。
- 逐段 delta 日志量较大，生产需配置 Loki 保留期或采样。
