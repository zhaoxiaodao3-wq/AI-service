# 阶段六容器化部署与项目收尾 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 背景与目标

阶段 1-5 已完成 backend/PostgreSQL/Qdrant/观测栈/工具的容器化。阶段 6 补齐前端容器化与健康检查，完成一键部署与 README 收尾。

## 设计

### 1. 前端容器

- `frontend/Dockerfile`：Node 多阶段构建 → `pnpm build` → Nginx 托管 `dist`。
- `frontend/nginx.conf`：
  - `/api/` 代理到 `http://backend:8000`，关闭缓冲保证 SSE。
  - 其他路径 `try_files ... /index.html` 支持 SPA 路由。
- `frontend/.dockerignore`：排除 node_modules/dist。

### 2. Compose 服务

`docker-compose.yml` 增加 `frontend`：

- `build: ./frontend`
- `ports: "5173:80"`（保持前端访问地址不变）
- `depends_on: backend`
- `healthcheck`：wget 首页

`backend` 增加 `healthcheck`：Python 请求 `/api/health`。

### 3. 一键启动

```powershell
docker compose up -d --build
```

启动全部服务：frontend、backend、postgres、qdrant、loki、promtail、grafana、adminer。

### 4. README 收尾

- 快速启动改为一条命令。
- 增加架构说明、功能清单、端口一览、部署说明。
- 阶段表更新为阶段 6 已完成。

### 5. 学习文档

新增 `docs/learning/阶段6/01~03`：

1. 前端容器化与 Nginx
2. 健康检查与一键部署
3. 项目收尾与运维清单

## 验收标准

- [x] `docker compose config --quiet` 通过，包含 frontend 服务。
- [x] 前端镜像构建成功，http://localhost:5173 返回应用页面。
- [x] http://localhost:5173/api/health 代理到后端返回 200。
- [x] backend/frontend 健康检查配置存在。
- [x] README 与学习文档已收尾。
- [x] `pnpm harness:check` 无警告。

## 非目标

- 不做云服务器部署与 HTTPS/CDN（README 给出生产建议）。
- 不引入 CI/CD。
