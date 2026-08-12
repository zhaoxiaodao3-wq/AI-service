# 01 · FastAPI 分层架构为什么这样拆

## 这一步做了什么

在 `backend/` 目录创建了 FastAPI 后端骨架，并安装了全部核心依赖。骨架按层拆成：

```text
app/
├── api/          # 路由层：接收 HTTP 请求
├── core/         # 配置、日志、异常、统一响应
├── models/       # SQLAlchemy 数据模型（阶段 2 使用）
├── schemas/      # Pydantic 入参/出参（阶段 1+ 使用）
├── services/     # 服务层：业务逻辑（阶段 1+ 使用）
├── adapters/     # 模型适配层：LiteLLM 二次封装占位
├── repositories/ # 数据访问层（阶段 2 使用）
└── utils/        # 通用工具
```

## 为什么要这么做

### 1. 项目会越写越大

阶段 1 要加对话接口，阶段 2 要加数据库 CRUD，阶段 3 要加 RAG。如果所有代码都塞在一个文件里，几百行之后：

- 改一个功能会不小心影响另一个功能
- 找 bug 要翻遍整个文件
- 新功能不知道该放哪

分层就是提前给每个功能「定好房间」，以后代码往对应房间放。

### 2. 每一层只做一件事

| 层 | 职责 | 比喻 |
|----|------|------|
| `api/` | 接收请求、调用服务、返回响应 | 前台接待 |
| `services/` | 编排业务逻辑 | 业务经理 |
| `adapters/` | 对接外部系统（模型 API） | 翻译官 |
| `repositories/` | 读写数据库 | 仓库管理员 |
| `core/` | 公共配置与工具 | 行政后勤 |

职责单一后，替换或升级任何一层都不需要动其他层。

## 底层原理

### 什么是 FastAPI

FastAPI 是一个 Python Web 框架：你写一个函数，它负责把这个函数变成「浏览器/前端可以访问的 URL 接口」。

```python
@router.get("/health")
async def health():
    return ok({...})
```

`@router.get("/health")` 表示：当有人 `GET /health` 时，执行下面这个函数。

### 什么是分层架构

典型请求链路：

```text
前端请求
  → api/（路由层接收）
  → services/（业务逻辑）
  → repositories/（读数据库）或 adapters/（调模型）
  → 原路返回统一格式响应
```

每一层只能调用「相邻的下层」，不能越级。这样依赖方向始终单向，代码可读、可测、可替换。

### venv 虚拟环境是什么

Python 项目之间依赖版本可能冲突。venv 给每个项目开一个「独立的小房间」，`pip install` 装的东西只属于这个项目，不影响系统 Python。

### requirements.txt 是什么

项目的依赖清单。别人拿到项目后执行 `pip install -r requirements.txt` 就能装齐所有包。比手写一堆命令可靠得多。

## 关键命令逐条解释

| 命令 | 含义 |
|------|------|
| `python -m venv venv` | 在 `backend/venv` 创建独立 Python 环境 |
| `.\venv\Scripts\Activate.ps1` | 激活虚拟环境（PowerShell） |
| `pip install -r requirements.txt` | 按清单安装依赖 |
| `pip freeze` | 查看当前环境已装的包与版本 |

> 版本说明：本机 Python 是 3.14，部分旧版本包没有对应的预编译轮子，所以 `requirements.txt` 用了「最低版本」约束（如 `fastapi>=0.115`），由 pip 自动挑选兼容 3.14 的最新版本。这也解释了为什么清单里不是写死 `==x.y.z`。

## 常见问题与避坑

1. **激活了 venv 还是找不到包**：确认命令提示符前面出现 `(venv)`，或直接用 `.\venv\Scripts\python.exe` 运行。
2. **pip 安装报 Rust/编译错误**：通常是某个包没有当前 Python 版本的预编译轮子，把该包换成更高版本（`>=`）即可。
3. **依赖版本冲突**：让 pip 自动解决，不要把相互冲突的包写死，例如 httpx 由 litellm 决定版本。
4. **忘了复制 `.env`**：配置模块读不到环境变量时会用默认值，连不上数据库；确保 `backend/.env` 存在且密码与根级 `.env` 一致。
