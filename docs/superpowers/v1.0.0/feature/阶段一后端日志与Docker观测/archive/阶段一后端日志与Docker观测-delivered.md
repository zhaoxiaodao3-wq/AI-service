# 阶段一后端日志与Docker观测 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-13
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

用户希望用 Docker 客户端查看“前端发请求、后端返回响应”的日志。本次新增 FastAPI 请求/响应日志中间件与 SSE 流式事件日志，并把 backend 加入 Docker Compose；本地开发启动方式不变，Docker 网络恢复后即可 `docker compose logs -f backend` 看到完整链路。

## 改动文件

| 操作 | 路径 |
|------|------|
| 新增 | `backend/app/core/access_log.py`（ASGI 请求/响应日志中间件） |
| 改 | `backend/app/main.py`（挂载日志中间件） |
| 改 | `backend/app/api/chat.py`（chat_stream start/finish/错误日志与事件统计） |
| 新增 | `backend/tests/test_access_log.py` |
| 新增 | `backend/Dockerfile`、`backend/.dockerignore` |
| 改 | `docker-compose.yml`（新增 backend 服务，env_file + 容器网络覆盖 DB/Qdrant 地址） |
| 新增 | `docs/learning/阶段1/07-Docker日志查看与请求响应链路.md` |
| 改 | `README.md`（查看日志小节、学习文档索引、阶段表状态） |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段一后端日志与Docker观测/`（requirements/spec/plans/archive） |

## 验收结果

- [x] `pytest -q` 全部通过（原 11 个 + 新增日志测试）。
- [x] 请求日志包含 method/path/client/status/duration/body 摘要。
- [x] chat SSE 日志包含 start/finish、事件统计、字符数、预览；错误场景记录错误码。
- [x] `docker compose config` 校验通过。
- [ ] backend 镜像可构建并健康启动（当前环境 Docker Hub 不可达，配置已就绪，待网络恢复后验证）。
- [x] 本地 uvicorn 启动方式与接口行为不变；本地真实联调已看到完整请求/响应日志。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 无请求体记录 `body_bytes=0`，有请求体输出摘要；SSE 事件统计从 0 开始累加 |
| 常量/mock/真数据 | 通过 | 日志摘要读取真实请求体；单测 mock 适配层但请求/日志链路为真实代码 |
| 多入口 | 通过 | 本地 uvicorn 与 Docker 容器运行同一份代码，仅数据库/Qdrant 地址由环境变量区分 |
| 失败/缺省 | 通过 | `ModelError` 记录 warning + error 事件；未知异常记录堆栈；无 Key 时走 error 分支不崩 |

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

- 后端测试：`backend\venv\Scripts\python.exe -m pytest -q` → 13 passed。
- 本地真实联调：`POST /api/chat/stream` 返回 200，日志完整出现 `request start → request body → chat_stream start → chat_stream finish → request end`，SSE 事件统计 `events={'delta': 6, 'done': 1, 'error': 0} chars=11`。
- Docker：`docker compose config --quiet` 通过；backend 服务定义、环境覆盖、depends_on 校验无误。

## 遗留风险

- 当前机器 Docker Hub 无法连通（`registry-1.docker.io` 超时），backend 镜像构建与容器日志尚未实机验证；配置已就绪，网络恢复后执行 `docker compose up -d --build backend` 即可。
- `fastapi.testclient` 有 Starlette 弃用警告，不影响功能（阶段 5 可切 httpx2）。
- 本地 PowerShell 直接构造中文请求体时若编码不当，日志预览可能显示乱码；浏览器 fetch 与 Docker 内 UTF-8 环境不受影响。
