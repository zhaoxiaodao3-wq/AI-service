import { join } from 'node:path'
import { mkdirSync, appendFileSync, existsSync } from 'node:fs'
import { resolveSuperpowersVersion, resolveVersionDir } from './lib/resolve-version.js'
import { discoverModules } from './lib/discover-modules.js'
import { getStagedFiles } from './lib/git-staged.js'
import { checkWorkflowGate } from './workflow-gate.js'
import { checkDocStructure } from './doc-structure.js'

export function runHarnessValidation(options = {}) {
  const { cwd = process.cwd(), strict = false } = options
  const superpowersBase = join(cwd, 'docs', 'superpowers')
  const version = resolveSuperpowersVersion(superpowersBase)
  const versionDir = resolveVersionDir(superpowersBase, version)
  const versionRoot = join(superpowersBase, versionDir)
  const modules = discoverModules(versionRoot)
  const staged = getStagedFiles(cwd)

  const mode = strict ? 'strict' : 'loose'
  const raw = [
    ...checkWorkflowGate(staged, modules),
    ...checkDocStructure(staged, modules, cwd),
  ].map((w) => ({ ...w, mode }))

  return { warnings: raw, staged, modules, mode }
}

export function writeWarningsLog(cwd, result) {
  const logDir = join(cwd, '.harness')
  if (!existsSync(logDir)) mkdirSync(logDir, { recursive: true })
  const entry = {
    timestamp: new Date().toISOString(),
    mode: result.mode,
    warnings: result.warnings.map(({ code, files }) => ({ code, files })),
    exitCode: result.warnings.length > 0 && result.mode === 'strict' ? 1 : 0,
  }
  appendFileSync(join(logDir, 'warnings.log'), JSON.stringify(entry) + '\n', 'utf8')
}
