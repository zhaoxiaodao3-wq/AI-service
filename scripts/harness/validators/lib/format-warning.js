export function formatWarning(warning) {
  const lines = [
    `⚠️  [HARNESS:${warning.code}]`,
    `    ${warning.message}`,
    '',
    '    修复步骤：',
    ...warning.remediation.map((s, i) => `    ${i + 1}. ${s}`),
    '',
    `    模式：${warning.mode === 'strict' ? '严格（阻断提交）' : '宽松（不阻断提交）'}。自查：node scripts/harness/validate-harness.mjs`,
  ]
  return lines.join('\n')
}
