# 04 · 宝塔 VPS 生产部署（从零把服务搬到云服务器）

> 本教程面向：**宝塔 Linux 面板（阿里云专享版 11.1.0）**，服务器为阿里云 ECS。
> 全程两种操作路径：宝塔面板点鼠标 / SSH 命令行，二选一即可，推荐面板操作更直观。

## 部署架构总览

```text
用户浏览器
  → 域名（HTTPS，宝塔申请的 SSL 证书）
    → 宝塔 Nginx 反向代理 → localhost:80（前端容器）
      → /api 请求再代理 → localhost:8000（后端容器）
容器网络内部：
  backend/worker → postgres（5432）/ qdrant（6333）/ redis（6379）/ tempo（4318）
```

要点：

- **外部只暴露 80/443**（HTTPS 由宝塔 Nginx 处理），数据库/Redis/Qdrant 全部在容器内网，公网不可达——安全。
- 后端容器通过 `docker-compose.prod.yml` 编排，与开发 compose 隔离。

## 前置准备（你操作）

### 1. 阿里云安全组放行端口

```text
阿里云控制台 → ECS 实例 → 安全组 → 配置规则 → 入方向
放行端口（宝塔面板也要放）：
  8888   宝塔面板
  22     SSH
  80     网站 HTTP
  443    HTTPS（申请证书后需要）
其余端口（5432/6379/6333/8000 等）一律不放行——它们只在内网容器网络用
```

### 2. 服务器装好 Docker

宝塔面板 → 左侧"软件商店"→ 搜索 **Docker 管理器** → 安装（会自动装 Docker 引擎与 Compose）。

安装后验证（SSH）：

```bash
docker --version
docker compose version
```

## 部署步骤（按顺序执行）

### 第 1 步：上传项目文件到服务器

```text
宝塔面板 → 文件 → 进入 /www/wwwroot/
新建目录 aigc → 进入
上传以下文件（从你本地项目拷）：
  docker-compose.prod.yml
  .env.prod（用 .env.prod.example 复制改名并填好配置）
  backend/  （整个目录，构建镜像用；或用 GHCR 拉取替代，见下方说明）
  frontend/ （整个目录）
```

> 如果 CI 已经推了 GHCR 镜像（见 03 篇），第 1 步可以只上传 `docker-compose.prod.yml` 和 `.env.prod`，然后把编排文件里的 `build` 段注释掉、启用 `image: ghcr.io/你的账号/...`，服务器直接拉镜像，不需要上传源码。

### 第 2 步：配置 .env.prod（关键！）

在 `/www/wwwroot/aigc/.env.prod` 里至少改这几项：

```text
POSTGRES_PASSWORD=改成强密码
SECRET_KEY=改成随机长字符串（可用 openssl rand -hex 32 生成）
JWT_SECRET=改成随机长字符串
LLM_PROVIDER=zhipu
LLM_MODEL=glm-4-flash
LLM_API_KEY=你的智谱API密钥
```

**这些值不要用默认值**——数据库密码、JWT 密钥暴露 = 服务器被攻破。

### 第 3 步：启动容器

```bash
cd /www/wwwroot/aigc
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps
```

预期看到 5 个容器（postgres/qdrant/redis/backend/worker/frontend）状态 healthy/Up。

验证后端健康：

```bash
curl http://127.0.0.1:8000/api/health
# 期望：{"code":0,"message":"ok","data":{"database":"ok","qdrant":"ok",...}}
```

### 第 4 步：宝塔创建网站 + 反代

```text
宝塔面板 → 网站 → 添加站点：
  域名：填你的域名（比如 ai.example.com）
  PHP 版本：纯静态
  （如果还没有域名：先用服务器 IP 访问 http://IP:80 验证，再补域名）

添加后：
  网站设置 → 反向代理 → 添加反向代理：
    代理名称：aigc-frontend
    目标 URL：http://127.0.0.1:80
    发送域名：$host
```

这样访问你的域名 → 宝塔 Nginx → 前端容器（80 端口）→ 前端 nginx 再反代 /api 到后端。

### 第 5 步：申请 HTTPS 证书

```text
网站设置 → SSL → Let's Encrypt → 勾选你的域名 → 申请
申请成功后：
  强制 HTTPS：网站设置 → 基本 → 开启"强制HTTPS"
```

证书到期自动续签（宝塔自带计划任务），无需手动管。

### 第 6 步：验证上线

```text
浏览器打开 https://你的域名
  → 页面正常加载（锁图标 = HTTPS 生效）
  → 注册账号 → 登录 → 发消息 → 模型正常回复
  → 上传文档 → worker 处理 → 知识库问答可用
```

## 常见问题与避坑

1. **端口必须收敛**：生产 compose 里数据库/Redis/Qdrant 没有 `ports` 映射（只在容器内网），**不要**手贱加上——那等于把数据库暴露到公网。
2. **数据库密码别用默认**：`docker-compose.prod.yml` 用 `${POSTGRES_PASSWORD}` 从 .env.prod 读，务必改成强密码。
3. **反代目标用 `127.0.0.1` 不是 `localhost`**：容器端口只绑定了 `127.0.0.1:80`，宝塔 Nginx 反代到 localhost 时 IPv6 解析可能失败，写 127.0.0.1 最稳。
4. **改代码后更新**：`cd /www/wwwroot/aigc && docker compose -f docker-compose.prod.yml up -d --build`（源码方式）；或重新推送 CI → 服务器 `docker compose pull && up -d`（GHCR 方式）。
5. **worker 与 backend 共用镜像**：worker 只是换了启动命令（`python -m scripts.worker`），用同一镜像，别单独构建。
6. **数据持久化**：数据都在 Docker 卷里（pg_data/qdrant_data/redis_data/uploads_data），容器删了数据还在；定期备份见 05 篇。
7. **安全组忘了放行 443**：HTTPS 申请好了但访问不了，八成是阿里云安全组没放 443。

## 升级更新流程（以后每次发版）

```text
1. 本地改代码 → commit → push（CI 自动测试+构建镜像）
2. SSH 服务器：
   cd /www/wwwroot/aigc
   docker compose -f docker-compose.prod.yml pull      # 拉新镜像
   docker compose -f docker-compose.prod.yml up -d     # 滚动重建
3. 浏览器验证 https://你的域名
```

## 小结

一句话记住：**宝塔部署 = 安全组放行 8888/22/80/443 → 上传 compose + .env.prod → docker compose up → 宝塔建站反代到 127.0.0.1:80 → 申请 SSL → 收工；数据库等端口绝不对外开放，密钥全走 .env.prod。**
