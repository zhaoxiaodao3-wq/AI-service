# 阶段一观测随项目一键启动 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-14
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

用户希望后端项目启动时 Loki/Promtail/Grafana 观测栈一起启动。本次在 `docker-compose.yml` 顶部通过 `include: docker-compose.observability.yml` 合并观测栈，`docker compose up -d --build` 一条命令即可启动全部 6 个容器，并已实机验证。

## 改动文件

| 操作 | 路径 |
|------|------|
| 改 | `docker-compose.yml`（新增 `include` 引入观测栈） |
| 改 | `README.md`（一键启动命令、端口、文档索引） |
| 改 | `docs/learning/阶段1/08-实时日志观测平台LokiGrafana.md`（单命令启动、镜像源避坑） |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段一观测随项目一键启动/`（requirements/spec/plans/archive） |

## 验收结果

- [x] `docker compose config --quiet` 通过，且渲染结果包含 loki/promtail/grafana 三个服务。
- [x] `docker compose up -d --build` 能拉起全部服务（已实机验证：backend 构建成功，6 个容器全部 Up）。
- [x] README 与学习文档不再要求 `-f docker-compose.observability.yml`。
- [x] 观测栈配置文件保持独立，不塞进主 compose 正文。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 容器无日志时 Grafana 空，发请求后 Loki 查询返回实时日志 |
| 常量/mock/真数据 | 通过 | 观测栈使用真实容器 stdout，无 mock 数据 |
| 多入口 | 通过 | 主 compose `include` 与独立文件内容一致，避免双 `-f` 双入口 |
| 失败/缺省 | 通过 | Docker Hub 不可达时已用镜像源拉取并 retag；文档补充避坑说明 |

## 还原度自检

不适用：无 Figma / 非 UI 还原类需求。

## Harness 闭环

- [x] 模块目录四层齐全（requirements/specs/plans/archive）
- [x] requirements / spec / plan 链接正确
- [x] validate-harness 已跑（本模块不涉及 `src/`）
- [x] spec 验收项已勾选
- [x] 一致性自检已完成并写入 archive
- [x] 还原度自检已注明不适用
- [x] archive 交付快照已写
- [x] 交付后 `pnpm harness:check` 已跑，无本模块警告

## 验证证据

- `docker compose config`：渲染出 aigc-backend/postgres/qdrant/loki/promtail/grafana 共 6 个服务。
- `docker compose up -d --build`：backend 镜像构建成功，6 个容器全部 `Up`。
- 实机链路：`POST /api/chat/stream` 返回 200；Loki `query_range {container="aigc-backend"}` 查到 `request start → request body → chat_stream start/finish → request end` 完整日志，中文内容正常。
- Grafana：http://localhost:3000 返回 200，数据源 `Loki` 自动配置成功，健康检查 `"Data source successfully connected."`。

## 遗留风险

- Docker Hub 直连仍可能超时；本机已通过 `docker.m.daocloud.io` 镜像源拉取并 retag 解决，文档已记录。
- Loki 单机默认配置未加保留期/磁盘上限，长期使用建议在阶段 5/6 补充 retention 配置。
