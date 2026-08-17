# 阶段三可视化工具 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 用 Adminer 与 Qdrant Dashboard 提供网页可视化查看。

**Architecture:** 新增 tools compose 文件并纳入主 `include`；Qdrant 使用内置 Dashboard。

**Tech Stack:** Docker Compose、Adminer、Qdrant Dashboard。

---

### Task 1: 编排文件

**Files:**
- Create: `docker-compose.tools.yml`
- Modify: `docker-compose.yml`

**Step 1:** 添加 adminer 服务并纳入 include。

**Step 2:** `docker compose config --quiet` 校验。

### Task 2: 启动与验证

**Step 1:** `docker compose up -d adminer`，验证 http://localhost:5050。

**Step 2:** 验证 http://localhost:6333/dashboard 可访问。

### Task 3: 文档与归档

**Files:**
- Modify: `README.md`
- Create: `docs/learning/阶段3/06-可视化查看数据库与向量库.md`

**Step 1:** 更新端口表与说明。

**Step 2:** 写 archive，跑 `pnpm harness:check`。
