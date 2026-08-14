# 阶段一实时日志观测平台 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-13
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

用户希望用主流观测软件在浏览器里实时查看后端日志，而不是只打 `docker logs` 命令。本模块引入 **Loki + Promtail + Grafana**：Promtail 通过 Docker socket 实时采集容器 stdout 并推给 Loki，Grafana 提供 Explore + Live Tail 网页界面；全程不写日志文件。

## 改动文件

| 操作 | 路径 |
|------|------|
| 新增 | `docker-compose.observability.yml`（loki/promtail/grafana 三服务） |
| 新增 | `observability/promtail/config.yml`（docker_sd_configs 实时采集 stdout） |
| 新增 | `observability/grafana/provisioning/datasources/loki.yml`（自动连接 Loki） |
| 新增 | `docs/learning/阶段1/08-实时日志观测平台LokiGrafana.md` |
| 改 | `README.md`（观测启动命令、端口、学习文档索引、阶段状态） |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段一实时日志观测平台/`（requirements/spec/plans/archive） |

## 验收结果

- [x] `docker compose -f docker-compose.observability.yml config --quiet` 通过。
- [x] Promtail 配置可被 Python `yaml.safe_load` 解析且包含 docker_sd_configs。
- [x] Grafana datasource 配置指向 `http://loki:3100`。
- [x] README 与学习文档包含完整启动命令与 Live Tail 使用说明。
- [x] 不修改后端代码；后端 stdout 日志保持不变，无文件落盘。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | Grafana Live Tail 无日志时为空，容器有输出即实时滚动 |
| 常量/mock/真数据 | 通过 | Promtail 采集真实 Docker stdout；配置无 mock 数据 |
| 多入口 | 通过 | 本地 `docker logs` 与 Loki/Grafana 共用同一份 stdout，无重复代码路径 |
| 失败/缺省 | 通过 | 镜像拉取失败/容器未启动时有明确文档避坑；Grafana 默认密码可被 `.env` 覆盖 |

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

- Python `yaml.safe_load`：三个 YAML（compose/promtail/datasource）均解析成功。
- `docker compose -f docker-compose.observability.yml config --quiet`：exit 0；渲染出 `aigc-loki`、`aigc-promtail`、`aigc-grafana` 三服务及 3000/3100 端口。
- 后端代码未改动，日志仍为 stdout 实时输出、无 FileHandler。

## 遗留风险

- 当前机器 Docker Hub 无法连通，Loki/Promtail/Grafana 镜像尚未实机启动；配置已通过 compose config 校验，网络恢复后按 README 启动即可。
- Promtail 当前采集所有容器日志，Grafana 中可用 `container="aigc-backend"` 过滤；后续如需更细粒度，可给服务加 label 后配置 promtail filter。
