# 阶段六前端聊天布局交互优化 · 交付归档

**归档类型：** ui-style 交付快照
**归档日期：** 2026-08-17
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

完成聊天页布局交互：侧栏整高内部滚动；新会话输入框居中，发送后平滑落到底部；消息区独立滚动并增加“回到底部”按钮。

## 改动文件

| 操作 | 路径 |
|------|------|
| 改 | `frontend/src/views/ChatView.vue`（centeredInput、scroll 监听、回底按钮、布局 CSS） |
| 新增 | `docs/learning/阶段6/05-聊天布局与滚动交互优化.md` |
| 新增 | `docs/superpowers/v1.0.0/ui-style/阶段六前端聊天布局交互优化/`（requirements/spec/plans/archive） |

## 验收结果

- [x] 侧栏占满整高，会话多时只在侧栏内滚动。
- [x] 新会话输入框居中；发送后动画落到底部。
- [x] 消息多时只有聊天区滚动，整页不滚动。
- [x] 消息多且未在底部时出现回底按钮，点击平滑回底并隐藏。
- [x] `pnpm build` 通过，桌面/移动端截图无溢出。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 空会话输入框居中；有消息后输入框落底 |
| 常量/mock/真数据 | 通过 | 阈值常量（160px/4 条）写在组件内，行为与真实消息一致 |
| 多入口 | 通过 | 新会话/历史会话共用同一套布局状态 |
| 失败/缺省 | 通过 | 后端不可用时本地会话仍可交互；滚动按钮只在需要时显示 |

## 还原度自检

- 参考对象：产品交互需求（非 Figma）。
- 对照方式：Edge headless 实测输入框位置与滚动容器尺寸。
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
  - 新会话输入框 top=441，视口中心 450（居中）。
  - 发送消息后输入框 top=811（底部）。
  - 消息区 clientHeight=677、overflow-y=auto（独立滚动）。
- 学习文档：`docs/learning/阶段6/05-聊天布局与滚动交互优化.md`。

## 遗留风险

- 回底按钮阈值为固定值，后续可按真实使用反馈调整。
- 居中位移按 100vh 估算，极端小屏/缩放场景可能需要微调。
