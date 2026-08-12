import { describe, expect, it } from 'vitest'
import { mkdtempSync, writeFileSync, mkdirSync, symlinkSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { resolveSuperpowersVersion, resolveVersionDir } from '../lib/resolve-version.js'
import { discoverModules } from '../lib/discover-modules.js'

describe('resolveSuperpowersVersion', () => {
  it('reads current-version.txt', () => {
    const base = mkdtempSync(join(tmpdir(), 'sp-'))
    writeFileSync(join(base, 'current-version.txt'), 'v1.4.8\n')
    expect(resolveSuperpowersVersion(base)).toBe('v1.4.8')
  })

  it('normalizes two-part version', () => {
    const base = mkdtempSync(join(tmpdir(), 'sp-'))
    writeFileSync(join(base, 'current-version.txt'), 'v1.4\n')
    expect(resolveSuperpowersVersion(base)).toBe('v1.4.0')
  })
})

describe('discoverModules', () => {
  it('finds modules under type dirs', () => {
    const base = mkdtempSync(join(tmpdir(), 'sp-'))
    const mod = join(base, 'v1.0.0', 'feature', '测试模块')
    mkdirSync(join(mod, 'requirements'), { recursive: true })
    mkdirSync(join(mod, 'specs'), { recursive: true })
    const modules = discoverModules(join(base, 'v1.0.0'))
    expect(modules).toHaveLength(1)
    expect(modules[0].name).toBe('测试模块')
    expect(modules[0].type).toBe('feature')
  })
})
