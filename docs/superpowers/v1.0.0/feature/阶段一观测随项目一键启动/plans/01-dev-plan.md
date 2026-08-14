# 阶段一观测随项目一键启动 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 让 `docker compose up -d --build` 一条命令同时启动后端与观测栈。

**Architecture:** 主 compose 使用 `include` 引入观测 compose，服务定义仍保留在独立文件。

**Tech Stack:** Docker Compose。

---

### Task 1: 主 compose 集成观测栈

**Files:**
- Modify: `docker-compose.yml`

**Step 1:** 在文件顶部增加 `include: - docker-compose.observability.yml`。

**Step 2:** 校验：
```powershell
docker compose config --quiet
docker compose config | Select-String "aigc-loki|aigc-promtail|aigc-grafana"
```

### Task 2: 文档同步

**Files:**
- Modify: `README.md`
- Modify: `docs/learning/阶段1/08-实时日志观测平台LokiGrafana.md`

**Step 1:** 把两处启动命令改为 `docker compose up -d --build`，去掉 `-f docker-compose.observability.yml`。

### Task 3: 尝试实机启动并归档

**Step 1:** 执行 `docker compose up -d --build`，观察镜像拉取是否受网络阻塞。

**Step 2:** 写 archive，勾选 spec 验收项。
