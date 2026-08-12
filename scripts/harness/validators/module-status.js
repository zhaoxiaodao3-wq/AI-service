import { existsSync, readdirSync } from 'node:fs'
import { join } from 'node:path'
import { discoverModules } from './lib/discover-modules.js'
import { resolveSuperpowersVersion, resolveVersionDir } from './lib/resolve-version.js'

const NEXT_BY_PHASE = {
  NO_MODULE: 'create-demand',
  NO_SPEC: 'brainstorming',
  NO_PLAN: 'writing-plans',
  READY_TO_DEV: '开发 + 交付归档',
  DELIVERED: '无（已完成）或新需求另开模块',
}

/**
 * @param {string} archiveDir
 */
function hasDeliveredArchive(archiveDir) {
  if (!existsSync(archiveDir)) return false
  return readdirSync(archiveDir).some((f) => f.endsWith('-delivered.md'))
}

/**
 * @param {{ hasSpec: boolean, hasPlan: boolean, root: string, dirs: Array<{ name: string, exists: boolean }> }} mod
 */
export function getModulePhase(mod) {
  const archiveDir = join(mod.root, 'archive')
  if (!mod.hasSpec) return 'NO_SPEC'
  if (!mod.hasPlan) return 'NO_PLAN'
  if (!hasDeliveredArchive(archiveDir)) return 'READY_TO_DEV'
  return 'DELIVERED'
}

/**
 * @param {{ hasSpec: boolean, hasPlan: boolean, root: string, type: string, name: string, dirs: Array<{ name: string, exists: boolean }> }} mod
 */
export function getModuleMissing(mod) {
  const missing = []
  for (const { name, exists } of mod.dirs) {
    if (!exists) missing.push(`${name}/`)
  }
  if (!mod.hasSpec) missing.push('specs/01-dev-spec.md')
  if (!mod.hasPlan) missing.push('plans/01-dev-plan.md')
  const phase = getModulePhase(mod)
  if (phase === 'READY_TO_DEV') missing.push('archive/*-delivered.md')
  return missing
}

/**
 * @param {{ type: string, name: string, root: string, hasSpec: boolean, hasPlan: boolean, dirs: Array<{ name: string, exists: boolean }> }} mod
 */
export function toModuleStatus(mod) {
  const phase = getModulePhase(mod)
  const missing = getModuleMissing(mod)
  return {
    type: mod.type,
    name: mod.name,
    path: mod.root.replace(/\\/g, '/'),
    phase,
    next: NEXT_BY_PHASE[phase],
    missing,
    hasSpec: mod.hasSpec,
    hasPlan: mod.hasPlan,
    delivered: phase === 'DELIVERED',
  }
}

/**
 * @param {string} keyword
 * @param {ReturnType<typeof toModuleStatus>[]} statuses
 */
function matchKeyword(keyword, statuses) {
  const k = keyword.trim().toLowerCase()
  if (!k) return statuses
  return statuses.filter(
    (s) =>
      s.name.toLowerCase().includes(k) ||
      s.path.toLowerCase().includes(k) ||
      s.type.toLowerCase().includes(k),
  )
}

/**
 * @param {{ cwd?: string, match?: string }} [options]
 */
export function runHarnessStatus(options = {}) {
  const { cwd = process.cwd(), match = '' } = options
  const superpowersBase = join(cwd, 'docs', 'superpowers')
  const version = resolveSuperpowersVersion(superpowersBase)
  const versionDir = resolveVersionDir(superpowersBase, version)
  const versionRoot = join(superpowersBase, versionDir)
  const modules = discoverModules(versionRoot)
  const statuses = modules.map(toModuleStatus)
  const filtered = matchKeyword(match, statuses)

  return {
    version,
    versionRoot: versionRoot.replace(/\\/g, '/'),
    match: match.trim() || null,
    total: modules.length,
    modules: filtered,
    noMatch: match.trim() && filtered.length === 0,
  }
}
