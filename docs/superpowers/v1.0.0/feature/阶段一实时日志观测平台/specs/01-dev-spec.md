# 阶段一实时日志观测平台 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 背景与目标

上一补充已完成后端 stdout 实时日志，但用户希望用主流观测软件在浏览器里实时查看，而不是打命令。本模块引入 **Loki + Promtail + Grafana**，Promtail 从 Docker 容器 stdout 实时采集日志并推给 Loki，Grafana 提供 Live Tail 网页界面。全程不写日志文件。

## 架构

```text
FastAPI backend (stdout)
        │ docker.sock 实时尾随
        ▼
Promtail ──HTTP──▶ Loki ──HTTP──▶ Grafana (http://localhost:3000)
```

## 设计

### 1. `docker-compose.observability.yml`

新增独立 compose 文件，与主 `docker-compose.yml` 叠加使用：

- `loki`：`grafana/loki:3.5.0`，端口 `3100`，单机模式，默认配置即可。
- `promtail`：`grafana/promtail:3.5.0`：
  - 挂载 `/var/run/docker.sock:/var/run/docker.sock` 实时尾随容器 stdout。
  - 挂载 `./observability/promtail/config.yml:/etc/promtail/config.yml`。
  - `depends_on: loki`。
- `grafana`：`grafana/grafana:11.4.0`，端口 `3000:3000`：
  - `GF_SECURITY_ADMIN_PASSWORD` 默认 `admin`，可用根 `.env` 的 `GRAFANA_ADMIN_PASSWORD` 覆盖。
  - 挂载 datasource 自动配置，启动即连接 Loki。

### 2. Promtail 配置 `observability/promtail/config.yml`

- `clients.url=http://loki:3100/loki/api/v1/push`。
- `docker_sd_configs` 发现本机所有 Docker 容器。
- relabel 保留 `container`（如 `aigc-backend`）、`stream` 标签，方便 Grafana 过滤。

### 3. Grafana 自动数据源 `observability/grafana/provisioning/datasources/loki.yml`

- datasource `uid: loki`、`type: loki`、`url: http://loki:3100`。
- Grafana 启动后无需手动添加数据源。

### 4. 使用方式

```powershell
docker compose -f docker-compose.yml -f docker-compose.observability.yml up -d --build
```

浏览器打开 `http://localhost:3000`，默认账号 `admin` / `admin`，进入 **Explore → Loki → Live tail** 实时观测。

### 5. 文档

- README 增加“实时日志观测（Loki + Grafana）”小节。
- 新增 `docs/learning/阶段1/08-实时日志观测平台LokiGrafana.md`，讲解架构、启动、Live Tail 用法与避坑。

## 验收标准

- [x] `docker compose -f docker-compose.observability.yml config --quiet` 通过。
- [x] Promtail 配置可被 Python `yaml.safe_load` 解析且包含 docker_sd_configs。
- [x] Grafana datasource 配置指向 `http://loki:3100`。
- [x] README 与学习文档包含完整启动命令与 Live Tail 使用说明。
- [x] 不修改后端代码；后端 stdout 日志保持不变，无文件落盘。

## 非目标

- 不接入日志文件采集（要求就是只采 stdout）。
- 不做指标/链路追踪（阶段 5/6 可扩展 SigNoz 或 OpenTelemetry）。
- 不修改主 compose 的 backend/postgres/qdrant 服务。
