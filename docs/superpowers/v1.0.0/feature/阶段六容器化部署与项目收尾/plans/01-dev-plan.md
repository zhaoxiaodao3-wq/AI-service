# 阶段六容器化部署与项目收尾 · 实施计划

**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

**Goal:** 前端容器化 + 健康检查 + 一键部署 + 文档收尾。

**Architecture:** Node 构建 → Nginx 托管静态资源并代理 /api；Compose 编排全部服务。

**Tech Stack:** Docker Compose、Nginx、Node。

---

### Task 1: 前端容器

**Files:**
- Create: `frontend/Dockerfile`、`frontend/nginx.conf`、`frontend/.dockerignore`

**Step 1:** 多阶段构建 + Nginx 配置。

### Task 2: Compose 与健康检查

**Files:**
- Modify: `docker-compose.yml`

**Step 1:** 增加 frontend 服务与 backend 健康检查。

**Step 2:** `docker compose config --quiet`。

### Task 3: 构建与实测

**Step 1:** `docker compose up -d --build frontend`。

**Step 2:** 验证 http://localhost:5173 与 /api/health 代理。

### Task 4: 文档收尾与归档

**Files:**
- Modify: `README.md`
- Create: `docs/learning/阶段6/01~03`

**Step 1:** README 一键部署/架构/功能/端口收尾。

**Step 2:** 归档 + `pnpm harness:check`。
