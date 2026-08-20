# 阶段十异步任务与文件处理 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-20
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

引入 Redis + RQ，把文档上传改为异步：上传立即返回任务，worker 容器后台完成解析/切片/向量化/入库；新增任务状态接口与前端轮询。

## 改动文件

| 操作 | 路径 |
|------|------|
| 新增 | `backend/app/repositories/document_task_repo.py` |
| 新增 | `backend/app/services/document_processing.py`、`backend/app/services/task_queue.py` |
| 新增 | `backend/scripts/worker.py` |
| 改 | `backend/app/models/entities.py`（DocumentTask）、`backend/app/api/documents.py` |
| 改 | `backend/app/core/config.py`、`backend/requirements.txt`、`.env*` |
| 改 | `frontend/src/views/UploadView.vue`（任务轮询） |
| 改 | `docker-compose.yml`（redis + worker + uploads 卷） |
| 新增 | `backend/tests/test_tasks.py`，更新 `backend/tests/test_rag.py` |
| 新增 | `docs/learning/阶段10/01~02` 共 2 篇学习文档 |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段十异步任务与文件处理/`（requirements/spec/plans/archive） |

## 验收结果

- [x] 上传立即返回，不阻塞请求。
- [x] worker 能完成解析/切片/向量化/入库。
- [x] 任务状态可查询，失败有 error。
- [x] 前端展示处理进度。
- [x] `pytest -q`（32 passed）与 `pnpm build` 通过。
- [x] 学习文档 2 篇齐全。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 无任务 pending；有任务 completed 且 chunk_count>0 |
| 常量/mock/真数据 | 通过 | 单测 mock Embedding/Qdrant；容器实测真实 worker 完成 |
| 多入口 | 通过 | 同步上传逻辑抽到 worker，接口行为不变 |
| 失败/缺省 | 通过 | worker 异常写入 failed+error，前端轮询展示 |

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

- 后端测试：`pytest -q` → 32 passed。
- 前端构建：`pnpm build` 通过。
- Docker 实测：上传后任务 pending → 轮询 completed，chunk_count=1，Qdrant/PG 均入库。

## 遗留风险

- 临时文件存共享卷，多实例部署需换对象存储。
- RQ 任务无优先级/延迟队列，生产可扩展。
- 批量导入与增量更新 UI 未做，后续可扩展。
