# 07 · Docker 日志查看与请求响应链路

## 做了什么

阶段一补充为后端增加了**结构化请求/响应日志**，并把后端加入 Docker Compose。这样无论是 Docker Desktop 图形界面还是命令行，都能看到“前端发了什么请求、后端返回了什么”的完整链路。

这套日志是**实时观测式**的：后端把日志直接输出到 stdout，**不写任何日志文件**。你打开日志跟随后，前端每发一条消息，日志会立刻滚动出现。

## 为什么

排查问题时，光看前端页面不够：你往往需要确认请求有没有到达后端、后端是否真的返回了内容、耗时多久。日志就是这条链路的“黑匣子”。

## 三种查看方式

### 1. Docker Desktop 图形界面（最简单）

1. 打开 Docker Desktop。
2. 左侧点 **Containers**。
3. 找到 `aigc-backend` 容器。
4. 点容器名进入详情，切到 **Logs** 标签页。
5. 在前端聊天页发一条消息，日志会实时滚动出现。

### 2. 命令行跟随日志

```powershell
docker compose logs -f backend
```

`-f` 表示跟随（follow），日志实时滚动，退出按 `Ctrl+C`。只想从当前时刻开始看新日志：

```powershell
docker compose logs -f --tail 0 backend
```

只看最近 100 行：

```powershell
docker compose logs --tail 100 backend
```

这些命令都是读 Docker 采集到的 stdout 实时流，不会生成落盘日志文件。

### 3. 查看数据库/向量库日志

```powershell
docker compose logs -f postgres
docker compose logs -f qdrant
```

## 一条真实请求日志长什么样

前端在聊天页发“你好”后，`docker compose logs -f backend` 会输出类似下面的内容：

```text
INFO     app.access | request start method=POST path=/api/chat/stream client=172.20.0.1
INFO     app.access | request body method=POST path=/api/chat/stream messages=1 model=glm-4-flash last_user='你好'
INFO     app.chat   | chat_stream start messages=1 model=glm-4-flash preview='你好'
INFO     app.chat   | chat_stream finish events={'delta': 3, 'done': 1, 'error': 0} chars=42 preview='你好，有什么可以帮你？'
INFO     app.access | request end method=POST path=/api/chat/stream client=172.20.0.1 status=200 bytes=512 duration_ms=830.2
```

## 日志字段逐段解释

| 日志 | 含义 |
|------|------|
| `request start` | 后端收到 HTTP 请求，记录方法、路径、客户端 IP |
| `request body` | 请求体完整读取后的摘要：消息数量、模型、最后一条用户消息前 80 字 |
| `chat_stream start` | SSE 对话开始，包含消息数与内容预览 |
| `chat_stream finish` | 流式输出结束，统计 delta/done/error 事件数、总字符数、回答前 80 字 |
| `request end` | 请求整体结束，记录 HTTP 状态码、响应字节数、耗时 |
| `chat_stream model error` | 模型侧错误（Key 无效、额度不足等），记录错误码 |

## 如何启动带日志的后端容器

先确认 `backend/.env` 里已配置 LLM Key（本地开发本来就有），然后：

```powershell
docker compose up -d --build backend
```

Compose 会读取 `backend/.env` 的 LLM 配置，并把 `DATABASE_URL`、`QDRANT_URL` 自动指向容器网络内的 `postgres` 与 `qdrant` 服务，不需要手动改。

## 避坑

- 本地 `uvicorn` 也输出同样格式的日志；如果没开 Docker，直接看启动后端的终端即可。
- 8000 端口被本地后端占用时，先停掉本地 uvicorn 再启动容器，否则端口冲突。
- 如果容器内看不到日志，先确认前端请求确实到了 8000 端口，而不是代理到了别的地址。
- Docker Hub 拉不到 `python` 基础镜像时，通常是网络/代理问题，先解决镜像下载再构建。
