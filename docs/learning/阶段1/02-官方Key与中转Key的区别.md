# 02 · 官方 Key 与中转 Key 的区别

## 这一步做了什么

实现了模型配置与列表接口：

- `config.py` 新增可用模型清单与上下文上限配置
- `GET /api/models` 返回当前模式（`official` / `proxy`）、模型列表、默认模型
- 用单元测试验证接口契约
- 当前项目配置为智谱官方直连：`glm-4-flash`

## 为什么要这么做

### 1. 前端需要知道能选哪些模型

聊天页要做模型下拉，数据从 `GET /api/models` 来。这样以后模型清单变化，只改后端配置，前端自动更新。

### 2. 官方与中转为什么都要支持

手册明确规定：**中转 Key 仅用于开发调试，架构完全解耦，不依赖第三方黑盒服务**。

- 官方 Key：稳定、可上生产，但需要充值
- 中转 Key：便宜/免费，适合开发调试，但可能不稳定

项目同时支持两种，随时切换，不被任何一家绑定。

## 底层原理

### 官方直连

```dotenv
LLM_API_KEY=你的官方Key
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4-flash
```

请求直接发往厂商官方地址。厂商是谁，Key 就是谁的。

### 中转（代理）模式

```dotenv
LLM_PROXY_API_KEY=中转商给的Key
LLM_PROXY_BASE_URL=https://中转商地址/v1
```

中转商把各家模型统一成一套兼容协议，你买它的额度/免费额度，请求先到中转商，再转发到真实厂商。

### 适配层如何判断模式

```python
mode = "proxy" if (llm_proxy_api_key and llm_proxy_base_url) else "official"
```

中转配置非空 → `proxy`；否则 → `official`。前端下拉旁可以显示当前模式，帮助排查。

### 模型清单为什么静态配置

阶段 2 会把模型配置存进 PostgreSQL（含启用状态、权重、加密 Key），支持后台增删。现在先放 `config.py` 常量，减少阶段 1 复杂度。

## 关键命令逐条解释

| 命令 | 含义 |
|------|------|
| `GET /api/models` | 返回模式/模型清单/默认模型 |
| `pytest tests/test_models.py -v` | 验证模型列表接口 |
| 修改 `backend/.env` 后重启后端 | 让新模式生效 |

## 常见问题与避坑

1. **Key 填了还是 invalid_key**：官方 Key 要配 `LLM_API_KEY` + `LLM_BASE_URL`；中转 Key 要配 `LLM_PROXY_*`，两者别混。
2. **base_url 结尾**：智谱是 `/api/paas/v4`，很多中转商是 `/v1`，不要凭感觉填。
3. **切换后不生效**：`.env` 在服务启动时读取，改完必须重启 uvicorn。
4. **Key 泄露**：任何 Key 都只放本地 `.env`，`.env` 已被 gitignore，提交前用 `git status` 自查。
