import { execSync } from 'node:child_process'

export function getStagedFiles(cwd = process.cwd()) {
  try {
    const out = execSync('git diff --cached --name-only --diff-filter=ACMR', {
      cwd,
      encoding: 'utf8',
    })
    return out.split('\n').map((l) => l.trim()).filter(Boolean)
  } catch {
    return []
  }
}
