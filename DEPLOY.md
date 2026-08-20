# AI-agent 前后端部署上线文档（阿里云 ECS + Docker Compose）

> 目标：把本仓库（FastAPI 后端 + Vue3 前端 + PG/Qdrant/Redis/Worker + 可观测栈）部署到阿里云 ECS。
> 部署方式：**Docker Compose**，代码通过本地打包上传或 git clone 上服务器，服务器只装 Docker。

## 1. 架构与端口总览

| 服务 | 容器名 | 镜像/构建 | 容器端口 | 宿主映射 |
|------|--------|-----------|----------|----------|
| PostgreSQL | aigc-postgres | postgres:16 | 5432 | 生产不对外（prod override 关闭） |
| Qdrant | aigc-qdrant | qdrant:v1.12.4 | 6333 | 生产不对外 |
| Redis | aigc-redis | redis:7-alpine | 6379 | 生产不对外 |
| Backend | aigc-backend | backend/Dockerfile (FastAPI) | 8000 | 生产不对外（走 nginx 反代） |
| Worker | aigc-worker | 同 backend | - | 不对外 |
| Frontend | aigc-frontend | frontend/Dockerfile (Vue3→nginx) | 80 | **80:80（生产）** |
| Loki | aigc-loki | grafana/loki:3.5.0 | 3100 | 仅内网 |
| Tempo | aigc-tempo | grafana/tempo:2.6.1 | 3200/4317/4318 | 仅内网 |
| Promtail | aigc-promtail | grafana/promtail:3.5.0 | - | - |
| Grafana | aigc-grafana | grafana/grafana:11.4.0 | 3000 | 按需开公网（建议限 IP） |
| Adminer | aigc-adminer | adminer:4 | 8080 | 5050（建议限 IP） |

请求链路：浏览器 → `http://IP:80`（nginx，含 /api 反代 + SSE 关缓冲）→ backend:8000 → PG/Qdrant/Redis。

## 2. 阿里云 ECS 准备

- 系统：**Ubuntu 22.04 LTS**（推荐，脚本已适配；24.04 亦可）
- 规格：2C4G 起步；启用 RAG 向量 + 可观测栈建议 **4C8G**
- 磁盘：40G+（数据都在 Docker volume：pg_data / qdrant_data / redis_data / uploads_data）
- **安全组**（控制台 → 实例 → 安全组 → 入方向）：
  - 22：SSH（强烈建议仅允许你的出口 IP）
  - 80/443：HTTP/HTTPS（必须）
  - 3000：Grafana、5050：Adminer —— 默认**不开公网**，需要时限定来源 IP
  - 5432/6379/6333/8000 —— 一律不开公网
- 国内网络建议（脚本已含）：Docker 镜像加速、pip/npm 构建时换镜像源。

## 3. 服务器初始化（一次性）

```bash
# 把 scripts/deploy/server-init.sh 上传到服务器后执行
sudo bash server-init.sh
```

脚本完成：apt 基础依赖、Docker CE + compose 插件、开机自启、Docker 镜像加速。验证：

```bash
docker --version && docker compose version
```

## 4. 上传代码与配置

### 方式 A：本地打包上传（推荐，无需服务器访问 GitHub）

本地（Windows）执行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy/build-package.ps1
```

生成 `dist/aigc-agent.tar.gz`（自动排除 .git / node_modules / venv / __pycache__ / .env 密钥）。上传并解包：

```bash
scp dist/aigc-agent.tar.gz root@<服务器IP>:/tmp/
ssh root@<服务器IP> "mkdir -p /opt/aigc-agent && tar -xzf /tmp/aigc-agent.tar.gz -C /opt/aigc-agent"
```

### 方式 B：git clone（需服务器能访问 GitHub）

```bash
cd /opt && git clone git@github.com:zhaoxiaodao3-wq/AI-service.git aigc-agent
```

### 环境变量（密钥不上包，单独上传/生成）

1. 根目录 `.env`（compose 编排用）：服务器上首次执行 `deploy.sh` 会自动从模板生成，需改强密码。
2. `backend/.env`（后端密钥，含智谱 LLM key / 硅基流动 embedding key 等）：
   - 推荐：本地 `scp backend/.env root@<IP>:/opt/aigc-agent/backend/.env`（复用现有密钥）
   - 或按 `backend/.env.example` 现场填写
   - 生产必须更换：`SECRET_KEY`（Fernet）、`JWT_SECRET`、`POSTGRES_PASSWORD`（可用 `openssl rand -base64 32` 生成）

## 5. 构建与启动

```bash
cd /opt/aigc-agent
bash scripts/deploy/deploy.sh /tmp/aigc-agent.tar.gz   # 或已解包则直接执行
# 等价命令：
docker compose -f docker-compose.yml -f scripts/deploy/docker-compose.prod.yml up -d --build
```

> 首次构建较慢（后端 pip 安装、前端 pnpm 安装 + 打包）。国内服务器若慢：
> - 后端：`backend/Dockerfile` 的 pip 加 `-i https://mirrors.aliyun.com/pypi/simple/`
> - 前端：在 `frontend/` 放 `.npmrc`，内容 `registry=https://registry.npmmirror.com`

## 6. 验证

```bash
docker compose -f docker-compose.yml -f scripts/deploy/docker-compose.prod.yml ps   # 全部 Up/healthy
curl http://127.0.0.1/api/health                                                    # 后端健康检查
curl -I http://127.0.0.1/                                                            # 前端页面
```

浏览器访问 `http://<服务器IP>/` 完成登录与对话验证（SSE 流式、文件上传、RAG 检索）。

## 7. 域名与 HTTPS（可选）

1. 阿里云 DNS 添加 A 记录：`app.你的域名.com → 服务器IP`
2. 方案一（推荐，宿主 Caddy 自动证书）：
   ```bash
   # 安装 caddy：https://caddyserver.com/docs/install
   echo "app.你的域名.com { reverse_proxy 127.0.0.1:80 }" > /etc/caddy/Caddyfile
   systemctl enable --now caddy
   ```
3. 方案二：nginx + certbot（`certbot --nginx -d app.你的域名.com`）
4. 无论哪种反代，**SSE 必须** `proxy_buffering off`（前端 nginx 内部已配好；外层反代也要关）。

## 8. 运维

- 更新发布：重新打包上传 → `docker compose ... up -d --build`（或 git pull 后同样命令）
- 日志：`docker compose logs -f backend`；Grafana(http://IP:3000, admin/admin，首次登录改密) 看 Loki/Tempo
- 备份（重要）：`docker compose exec postgres pg_dump -U aigc_user aigc_chat > backup.sql`；卷 `pg_data/qdrant_data/redis_data/uploads_data` 定期打包到 /backup
- 开机自启：`restart: unless-stopped` + `systemctl enable docker`（脚本已做）
- 数据目录：所有数据都在 Docker 卷中，容器可随意重建不丢数据

## 9. 安全清单

- [ ] 更换 `POSTGRES_PASSWORD` / `SECRET_KEY` / `JWT_SECRET`
- [ ] 安全组只开 22/80/443（+ 必要的限定 IP）
- [ ] Grafana / Adminer 改默认口令或仅内网
- [ ] SSH 禁用密码登录（用密钥）或仅限白名单 IP
