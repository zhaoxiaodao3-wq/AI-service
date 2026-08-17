# 阶段八Agent工具增强 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 设计

### 1. `backend/app/tools/builtin.py`

- `get_weather(city)`：请求 `https://wttr.in/<city>?format=j1`，返回温度/体感/湿度/风速/描述。
- `convert_currency(amount, from, to)`：请求 `https://open.er-api.com/v6/latest/<FROM>`，按汇率换算。
- 均使用 `httpx.AsyncClient` 超时 8s，失败返回友好提示，不抛错。

### 2. `backend/app/tools/registry.py`

注册两个新工具，模型可直接调用。

### 3. 测试

- 注册中心包含新工具名。
- 天气/汇率为真实网络调用，不做单测断言，避免测试环境网络波动。

## 验收标准

- [x] 工具列表包含 `get_weather` 与 `convert_currency`。
- [x] 聊天开启工具后能查询天气并回答。
- [x] 聊天开启工具后能换算汇率并回答。
- [x] 网络失败时不阻塞聊天。
- [x] `pytest -q`（30 passed）与 `pnpm build` 通过。

## 非目标

- 不接入需付费/Key 的天气与汇率服务。
