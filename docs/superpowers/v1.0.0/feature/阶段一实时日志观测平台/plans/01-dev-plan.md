# 阶段一实时日志观测平台 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 通过 Loki + Promtail + Grafana 提供浏览器实时日志观测，不写日志文件。

**Architecture:** Promtail 通过 Docker socket 实时尾随容器 stdout → Loki 存储索引 → Grafana Live Tail 网页实时展示。

**Tech Stack:** Docker Compose、Grafana Loki、Promtail、Grafana。

---

### Task 1: 观测编排文件

**Files:**
- Create: `docker-compose.observability.yml`

**Step 1:** 添加 `loki`（3100）、`promtail`（docker.sock + config 挂载）、`grafana`（3000 + datasource 自动配置）三个服务。

**Step 2:** 校验：
```powershell
docker compose -f docker-compose.observability.yml config --quiet
```
期望：exit 0。

### Task 2: Promtail 与 Grafana 配置

**Files:**
- Create: `observability/promtail/config.yml`
- Create: `observability/grafana/provisioning/datasources/loki.yml`

**Step 1:** Promtail 配置 `docker_sd_configs`，relabel 出 `container`/`stream` 标签，client 指向 `http://loki:3100`。

**Step 2:** Grafana provisioning datasource 指向 `http://loki:3100`。

**Step 3:** 用 Python `yaml.safe_load` 解析两个 YAML，确认语法正确。

### Task 3: 文档

**Files:**
- Modify: `README.md`
- Create: `docs/learning/阶段1/08-实时日志观测平台LokiGrafana.md`

**Step 1:** README 增加实时观测小节：启动命令、Grafana 地址、Live Tail 用法。

**Step 2:** 学习文档说明架构、启动、Live Tail、常见问题。

### Task 4: 验证与归档

**Step 1:** 重跑 `docker compose -f docker-compose.observability.yml config --quiet` 与 `pnpm harness:check`。

**Step 2:** 写 archive，勾选 spec 验收项。
