---
name: superpowers-harness-run
description: >-
  Superpowers Harness 完整开发流程一键入口：从需求到交付自动走
  create-demand → brainstorming → writing-plans → 开发 → 归档 → validate-harness。
  用户提出新功能、改页面、修 bug、实现需求、对接接口、UI 还原、fix、开发、
  或描述任何要改 src/ 的任务时，必须优先使用本技能——即使用户没有说
  「harness」「superpowers」「按流程」。不要直接 /brainstorming 或跳过 spec/plan 改代码。
  与 superpowers-harness、superpowers-demand-workflow、brainstorming、writing-plans 配合。
---

# Superpowers Harness 完整流程

用户只需描述**要什么**，本技能负责走完整 Harness 工程链路。

**技能源码根目录：** `E:\code\frontend-local\`（`.agents/skills/` 与 `.cursor/skills/` 下副本均从此处维护）。**禁止**只改 `e:\code\frontend\` 的 junction 链接侧而不同步 `frontend-local` 源文件。

**启动时宣告：**「正在使用 superpowers-harness-run 执行 Harness 完整流程。」

## 何时使用

- 任何会改动 `src/` 的开发类任务
- 用户说「做个需求」「修一下」「实现」「对接」「改页面」
- 用户**没有**显式说 harness，但任务属于开发范畴
- 用户希望「一条对话走完全流程」

## 不要误触发

- 纯问答、代码 review、解释现有逻辑（只读）
- 用户明确说「跳过文档直接改」→ 警告后按 superpowers-harness 宽松模式处理

## 执行前必读

1. `docs/superpowers/HARNESS_RULES.md`
2. `docs/superpowers/SUPERPOWERS_RULES.md`

## Step 0：机械阶段查询（每次启动必做）

```bash
pnpm harness:status -- --match "<模块名关键词或路径片段>"
```

- 无匹配 → `NO_MODULE`，从 Step A 开始
- 有匹配 → 以 CLI 输出的 `阶段` / `下一步` 为准，**不要凭印象猜**
- 每次回复开头输出状态行：

  ```
  [Harness] fix/语言可理解度缺省态数值 | 阶段: READY_TO_DEV | 下一步: 开发 + 交付归档
  ```

## fix 轻量通道

同时满足以下条件时，可缩短 brainstorming，**不可跳过 spec/plan/validate/archive**：

- 分类为 `fix`
- 预计只改 1～2 个文件、无架构决策
- 用户描述明确（如「缺省态显示 0 不要 0.0」）

轻量做法：

1. 探索相关代码（只读）
2. 直接呈现推荐方案 + 1 句替代方案，一次确认
3. spec 可 ≤80 行，但仍须写 `specs/01-dev-spec.md`
4. plan 可 1～2 个 Task，但仍须写 `plans/01-dev-plan.md`
5. **validate、交付归档与标准流程相同**

## 从用户消息解析

| 字段 | 推断规则 |
|------|----------|
| **分类 type** | 新页面/能力→`feature`；UI/Figma→`ui-style`；接口/字段→`api-adapter`；bug/小修→`fix` |
| **模块名** | 用户给的名称；或从 `src/` 路径推断；2～20 字中文 |
| **需求摘要** | 写入 `requirements/01-原始需求.md` 的正文 |
| **关联路径** | 用户提到的组件/页面路径，用于 fuzzy 匹配已有模块 |

## 阶段判断

扫描 `docs/superpowers/` 下当前版本目录（读 `current-version.txt` 或 `v*` 最新）：

```
docs/superpowers/vX.X/{type}/{模块名}/
  requirements/
  specs/01-dev-spec.md
  plans/01-dev-plan.md
  archive/
```

匹配优先级：模块名精确 → 路径 fuzzy → 无匹配则新需求。

| 阶段 | 条件 | 下一步 |
|------|------|--------|
| `NO_MODULE` | 无对应目录 | Step A：create-demand |
| `NO_SPEC` | 无 spec | Step B：brainstorming |
| `NO_PLAN` | 无 plan | Step C：writing-plans |
| `READY_TO_DEV` | spec + plan 齐全 | Step D：开发 |
| `DELIVERED` | 已有 archive 交付快照且需求已变 | 新建 requirements 或新模块 |

**改 `src/` 前必须是 `READY_TO_DEV`。**

---

## Step A：建模块（NO_MODULE）

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/create-demand.ps1 -Type <type> -Name "<模块名>"
```

- 将用户需求写入 `{模块}/requirements/01-原始需求.md`
- 回报创建的目录路径
- 继续 Step B

## Step B：brainstorming（NO_SPEC）

**必须读取并遵循 `brainstorming` 技能**，不得跳过设计确认直接写代码。

1. 探索项目上下文（相关 `src/`、已有 docs）
2. 一次只问一个澄清问题（必要时）
3. 提出 2～3 方案 + 推荐
4. 分节呈现设计，每节后等用户确认
5. 写 `{模块}/specs/01-dev-spec.md`，头部：

   ```markdown
   **Requirement:** [requirements/01-原始需求.md](../requirements/01-原始需求.md)
   ```

6. spec 自检（无 TBD、无矛盾）
7. **UI/Figma 样式对照（READY_TO_DEV 前必做）：**
   - 类型为 `ui-style`，或类型为 `feature` 且 `requirements/` 中含 `figma.com` 链接 → spec **必须**含 `## 样式对照（Figma）`（或同义标题）
   - 表格至少含：字号/字重/色、间距、圆角/边框、关键尺寸；并注明 Figma 节点
   - 须用 Figma MCP / `get_design_context` 或截图取值，**禁止**凭印象填表
   - 缺此节时 `harness:check` 会 ⚠️ `SPEC_MISSING_FIGMA_STYLE_TABLE`；Agent 不得进入 READY_TO_DEV
8. **暂停**：请用户 review spec，确认后再 Step C

## Step C：writing-plans（NO_PLAN）

**必须读取并遵循 `writing-plans` 技能。**

1. 基于 spec 写 `{模块}/plans/01-dev-plan.md`
2. plan 头部含 `**Spec:**` 链接
3. 任务粒度 2～5 分钟，含具体文件路径与代码片段
4. **暂停**：提供两种执行方式让用户选：
   - Subagent-Driven（推荐）
   - Inline Execution

## Step D：开发（READY_TO_DEV）

**改 `src/` 之前：**

```bash
pnpm harness:status -- --match "<模块名>"
pnpm harness:check
```

- 有警告则汇报；本模块相关警告须先修复
- 宽松模式下其他模块历史警告可记录但不阻断

**开发期间：**

- 严格按 plan 执行；连续执行，仅在 plan 规定的确认点暂停
- 每完成一个 Task 做 lint / 相关测试
- **禁止**扩大 scope（不顺手重构无关代码）

**开发完成后 → Step E**

## Step E：Harness 交付收尾

**顺序强制：先 A 一致性自检 → 再 B 还原度自检（适用时）→ 写 archive → validate → 方可报 DELIVERED。**

禁止在未完成适用自检的情况下声称「已对齐 Figma」或「逻辑已闭环」。

### E.1 A · 一致性自检（全部模块类型）

写 archive **之前**，逐项检查（无关项标 **N/A** 并写原因）：

| 检查项 | 含义 |
|--------|------|
| 空态 vs 有数据 | Container/View 空态 hardcode 与 adapter/真数据路径是否一致 |
| 常量 / mock / 真数据 | 维度常量、mock、接口映射文案/数值是否同源 |
| 多入口 | A/B 类、列表/详情等是否只改一侧 |
| 失败 / 缺省 | `--`、0、隐藏与有数据语义是否合理 |

### E.2 B · 还原度自检（条件适用）

**适用：** 类型为 `ui-style`，或类型为 `feature` 且 `requirements/` 含 `figma.com`。

**不适用：** archive 的 `## 还原度自检` 写一行「不适用：无 Figma / 非 UI」。

适用时须对照 spec 的 `## 样式对照（Figma）` 与实现，记录：Figma 节点、对照方式、偏差清单、结论（可交付 / 需返工）。

### E.3 写 archive 并 validate

1. 勾选 `specs/01-dev-spec.md` 验收项
2. 写 `{模块}/archive/{模块名}-delivered.md`，使用模板（**必须含**下方两个强制小节）：

```markdown
# {模块名} · 交付归档

**归档类型：** {type} 交付快照
**归档日期：** {YYYY-MM-DD}
**版本：** {current version}
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

（1～3 句说明为什么改）

## 改动文件

| 操作 | 路径 |
|------|------|
| 改 | `src/...` |

## 验收结果

- [x] （对应 spec 第 6 节各项）

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 / N/A | … |
| 常量/mock/真数据 | 通过 / N/A | … |
| 多入口 | 通过 / N/A | … |
| 失败/缺省 | 通过 / N/A | … |

## 还原度自检

（适用 ui-style / 带 Figma 的 feature；否则写：不适用：无 Figma / 非 UI）
- Figma 节点：…
- 对照方式：…
- 偏差清单：无关键偏差 / …
- 结论：可交付 / 需返工

## Harness 闭环

- [x] validate 开发前已跑
- [x] archive 交付快照已写
- [x] validate 交付后已跑
```

3. 再跑：

   ```bash
   pnpm harness:check
   ```

4. 再跑 `pnpm harness:status`，确认阶段为 `DELIVERED`
5. 汇报 Harness 闭环清单（见下方）

**用户未要求时不要自动 commit。**

---

## Harness 闭环清单（交付时必报）

```
- [ ] 模块目录四层齐全
- [ ] requirements / spec / plan 链接正确
- [ ] 改 src/ 前 validate-harness 已跑
- [ ] spec 验收项已勾选
- [ ] 一致性自检已完成并写入 archive
- [ ] 还原度自检已完成或已注明不适用
- [ ] archive 交付快照已写
- [ ] commit 前 validate-harness 已跑
- [ ] harness:check 无本模块 ARCHIVE_MISSING_* / SPEC_MISSING_FIGMA_STYLE_TABLE 警告（否则不得报 DELIVERED）
```

## 子技能调用顺序

```
superpowers-harness-run（本技能，总编排）
  ├─ superpowers-harness（阶段判断、门禁规则）
  ├─ superpowers-demand-workflow（目录规范）
  ├─ brainstorming（spec）
  ├─ writing-plans（plan）
  └─ executing-plans 或 subagent-driven-development（开发）
```

**禁止**在未完成 spec/plan 时调用 executing-plans 或直接改 `src/`。

## 用户最简用法

用户只需：

```
语言可理解度组件缺省态 gauge 不要显示 0.0
```

或附加本技能：

```
/harness 语言可理解度 gauge 缺省态显示整数 0
```

Agent 自动推断 `fix` + 模块名 + 走全流程。

## 分类默认值

| 用户说法 | type |
|----------|------|
| 修 bug、修复、兼容、显示不对 | `fix` |
| 新页面、新功能、新增 | `feature` |
| Figma、UI 还原、样式 | `ui-style` |
| 接口、字段、对接、adapter | `api-adapter` |

不确定时问用户一次，不要猜测多次。

## 与 superpowers-harness 的分工

| 技能 | 职责 |
|------|------|
| `superpowers-harness` | 门禁规则、validate-harness、阶段枚举 |
| `superpowers-harness-run` | **端到端编排**，替用户串联全部步骤 |

两者同时可用：本技能内含 harness 门禁，无需用户再提「按 harness 流程」。
