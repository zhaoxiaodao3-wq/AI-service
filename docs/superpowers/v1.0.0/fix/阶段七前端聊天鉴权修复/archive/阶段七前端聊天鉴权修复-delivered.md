# 阶段七前端聊天鉴权修复 · 交付归档

**归档类型：** fix 交付快照
**归档日期：** 2026-08-17
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

修复登录后聊天接口 401：`chatStream.ts` 使用原生 fetch，未走 axios 拦截器，导致没有携带 JWT。现在 fetch 请求显式添加 `Authorization: Bearer`，并在 401 时清理登录态跳转登录页。

## 改动文件

| 操作 | 路径 |
|------|------|
| 改 | `frontend/src/api/chatStream.ts`（Token 头 + 401 处理） |
| 新增 | `docs/superpowers/v1.0.0/fix/阶段七前端聊天鉴权修复/`（requirements/spec/plans/archive） |

## 验收结果

- [x] 登录后聊天请求带 Authorization 头。
- [x] 聊天接口不再返回 401。
- [x] `pnpm build` 通过。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 无 Token 时不加头；有 Token 时自动携带 |
| 常量/mock/真数据 | 通过 | 真实浏览器登录后抓包验证 |
| 多入口 | 通过 | axios 与 fetch 两条通道都携带 Token |
| 失败/缺省 | 通过 | 401 清理登录态并跳转登录页 |

## 还原度自检

不适用：无 Figma / 非 UI 还原类需求。

## Harness 闭环

- [x] 模块目录四层齐全（requirements/specs/plans/archive）
- [x] requirements / spec / plan 链接正确
- [x] 改 `src/` 前 validate-harness 已跑（阶段 READY_TO_DEV 后开发）
- [x] spec 验收项已勾选
- [x] 一致性自检已完成并写入 archive
- [x] 还原度自检已注明不适用
- [x] archive 交付快照已写
- [x] 交付后 `pnpm harness:check` 已跑，无本模块警告

## 验证证据

- `pnpm build` 通过。
- 无头浏览器实测：登录后发送消息，抓包 `chat_req_auth=Bearer eyJ...`，`chat_resp_status=200`。
