# 阶段六前端聊天布局交互优化修订 · 交付归档

**归档类型：** ui-style 交付快照
**归档日期：** 2026-08-17
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

根据 ui-ux-pro-max 审查，撤销上一版“输入框居中”的硬编码位移实现，改为标准底部输入 + 消息区空态居中；侧栏整高内部滚动；回底按钮改为“不靠底即显示”并支持减少动态效果；补齐无障碍标签。

## 改动文件

| 操作 | 路径 |
|------|------|
| 改 | `frontend/src/views/ChatView.vue`（删除 centeredInput/center-hint、回底按钮 rAF 节流、aria-label） |
| 改 | `frontend/src/layouts/MainLayout.vue`（100vh + content 内部滚动） |
| 新增 | `docs/learning/阶段6/06-聊天布局审查与修订.md` |
| 新增 | `docs/superpowers/v1.0.0/ui-style/阶段六前端聊天布局交互优化修订/`（requirements/spec/plans/archive） |

## 验收结果

- [x] 输入框始终在底部；空会话提示居中在消息区。
- [x] 侧栏整高且内部滚动。
- [x] 回底按钮仅在不靠底时出现，点击平滑回底并隐藏。
- [x] `prefers-reduced-motion` 下无强制动画。
- [x] `pnpm build` 通过，桌面/移动端截图无溢出。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 空会话提示居中；有消息后输入框固定底部 |
| 常量/mock/真数据 | 通过 | 回底阈值 160px 为组件常量，行为与真实消息一致 |
| 多入口 | 通过 | 新会话/历史会话共用同一布局 |
| 失败/缺省 | 通过 | 后端不可用时本地会话可用；滚动按钮不靠底才显示 |

## 还原度自检

- 参考对象：ui-ux-pro-max 审查结论（非 Figma）。
- 对照方式：Edge headless 实测输入框/空态位置与滚动容器。
- 偏差清单：无关键偏差。
- 结论：可交付。

## Harness 闭环

- [x] 模块目录四层齐全（requirements/specs/plans/archive）
- [x] requirements / spec / plan 链接正确
- [x] 改 `src/` 前 validate-harness 已跑（阶段 READY_TO_DEV 后开发）
- [x] spec 验收项已勾选
- [x] 一致性自检已完成并写入 archive
- [x] 还原度自检已完成并写入 archive
- [x] archive 交付快照已写
- [x] 交付后 `pnpm harness:check` 已跑，无本模块警告

## 验证证据

- `pnpm build` 通过，前端镜像重建成功。
- 无头浏览器实测：
  - 新会话输入框 top=811（底部固定）。
  - 空态提示 top=144、中心 y=406（消息区居中）。
  - 消息区 clientHeight=677、overflow-y=auto（独立滚动）。
- 学习文档：`docs/learning/阶段6/06-聊天布局审查与修订.md`。

## 遗留风险

- 回底按钮阈值仍为固定 160px，后续可按真实反馈调整。
- 移动端系统手势区未做 `env(safe-area-inset-bottom)` 适配，阶段后续可补。
