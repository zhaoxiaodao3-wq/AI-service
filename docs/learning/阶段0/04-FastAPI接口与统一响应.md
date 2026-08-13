# 04 · FastAPI 接口与统一响应

## 这一步做了什么

实现了后端第一个真正可访问的接口：

```text
GET /api/health
```

返回统一格式：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "service": "aigc-backend",
    "time": "2026-08-13T11:58:54+08:00",
    "database": "ok",
    "qdrant": "ok"
  }
}
```

同时建立了两个全局机制：统一响应格式、统一异常处理，并用 pytest 写了接口测试。

## 为什么要这么做

### 1. 统一响应格式

如果每个接口自己决定返回结构，前端每接一个接口就要写一种解析逻辑，非常容易乱。

本项目约定所有接口都返回：

```text
{ code, message, data }
```

- `code = 0`：成功
- `code != 0`：业务错误码
- `message`：给人看的说明
- `data`：真正的业务数据

前端只需要解析这一种结构，后端加新接口也无需发明新格式。

### 2. 健康检查为什么有用

健康检查是项目的「体检报告」。以后每次排查「是不是服务没起来 / 数据库挂了 / 向量库挂了」，先访问 `/api/health` 就能定位，不用到处翻日志。

### 3. 测试为什么先写

先用测试把「接口应该返回什么」固定下来，再实现接口。好处：

- 以后改代码时跑一遍测试，立刻知道有没有破坏已有行为
- 测试本身就是接口的「使用说明书」

## 底层原理

### FastAPI 路由

```python
@router.get("/health")
async def health():
    return ok({...})
```

`@router.get("/health")` 是装饰器：它把下面的函数注册为「访问 `GET /health` 时执行」的处理函数。`router` 是路由分组，`prefix="/api"` 让整组路由统一加 `/api` 前缀。

### 请求处理流程

```text
浏览器/前端
  → GET /api/health
  → FastAPI 找到 health 函数
  → 函数探测数据库、Qdrant
  → ok() 包成统一格式
  → 返回 JSON 给前端
```

### 异常处理

程序出错时如果直接抛堆栈，前端看到的是又长又乱的报错。统一异常处理器把错误收敛成：

```json
{ "code": 500, "message": "服务器内部错误", "data": null }
```

真实堆栈只写进日志，不暴露给用户，既安全又清晰。

### CORS 是什么

浏览器安全策略不允许「页面地址」和「接口地址」不同源时随意读取数据。CORS 中间件告诉浏览器「我们允许 5173 前端访问后端」，否则前端直连后端会被拦截。本阶段前端走 Vite 代理通常不触发，这里先预留。

### TestClient

```python
client = TestClient(app)
resp = client.get("/api/health")
```

TestClient 在内存中启动一个 FastAPI 实例发请求，不需要真的开端口，适合写自动化测试。

## 关键命令逐条解释

| 命令 | 含义 |
|------|------|
| `pytest tests/test_health.py -v` | 运行健康检查接口测试，`-v` 显示详细结果 |
| `uvicorn app.main:app --reload --port 8000` | 启动后端服务；`--reload` 改代码自动重启 |
| `http://localhost:8000/api/health` | 浏览器直接访问验证接口 |

## 常见问题与避坑

1. **接口返回 500**：先看终端日志里的堆栈，通常是 `.env` 没配好或依赖缺失。
2. **`database: error`**：先 `docker compose ps` 确认 PostgreSQL 是 `healthy`。
3. **`qdrant: error`**：确认 Qdrant 容器健康，且客户端版本与服务端匹配。
4. **pytest 找不到 `app`**：必须从 `backend/` 目录运行 `pytest`，不要进到 `tests/` 里跑。
