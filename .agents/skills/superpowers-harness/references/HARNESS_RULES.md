# Harness 执行规则

> **强制**：开发类任务前须同时读取本文件与 `SUPERPOWERS_RULES.md`。  
> 本文件**叠加** Superpowers 规则，**不替代**它。

## 1. 当前模式：宽松

| 场景 | Agent 层 | 机械层 | Git hook |
|------|----------|--------|----------|
| 无模块就改 `src/` | 强制走 create-demand | ⚠️ 警告 | 不阻断 |
| 无 spec/plan 就改 `src/` | 强制走 brainstorming/plans | ⚠️ 警告 | 不阻断 |
| 写入旧扁平路径 | 禁止 | ⚠️ 警告 | 不阻断 |
| spec/plan 缺头部链接 | 提示补全 | ⚠️ 警告 | 不阻断 |

自查：

```bash
node scripts/harness/validate-harness.mjs
```

严格模式（Phase 2）：`node scripts/harness/validate-harness.mjs --strict`

## 2. 阶段门禁

推荐顺序：

```
create-demand → brainstorming → writing-plans → 开发
```

阶段枚举：

| 阶段 | 条件 | 动作 |
|------|------|------|
| `NO_MODULE` | current/ 下无对应模块 | create-demand |
| `NO_SPEC` | 有 requirements，无 specs/01-dev-spec.md | brainstorming |
| `NO_PLAN` | 有 spec，无 plans/01-dev-plan.md | writing-plans |
| `READY_TO_DEV` | 有 spec 且有 plan | 允许改 src/ |

## 3. 技能调用顺序

| 阶段 | 技能 |
|------|------|
| 入口判断 | `superpowers-harness` |
| 建目录 | `superpowers-demand-workflow` |
| 写 spec | `brainstorming` |
| 写 plan | `writing-plans` |
| 执行开发 | `executing-plans` 或按 plan 开发 |

## 4. 禁止事项

- 写入 `docs/superpowers/specs/`、`plans/`、`archive/`、`reports/` 等旧扁平路径
- 未完成 spec/plan 时主动引导修改 `src/`（宽松模式下用户坚持则警告后继续）

## 5. 升级路径

1. **Phase 1（当前）**：宽松模式，积累 `.harness/warnings.log`
2. **Phase 2**：启用 `--strict`；fix 类型可配置豁免
3. **Phase 3**：pre-commit 默认 strict
