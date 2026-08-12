import { existsSync, readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'

const LEGACY_PREFIXES = [
  'docs/superpowers/specs/',
  'docs/superpowers/plans/',
  'docs/superpowers/archive/',
  'docs/superpowers/reports/',
]

const REQUIREMENT_LINK_RE = /\*\*Requirement:\*\*\s*\[([^\]]+)\]\(([^)]+)\)/
const SPEC_LINK_RE = /\*\*Spec:\*\*\s*\[([^\]]+)\]\(([^)]+)\)/

/**
 * @param {string[]} stagedFiles
 * @param {Array<{ root: string, name: string, type: string, dirs: Array<{ name: string, exists: boolean }> }>} modules
 * @param {string} _projectRoot
 * @returns {Array<{ code: string, message: string, remediation: string[] }>}
 */
export function checkDocStructure(stagedFiles, modules, _projectRoot) {
  const warnings = []

  for (const file of stagedFiles) {
    const normalized = file.replace(/\\/g, '/')
    if (LEGACY_PREFIXES.some((p) => normalized.startsWith(p))) {
      warnings.push({
        code: 'DOC_LEGACY_PATH',
        message: `禁止写入旧扁平路径：${normalized}`,
        remediation: [
          '使用 scripts\\create-demand.bat 创建模块目录',
          '写入 docs/superpowers/current/{type}/{模块名}/ 下对应子目录',
        ],
      })
    }
  }

  for (const mod of modules) {
    const missingDirs = mod.dirs.filter((d) => !d.exists).map((d) => d.name)
    if (missingDirs.length > 0) {
      warnings.push({
        code: 'DOC_INCOMPLETE_DIRS',
        message: `模块「${mod.name}」缺少目录：${missingDirs.join(', ')}`,
        remediation: ['重新运行 create-demand 或手动补齐四层目录'],
      })
    }

    const specPath = join(mod.root, 'specs', '01-dev-spec.md')
    if (existsSync(specPath)) {
      const content = readFileSync(specPath, 'utf8')
      const match = content.match(REQUIREMENT_LINK_RE)
      if (!match) {
        warnings.push({
          code: 'DOC_MISSING_REQUIREMENT_LINK',
          message: `spec 缺少 **Requirement:** 头部链接：${specPath}`,
          remediation: ['在 spec 头部添加：**Requirement:** [requirements/xxx.md](../requirements/xxx.md)'],
        })
      } else {
        const target = join(dirname(specPath), match[2])
        if (!existsSync(target)) {
          warnings.push({
            code: 'DOC_BROKEN_LINK',
            message: `spec 的 Requirement 链接目标不存在：${match[2]}`,
            remediation: ['创建对应 requirements 文件或修正链接路径'],
          })
        }
      }
    }

    const planPath = join(mod.root, 'plans', '01-dev-plan.md')
    if (existsSync(planPath)) {
      const content = readFileSync(planPath, 'utf8')
      const match = content.match(SPEC_LINK_RE)
      if (!match) {
        warnings.push({
          code: 'DOC_MISSING_SPEC_LINK',
          message: `plan 缺少 **Spec:** 头部链接：${planPath}`,
          remediation: ['在 plan 头部添加：**Spec:** [specs/01-dev-spec.md](../specs/01-dev-spec.md)'],
        })
      } else {
        const target = join(dirname(planPath), match[2])
        if (!existsSync(target)) {
          warnings.push({
            code: 'DOC_BROKEN_LINK',
            message: `plan 的 Spec 链接目标不存在：${match[2]}`,
            remediation: ['创建 specs/01-dev-spec.md 或修正链接路径'],
          })
        }
      }
    }
  }

  return warnings
}
