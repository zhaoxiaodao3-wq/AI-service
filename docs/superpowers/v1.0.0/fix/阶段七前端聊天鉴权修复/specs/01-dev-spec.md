# 阶段七前端聊天鉴权修复 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 设计

### 1. `frontend/src/api/chatStream.ts`

- 请求头统一加入 `Authorization: Bearer <localStorage access_token>`。
- `resp.status === 401` 时清空本地登录态并跳转 `/login`，避免重复 401。

### 2. 验证

- `pnpm build` 通过。
- 无头浏览器登录后发送消息，抓包确认 `chat_req_auth` 为 Bearer、响应非 401。

## 验收标准

- [x] 登录后聊天请求带 Authorization 头。
- [x] 聊天接口不再返回 401。
- [x] `pnpm build` 通过。
