# 02 · Docker 与 PostgreSQL 原理

## 这一步做了什么

在项目根目录编写了 `docker-compose.yml`，通过 Docker 启动了两个服务：

- PostgreSQL 16：业务数据库，宿主机端口 5433（因为本机 5432 已被另一个 PostgreSQL 占用）
- Qdrant：向量数据库，端口 6333

两个容器现在都是 `healthy` 状态，数据分别存放在 `pg_data` 和 `qdrant_data` 两个 Docker volume 中。

## 为什么要这么做

项目需要两个数据库，但它们都不应该由我们在本机手工安装：

1. **环境统一**：Docker 镜像里已经配好了 PostgreSQL/Qdrant，团队任何人拉下来都是同一个版本，不会出现「我电脑能跑你电脑跑不了」。
2. **删除干净**：不要了执行 `docker compose down` 即可，不会在本机残留一堆服务。
3. **贴近真实工作**：生产环境数据库也是独立部署的，本地用容器模拟最接近真实。

## 底层原理

### 容器 vs 镜像

- **镜像（Image）**：一个只读的「安装包模板」，例如 `postgres:16` 就是 PostgreSQL 16 的完整运行环境快照。
- **容器（Container）**：镜像运行起来后的一个独立进程实例，有自己的文件系统、网络和进程空间，互不干扰。

类比：镜像像「炒菜配方 + 提前切好的菜」，容器像「按配方炒出来的一盘菜」；一盘菜吃完了扔掉，配方还在，随时能再炒一盘。

### 端口映射

```yaml
ports:
  - "5433:5432"
```

冒号左边是宿主机端口（你电脑对外访问的端口），右边是容器内部端口。PostgreSQL 容器内部固定监听 5432，我们把宿主机 5433 转发给它，所以连接串写 `localhost:5433`。

### Volume 持久化

容器是临时环境，重启可能丢失数据。volume 相当于把容器里的一个目录挂载到宿主机磁盘上，即使容器删掉重建，数据还在。

```yaml
volumes:
  - pg_data:/var/lib/postgresql/data
```

### Healthcheck 健康检查

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
```

容器启动不等于可用。healthcheck 让 Docker 周期性执行探测命令，成功后才把状态标记为 `healthy`，方便我们判断「真的能连了」。

### Docker Compose 的作用

`docker-compose.yml` 一次性声明多个服务、网络、volume，然后一条命令启动/停止整套环境，相当于「项目的环境说明书」。

## 关键命令逐条解释

| 命令 | 含义 |
|------|------|
| `docker compose up -d` | 启动全部服务；`-d` 表示后台运行，不占着终端 |
| `docker compose ps` | 查看所有服务状态（是否 healthy） |
| `docker compose down` | 停止并删除容器（volume 默认保留） |
| `docker compose down -v` | 停止并连 volume 一起删除，数据会清空，谨慎使用 |
| `docker logs aigc-postgres` | 查看 PostgreSQL 容器日志 |
| `docker exec -it aigc-postgres bash` | 进入容器内部执行命令 |

## 为什么 PostgreSQL 用 5433 而不是 5432

任务 0 检查端口时发现本机 5432 已被一个本地 PostgreSQL 服务占用。如果强行占用会冲突，所以本项目的 `.env` 里设置了 `POSTGRES_PORT=5433`。这不影响任何功能，只是访问地址从 `localhost:5432` 变成 `localhost:5433`。

## 常见问题与避坑

1. **容器起不来**：先 `docker logs <容器名>` 看日志，常见原因是端口被占用或镜像下载中断。
2. **密码连不上**：容器用 `.env` 里的密码初始化，改了 `.env` 后要 `docker compose down -v && docker compose up -d` 重建（会清空数据）。
3. **数据丢了**：确认 volume 还在，`docker volume ls` 能看到 `ai-agent_pg_data`。
4. **health 一直 starting**：等 5~10 秒再 `docker compose ps`，首次启动初始化需要时间。
