---
name: superpowers-harness
description: >-
  Superpowers Harness 门禁子技能（内部）：阶段判断、validate-harness、bootstrap 安装。
  用户开发类任务请用 superpowers-harness-run，不要单独触发本技能。
  仅在以下场景使用：harness-run 内部调用、安装 bootstrap-harness、单独跑 validate-harness、
  用户明确说「安装 harness」「bootstrap」「validate 自查」。
  与 superpowers-demand-workflow 配合。
---

# Superpowers Harness 门禁

在 `superpowers-demand-workflow`（文档落位）之上叠加流程门禁与机械校验。

## 何时使用

- 用户提出开发类任务：新功能、改页面、修 bug、实现、开发
- 需要判断当前需求处于哪个阶段
- 需要安装 Harness 到新项目（bootstrap-harness）
- commit 前自查：`node scripts/harness/validate-harness.mjs`

## 执行前必读

1. `docs/superpowers/HARNESS_RULES.md`
2. `docs/superpowers/SUPERPOWERS_RULES.md`

## 阶段判断

扫描 `docs/superpowers/current/{type}/*/` 下所有模块。

匹配优先级：

1. 用户明确模块名 → 精确匹配
2. 用户给出 `src/` 路径 → 按路径片段 fuzzy 匹配模块名
3. 无法匹配 → 新需求，从 create-demand 开始

| 阶段 | 条件 | 调用 |
|------|------|------|
| NO_MODULE | 无对应模块目录 | `superpowers-demand-workflow` (create-demand) |
| NO_SPEC | 无 specs/01-dev-spec.md | `brainstorming` |
| NO_PLAN | 无 plans/01-dev-plan.md | `writing-plans` |
| READY_TO_DEV | 有 spec 且有 plan | 允许开发 |

## 与 demand-workflow 衔接

- **demand-workflow** 管目录与文档落位
- **harness** 管能不能写代码、技能路由、校验迁移
- 未完成 spec/plan 时**不得**引导修改 `src/`
- 宽松模式：用户坚持跳过时警告并提示后续补文档

## 宽松模式

- `validate-harness.mjs` 默认宽松：警告 + exit 0
- `--strict`：有警告时 exit 1
- 日志：`.harness/warnings.log`

## 交付自检门禁（A → B）

交付阶段 `pnpm harness:check` 会校验 archive / spec 章节存在性（半硬 ⚠️，宽松模式不阻断 git）：

| 顺序 | 检查 | 警告码 | Agent 行为 |
|------|------|--------|------------|
| **A** | `*-delivered.md` 须含 `## 一致性自检` | `ARCHIVE_MISSING_CONSISTENCY_CHECK` | 补全后再报 DELIVERED |
| **B** | 适用 UI 模块（`ui-style`，或 `feature` 且 requirements 含 `figma.com`）的 delivered 须含 `## 还原度自检`（不适用可写「不适用：无 Figma / 非 UI」） | `ARCHIVE_MISSING_FIDELITY_CHECK` | 同上 |
| spec | `ui-style` 模块的 `specs/01-dev-spec.md` 须含样式对照节（如 `## 样式对照（Figma）`） | `SPEC_MISSING_FIGMA_STYLE_TABLE` | READY_TO_DEV 前补 spec |

**顺序：** 同一交付先完成 A 一致性自检，再完成 B 还原度自检（适用时），再写 archive。**存在上述警告时 Agent 不得声称 DELIVERED**，须补全文档后重跑 `pnpm harness:check`。

详见 `docs/superpowers/HARNESS_RULES.md` 与 `superpowers-harness-run` Step E。

**技能源码根目录：** `E:\code\frontend-local\` — 改流程须同步 `.agents` 与 `.cursor` 两侧副本，勿只改 junction 链接侧。

## 新项目安装

`bootstrap-harness` 一步安装以下内容：

- `superpowers-demand-workflow`：scripts + `docs/superpowers` 规则 + `v1.0.0` 骨架
- `scripts/harness/`：`validate-harness.mjs` + `status.mjs` + validators
- `docs/superpowers/HARNESS_RULES.md`、`AGENTS.md`、`.cursorrules`
- `superpowers-harness-run` 编排技能（`.agents` + `.cursor`）
- `.cursor/commands/harness.md`（`/harness` 命令）
- `package.json`：`harness:status` / `harness:check` / `harness:strict`

**Windows：**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".agents\skills\superpowers-harness\scripts\bootstrap-harness.ps1"
```

**macOS/Linux：**

```bash
bash .agents/skills/superpowers-harness/scripts/bootstrap-harness.sh
```

## AI 检查清单

- [ ] 已读 HARNESS_RULES + SUPERPOWERS_RULES
- [ ] 已判断阶段并路由到正确技能
- [ ] 未 READY_TO_DEV 时不改 src/
- [ ] 文档写入 current/ 下正确子目录
- [ ] commit 前提示运行 validate-harness 自查
- [ ] 新项目安装后已具备 superpowers-harness-run 与 /harness 命令
