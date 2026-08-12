# Superpowers AI 执行规则

> **强制**：执行 brainstorming、writing-plans 或新建需求文档前，必须先读本文件。

## 1. 目录定位

新需求统一写入四层嵌套结构：

```
docs/superpowers/current/{type}/{中文模块名}/
```

- `{type}` 仅允许：`feature` | `ui-style` | `api-adapter` | `fix`
- `current` 解析顺序：软链接 → `current-version.txt` → 默认 `v1.0.0`
- 版本号格式：`v主.次.修订`（三位，如 `v1.2.0`）
- **禁止**写入旧扁平路径：`docs/superpowers/specs/`、`plans/`、`archive/`、`reports/`（无版本号层）

## 2. 模块内目录职责

| 目录 | 存放内容 | 禁止 |
|------|----------|------|
| `requirements/` | 原始需求、初稿、Figma 说明、产品输入 | 开发方案、代码 |
| `specs/` | brainstorming 产出的开发规格（验收依据） | 原始需求原文堆叠 |
| `plans/` | writing-plans 原子任务 | 需求契约原文 |
| `archive/` | 历史草稿、旧版 spec/plan、交付快照 | 当前生效文档 |

## 3. 新建需求流程

### 新版本初始化（Windows）

双击 `scripts/init-version.bat`，按窗口提示输入版本号并确认。

命令行：`./scripts/create-demand.sh --init-version --version v1.1.0`

### 新建业务模块

1. 调用 `create-demand-dir` 技能，或运行：
   ```bash
   ./scripts/create-demand.sh --type <type> --name "<中文模块名>"
   ```
   Windows：`scripts\create-demand.bat --type <type> --name "<中文模块名>"`
2. 将原始需求写入 `requirements/`
3. 执行 brainstorming → writing-plans → 开发
4. **禁止**手动 `mkdir`

### AI 对话创建模板

```
请按 Superpowers 目录规范初始化需求目录：
- 版本：current（解析为实际版本目录）
- 分类：feature
- 模块名：登录注册功能

要求：
1. 幂等创建完整四层骨架（requirements / archive / specs / plans）
2. 不覆盖已有文件
3. 完成后回报创建的路径清单
```

## 4. 开发流程

```
① create-demand          建目录
② 原始需求 → requirements/
③ brainstorming          → specs/01-dev-spec.md
④ writing-plans          → plans/01-dev-plan.md
⑤ 按计划开发              → src/...
⑥ 交付归档               → archive/vN-delivered/
```

## 5. 文件命名

- 格式：`{两位序号}-{英文描述}.md`
- 示例：`requirements/figma-login-page.md`
- 示例 spec/plan：`01-dev-spec.md`、`01-dev-plan.md`
- 正文语言：简体中文

## 6. 文档引用规范

- 外层 `specs/` 头部须含 `**Requirement:**` 链接指向 `requirements/` 中的原始需求
- `plans/` 头部须含 `**Spec:**` 链接指向外层 `specs/`
- 模块内：相对路径
- 跨模块：从 `docs/superpowers/` 起的完整路径
- **禁止**硬编码 `current` 字面路径

## 7. 归档操作

| 时机 | 操作 |
|------|------|
| spec/plan 大改前 | 旧版 → `archive/vN-{slug}/` |
| 交付验收 | 快照 → `archive/vN-delivered/` |

## 8. 存量兼容

- `docs/superpowers/specs/` 等旧目录只读，不得新增或修改
- 详见 `_legacy-README.md`

## 9. 验收报告

新流程验收报告写入：

```
{模块}/archive/vN-delivered/validation-report.md
```
