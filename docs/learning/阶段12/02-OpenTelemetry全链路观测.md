# 02 · OpenTelemetry 全链路观测（一次请求的"手术直播"）

## 这一步做了什么

接入 **OpenTelemetry（OTel）**，给系统装上"全链路追踪"能力：

- 后端启动时初始化 OTel，把 **Trace（追踪）** 数据通过 OTLP 协议上报到 Grafana Tempo
- 自动埋点：HTTP 请求（FastAPI）、数据库操作（SQLAlchemy）、外部 HTTP 调用（httpx → Qdrant）
- 手动埋点：LLM 调用（`llm.chat` span）、工具执行（`tool.execute` span）
- Grafana 增加 Tempo 数据源，一条请求从浏览器到数据库的完整调用链可视
- 观测层故障静默降级：Tempo 挂了聊天照常

## 为什么要这么做（用快递打比方）

以前排查问题靠日志：日志只能告诉你"某条请求出错了"，但**说不清它到底经历了什么**。

打个比方：以前你只能看到"包裹（请求）寄出"和"包裹损坏了"两条记录，不知道它中转了几个仓库、在哪一站出了问题。

全链路 Trace 就像给包裹装了 **GPS 定位**：

```text
浏览器请求
  → 后端 HTTP 层（route span）
    → 数据库查询（SQLAlchemy span）
    → Qdrant 检索（httpx span）
    → LLM 调用（llm.chat span，记录模型名/token 数）
    → 工具执行（tool.execute span）
  → 返回响应
```

每个环节都有"一个包裹 ID（trace_id）"，在 Tempo 里可以看这次请求完整的**瀑布图**：哪个环节慢、哪个环节出错、耗时多少，一目了然。

## 底层原理

### 1. 三个核心概念

| 概念 | 含义 | 类比 |
|------|------|------|
| **Trace** | 一次请求的完整调用链 | 一个包裹的完整运输路线 |
| **Span** | 调用链上的一个环节 | 运输路线上的一个站点 |
| **trace_id / span_id** | 环节的唯一标识，父子关联 | 包裹单号 / 站点的扫码记录 |

一次聊天请求 = 一个 Trace，里面串着 HTTP、DB、Qdrant、LLM 等多个 Span，每个 Span 记录自己的耗时和属性（模型名、token 数、错误信息等）。

### 2. 初始化代码（backend/app/core/telemetry.py）

核心三步：**建 Provider → 接 Exporter → 装 Instrumentor**

```python
def setup_telemetry() -> bool:
    # ① 资源：给 Trace 打上"服务名"标签，区分 aigc-backend / worker
    resource = Resource.create({"service.name": s.otel_service_name})

    # ② TracerProvider：全局"追踪工厂" + OTLP 导出器（发到 Tempo）
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=s.otel_exporter_otlp_endpoint))
    )
    trace.set_tracer_provider(provider)

    # ③ 自动埋点：FastAPI 路由 / SQLAlchemy 数据库 / httpx 外部请求
    FastAPIInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument(engine=engine)
    HTTPXClientInstrumentor().instrument()
```

- **Exporter** 决定 Trace 发到哪：`http://tempo:4318`（OTLP HTTP 协议）
- **Instrumentor** 是"自动探针"：不用改业务代码，框架层自动给每个 HTTP 请求/数据库查询创建 span
- **BatchSpanProcessor** 批量发送：攒一批再发，减少网络开销

### 3. 手动埋点：LLM 调用（backend/app/adapters/model_adapter.py）

自动埋点覆盖不到"LLM 调用"（那是 litellm 库内部的事），所以手动打 span：

```python
@contextmanager
def _llm_span(model: str):
    tr = get_tracer()
    if tr is None:
        yield None          # OTel 没初始化 → 空操作，零开销
        return
    with tr.start_as_current_span("llm.chat") as span:
        span.set_attribute("llm.model.name", model)   # 记录用的哪个模型
        yield span
```

调用处：

```python
with _llm_span(request.model) as span:
    resp = await litellm.acompletion(...)             # 真实调用
    if span is not None and resp.usage:
        span.set_attribute("llm.usage.total_tokens", resp.usage.get("total_tokens"))
```

这样 Tempo 里每个 `llm.chat` span 都带着**模型名和 token 消耗**，可以直接看出"哪个模型最贵、最慢"。

工具执行同理（`backend/app/tools/registry.py`），span 属性带 `tool.name`、`tool.user_id`、`tool.injection_filtered`（是否拦截了注入）。

### 4. 关键设计：观测层永不阻塞业务

```python
# telemetry.py 顶层不 import opentelemetry（全部惰性）
# setup_telemetry 内部 try/except，任何失败只打 warning
except Exception as exc:
    logger.warning("telemetry init failed (%s), run without tracing", exc)
    return False

def get_tracer():
    if not _initialized:
        return None      # 未初始化 → 返回 None，调用方跳过埋点
```

**为什么重要**：如果 Tempo 挂了或 OTel 依赖没装，观测系统故障不能拖垮聊天业务。所以：

- 顶层不 import OTel 包 → 没装依赖应用也能启动
- 初始化失败 → 打 warning 继续跑
- span 全部 `if tr is None` 降级 → 埋点代码在无观测环境下是空操作

### 5. Tempo 服务（docker-compose.observability.yml）

```yaml
tempo:
  image: grafana/tempo:2.6.1
  command: ["-config.file=/etc/tempo.yaml"]
  ports:
    - "3200:3200"   # 查询/UI
    - "4317:4317"   # OTLP gRPC
    - "4318:4318"   # OTLP HTTP（后端上报地址）
```

Grafana 里自动配好 Tempo 数据源（`observability/grafana/provisioning/datasources/tempo.yml`），并做了 **trace 与日志关联**：Tempo 里点开一个 span，可以直接跳到 Loki 里对应的日志（`tracesToLogs` 配置，按 trace_id 关联）。

## 关键命令逐条解释（怎么自己验证）

### 启动观测栈

```powershell
# 1) 启动观测服务（Loki + Tempo + Grafana）
docker compose -f docker-compose.observability.yml up -d

# 2) 重启后端（让 OTel 初始化生效，会连到 tempo:4318）
docker compose restart backend
# 后端日志应出现：telemetry initialized endpoint=http://tempo:4318

# 3) 确认 Tempo 起来了
docker compose -f docker-compose.observability.yml ps
```

### 制造一条请求并查看 Trace

```powershell
# 1) 登录并发一条聊天请求（正常问题 + 开启 RAG 更好，链路更长）
#    打开浏览器 → http://localhost:3000 → 登录 Grafana（admin/admin）
# 2) 左侧菜单：Explore → 数据源选 Tempo → Search
# 3) 能看到刚才请求的 Trace（service=aigc-backend）
# 4) 点开 → 瀑布图自上而下：
#    POST /api/chat/stream  (HTTP)
#      └─ SELECT ...          (SQLAlchemy 数据库)
#      └─ http://qdrant:6333  (httpx 检索)
#      └─ llm.chat            (模型调用，看 model/tokens 属性)
```

### 验证降级（可选）

```powershell
docker compose -f docker-compose.observability.yml stop tempo
# 再发聊天请求 → 一切正常，后端日志出现上报失败的 warning（不阻塞）
docker compose -f docker-compose.observability.yml start tempo
```

## 常见问题与避坑

1. **Tempo 没起来，后端一直重试上报**：OTel 批量导出有退避重试，不影响业务，Tempo 恢复后自动续传。日志里看到 warning 属正常。
2. **看不到 Trace**：检查三点——后端日志有没有 `telemetry initialized`、`OTEL_EXPORTER_OTLP_ENDPOINT` 是否指向 `tempo:4318`（容器内 hostname 是 tempo）、Grafana Explore 的数据源是否选对（Tempo 而非 Loki）。
3. **span 属性别塞敏感信息**：LLM span 只记录模型名和 token 数，不要把用户输入/回答原文写进 span 属性（会进存储）。
4. **自动埋点别重复**：`FastAPIInstrumentor().instrument()` 幂等，但不要在模块导入时反复调用；`setup_telemetry` 用 `_initialized` 标志保证只初始化一次。
5. **生产保留期**：Tempo 本地存储默认保留 3 天（`block_retention: 72h`），观测数据按需调大或接对象存储（超出本阶段范围）。
6. **trace 与日志关联**：Loki 日志里要有 trace_id 才能跳转。本阶段后端日志已带 trace 上下文（OTel 自动注入），promtail 采集即可关联。

## 小结

一句话记住：**OTel = 给请求装 GPS，自动埋点 HTTP/DB/Qdrant，手动埋点 LLM/工具，Tempo 里看瀑布图；观测层故障静默降级，绝不拖垮业务。**
