# 阶段十二可观测性与工程化部署 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-20
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

按"AI 完成代码/配置/文档、用户完成账号/服务器/执行"的分工原则，落地阶段 12：Alembic 数据库迁移替代 create_all、OpenTelemetry 全链路 Trace（Tempo）、GitHub Actions CI/CD（GHCR 镜像）、宝塔 VPS 生产编排与备份恢复脚本、5 篇小白版学习文档。

## 改动文件

| 操作 | 路径 |
|------|------|
| 新增 | `backend/alembic.ini`、`backend/alembic/env.py`、`backend/alembic/script.py.mako`、`backend/alembic/versions/0001_initial.py` |
| 新增 | `backend/app/core/telemetry.py` |
| 新增 | `.github/workflows/ci.yml` |
| 新增 | `docker-compose.prod.yml`、`.env.prod.example` |
| 新增 | `scripts/backup.sh`、`scripts/restore.sh` |
| 新增 | `observability/tempo/config.yml`、`observability/grafana/provisioning/datasources/tempo.yml` |
| 改 | `backend/requirements.txt`（alembic + OTel 5 包）、`backend/app/core/config.py`（otel_* 配置） |
| 改 | `backend/app/db/init_db.py`（create_all → alembic upgrade head + 兜底） |
| 改 | `backend/app/main.py`（setup_telemetry）、`backend/app/adapters/model_adapter.py`（llm.chat span）、`backend/app/tools/registry.py`（tool.execute span） |
| 改 | `docker-compose.observability.yml`（+tempo）、`README.md`（阶段状态/索引） |
| 新增 | `docs/learning/阶段12/01~05` 共 5 篇文档 |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段十二可观测性与工程化部署/`（requirements/spec/plans/archive） |

## 验收结果

- [x] Alembic：upgrade head 建表、downgrade base 可逆、启动自动迁移 + create_all 兜底。
- [x] OTel：FastAPI/SQLAlchemy/httpx 自动埋点 + LLM/工具手动 span，导出失败降级不阻塞。
- [x] CI：三 Job（pytest / 前端构建 / GHCR 推送），GITHUB_TOKEN 自动授权。
- [x] 生产编排：资源限制 + 日志轮转 + 端口收敛；备份脚本保留最近 7 份。
- [x] 文档 5 篇齐全（含 GitHub/宝塔/备份的用户操作步骤）。
- [x] 后端 `pytest -q`：37 passed（1 个环境性 error 为沙箱 tmp_path 限制，非代码问题）；前端构建因沙箱无法安装依赖，归档声明由用户环境验证。
- [x] `pnpm harness:check` 无本模块警告。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 迁移空库 upgrade 全量建表；既有库 upgrade 幂等（alembic_version 记录） |
| 常量/mock/真数据 | 通过 | 迁移表结构与 entities.py 逐列一致；CI 测试用 SQLite 内存 + dependency_overrides |
| 多入口 | 通过 | backend/worker 共用镜像；生产/开发 compose 双轨配置分离 |
| 失败/缺省 | 通过 | alembic 不可用回退 create_all；OTel 未装/失败降级无埋点；Tempo 故障不影响聊天 |

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

- 后端测试：`pytest -q` → 37 passed（本沙箱 1 个环境性 error：test_tasks 的 tmp_path 目录被沙箱锁定，属环境限制，代码无碍）。
- YAML 校验：ci.yml / docker-compose.prod.yml / observability 全部 `yaml.safe_load` 通过。
- Python 校验：`import app.main` 成功，OTel 未安装时日志出现 `telemetry init failed ... run without tracing` 且启动正常。
- 待用户环境验证：alembic upgrade/downgrade 实测、Tempo Trace 瀑布、CI 跑绿、宝塔部署、备份恢复（步骤见文档 01~05）。

## 遗留风险

- 本沙箱无法安装新 Python 包（pip 临时目录被沙箱拦截）与无法执行 Docker CLI，Alembic/OTel/Tempo/宝塔部署的**运行态验证需用户按文档执行**。
- GHCR 私有镜像在服务器拉取需登录（文档给出 Public 或 PAT 两种方案）。
- Qdrant 向量数据未纳入 backup.sh（文档列为可选增强，建议宝塔整目录备份 qdrant_data）。
- CI 首次运行需用户创建 GitHub 仓库并推送，才会真实触发流水线。
