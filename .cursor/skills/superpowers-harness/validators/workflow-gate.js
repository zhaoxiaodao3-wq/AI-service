/**
 * @param {string[]} stagedFiles
 * @param {{ hasSpec: boolean, hasPlan: boolean }[]} modules
 * @returns {Array<{ code: string, message: string, remediation: string[], files?: string[] }>}
 */
export function checkWorkflowGate(stagedFiles, modules) {
  const srcChanges = stagedFiles.filter((f) => f.startsWith('src/'))
  if (srcChanges.length === 0) return []

  if (modules.length === 0) {
    return [{
      code: 'WORKFLOW_GATE_NO_MODULE',
      message: `src/ 有 ${srcChanges.length} 个文件改动，但 superpowers 下找不到任何需求模块。`,
      files: srcChanges,
      remediation: [
        '运行 scripts\\create-demand.bat --type feature --name "你的模块名"',
        '将原始需求写入 requirements/',
        '执行 brainstorming 写 specs/01-dev-spec.md',
        '执行 writing-plans 写 plans/01-dev-plan.md',
      ],
    }]
  }

  const hasActivePlan = modules.some((m) => m.hasSpec && m.hasPlan)
  if (!hasActivePlan) {
    return [{
      code: 'WORKFLOW_GATE_NO_PLAN',
      message: `src/ 有 ${srcChanges.length} 个文件改动，但 superpowers 下找不到活跃的 spec/plan。`,
      files: srcChanges,
      remediation: [
        '运行 scripts\\create-demand.bat --type feature --name "你的模块名"',
        '执行 /brainstorming 写 specs/01-dev-spec.md',
        '执行 /writing-plans 写 plans/01-dev-plan.md',
      ],
    }]
  }

  return []
}
