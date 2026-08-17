# 阶段三可视化工具 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 背景与目标

阶段 3 交付后用户需要直接“看数据”。新增轻量 Adminer 容器查看 PostgreSQL；Qdrant v1.12 自带 Dashboard，无需额外容器，直接使用 `/dashboard`。

## 设计

### 1. Adminer

新增 `docker-compose.tools.yml`：

- 服务名 `adminer`，镜像 `adminer:4`，容器名 `aigc-adminer`。
- 端口 `5050:8080`。
- `depends_on: postgres`。
- 连接参数：`localhost:5050` → 系统选 PostgreSQL、服务器 `postgres`、用户名 `aigc_user`、密码取 `.env` 的 `POSTGRES_PASSWORD`、库 `aigc_chat`。

### 2. Qdrant Dashboard

Qdrant 容器已运行，内置网页位于 `http://localhost:6333/dashboard`，无需新增服务。

### 3. 主编排集成

`docker-compose.yml` 的 `include` 增加 `docker-compose.tools.yml`，`docker compose up -d` 一起启动。

### 4. 文档

- README 端口表增加 Adminer 与 Qdrant Dashboard。
- 新增 `docs/learning/阶段3/06-可视化查看数据库与向量库.md`。

## 验收标准

- [x] `docker compose up -d` 后 `aigc-adminer` 启动，http://localhost:5050 可访问。
- [x] http://localhost:6333/dashboard 可打开并显示集合。
- [x] README 与学习文档包含连接参数。

## 非目标

- 不做生产级数据库管理权限体系（仅本地开发查看）。
- 不引入 pgAdmin/DBeaver 等重型客户端（如需可自行安装 DBeaver）。
