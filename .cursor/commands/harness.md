---
description: 按 Superpowers Harness 完整流程处理开发需求（含两次用户确认暂停，fix 不例外）
---

请读取并严格遵循 **superpowers-harness-run** 技能，对以下需求执行 Harness 完整流程。

**硬性要求：**

1. 先 `pnpm harness:status -- --match "<关键词>"`，回复开头输出 `[Harness]` 状态行
2. **P1** 方案确认 → **P2** spec 确认 → **P3** 执行方式选择 → 然后才能改 `src/`
3. fix / 纠正 / 补充需求 **不得跳过** 上述暂停点
4. 改 `src/` 前后运行 `pnpm harness:check`

需求：

$ARGUMENTS
