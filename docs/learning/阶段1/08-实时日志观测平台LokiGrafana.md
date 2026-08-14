# 08 · 实时日志观测平台（Loki + Grafana）

## 做了什么

在项目里加入 **Loki + Promtail + Grafana** 观测栈：Promtail 实时尾随 Docker 容器 stdout，把日志推给 Loki；Grafana 提供网页界面，在 **Explore → Live Tail** 里实时滚动查看日志。整个过程不写日志文件。

## 为什么

`docker compose logs -f` 虽然也能实时看，但它只是命令行工具。主流做法是把“日志采集、存储、可视化”拆成独立的观测组件，这样可以在浏览器里过滤、搜索、多人同时看，也为以后加指标和链路追踪留好位置。

## 架构

```text
FastAPI backend (stdout)
        │ Promtail 通过 docker.sock 实时尾随
        ▼
Promtail ──HTTP──▶ Loki ──HTTP──▶ Grafana (http://localhost:3000)
```

## 启动

```powershell
docker compose up -d --build
```

观测栈已通过主 `docker-compose.yml` 的 `include` 纳入项目，执行这一条命令即可同时启动后端和观测栈。启动后三个新容器：

| 容器 | 作用 | 地址 |
|------|------|------|
| `aigc-loki` | 日志存储与索引 | localhost:3100 |
| `aigc-promtail` | 从 Docker stdout 采集日志 | 无对外端口 |
| `aigc-grafana` | 网页观测界面 | http://localhost:3000 |

## 网页实时观测

1. 打开 http://localhost:3000。
2. 默认账号 `admin`，密码 `admin`（可用根 `.env` 的 `GRAFANA_ADMIN_PASSWORD` 覆盖）。
3. 左侧进入 **Explore**，数据源选 **Loki**。
4. 打开 **Live tail**，然后去聊天页发一条消息。
5. 后端日志会实时滚动，可用 `container="aigc-backend"` 过滤只看后端。

## 日志里能看到什么

后端本来就会输出：

```text
request start method=POST path=/api/chat/stream client=...
request body method=POST path=/api/chat/stream messages=1 model=glm-4-flash last_user='你好'
chat_stream start messages=1 model=glm-4-flash preview='你好'
chat_stream delta chunk='你好' chunk_chars=2 total_chars=2
chat_stream delta chunk='，' chunk_chars=1 total_chars=3
chat_stream finish events={'delta': 6, 'done': 1, 'error': 0} chars=11 preview='...'
request end method=POST path=/api/chat/stream status=200 bytes=... duration_ms=...
```

`chat_stream delta` 会在每个分片到达时实时出现，因此 Live Tail 里能看到 AI 一段一段输出的过程；`chat_stream finish` 是末尾完整汇总。

## 只采集 stdout，不写文件

Promtail 的 `docker_sd_configs` 通过 Docker socket 读取容器日志流，这是 Docker 为每个容器收集的 stdout/stderr，不是项目自己写的日志文件。项目代码里没有任何 FileHandler。

## 避坑

- 镜像首次启动需要 Docker Hub 网络；如果拉取超时，先解决镜像下载问题。
- Docker Hub 连不上时可从国内镜像拉取后 retag，例如：
  ```powershell
  docker pull docker.m.daocloud.io/grafana/loki:3.5.0
  docker tag docker.m.daocloud.io/grafana/loki:3.5.0 grafana/loki:3.5.0
  ```
- Grafana 第一次登录后会要求改密码；只想本地看可以直接用默认密码。
- 忘记密码时可删掉 `grafana_data` 卷重新初始化。
- 如果 Live Tail 没数据，先在 Explore 左侧看日志时间范围，再确认 `aigc-backend` 容器确实在运行。
