# 阶段一SSE逐段输出日志 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-14
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

用户希望在 Grafana Live Tail 中看到 AI 流式输出一段一段返回，而不是只有最终汇总。本次在 `chat.py` 的 SSE 事件循环中为每个 `delta` 增加 INFO 日志，并保留末尾 `chat_stream finish` 完整汇总。

## 改动文件

| 操作 | 路径 |
|------|------|
| 改 | `backend/app/api/chat.py`（每个 delta 输出分片内容/分片字符数/累计字符数） |
| 改 | `backend/tests/test_access_log.py`（断言两条 delta 日志与累计字符数递增） |
| 改 | `docs/learning/阶段1/08-实时日志观测平台LokiGrafana.md`（delta 日志示例） |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段一SSE逐段输出日志/`（requirements/spec/plans/archive） |

## 验收结果

- [x] 每个 delta 到达时输出 `chat_stream delta` 日志，含分片内容、分片字符数、累计字符数。
- [x] 流结束仍输出 `chat_stream finish` 完整汇总。
- [x] `pytest -q` 通过（13 passed）。
- [x] Docker 后端重建后，Loki 查询能看到逐段 delta 日志。
- [x] SSE 接口协议与前端流式渲染行为不变。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 无 delta 时无逐段日志；有返回时每条分片一行 |
| 常量/mock/真数据 | 通过 | 单测 mock 适配层验证日志结构；真实 GLM 流式返回同样生效 |
| 多入口 | 通过 | 本地 uvicorn 与 Docker 容器共用同一 chat.py，日志一致 |
| 失败/缺省 | 通过 | 错误分支仍走 error 事件，不产生 delta 日志；finish 统计 error 数 |

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

- 后端测试：`pytest -q` → 13 passed。
- Docker 后端已重建并运行，真实聊天请求后 Loki `query_range {container="aigc-backend"} |= "chat_stream delta"` 返回逐段日志：
  ```text
  chat_stream delta chunk='我' chunk_chars=1 total_chars=66
  chat_stream delta chunk='同时' chunk_chars=2 total_chars=64
  chat_stream finish events={'delta': 43, 'done': 1, 'error': 0} chars=87 preview='...'
  ```

## 遗留风险

- 每条 delta 都打日志会增加日志量，本地观测可接受；生产环境如需降低噪音，可加采样或改为每 N 条合并（阶段 5/6）。
