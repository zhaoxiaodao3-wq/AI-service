import { existsSync, readFileSync, lstatSync, readlinkSync } from 'node:fs'
import { join } from 'node:path'

export function normalizeVersion(ver) {
  const trimmed = ver.trim()
  if (/^v\d+\.\d+$/.test(trimmed)) return `${trimmed}.0`
  return trimmed
}

export function resolveSuperpowersVersion(superpowersBase) {
  const currentLink = join(superpowersBase, 'current')
  if (existsSync(currentLink) && lstatSync(currentLink).isSymbolicLink()) {
    return normalizeVersion(readlinkSync(currentLink).replace(/^\.\//, ''))
  }
  const versionFile = join(superpowersBase, 'current-version.txt')
  if (existsSync(versionFile)) {
    return normalizeVersion(readFileSync(versionFile, 'utf8'))
  }
  return 'v1.0.0'
}

export function resolveVersionDir(superpowersBase, version) {
  const normalized = normalizeVersion(version)
  if (existsSync(join(superpowersBase, normalized))) return normalized
  const legacy = normalized.replace(/\.0$/, '')
  if (legacy !== normalized && existsSync(join(superpowersBase, legacy))) return legacy
  return normalized
}
