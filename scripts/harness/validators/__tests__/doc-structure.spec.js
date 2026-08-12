import { describe, expect, it } from 'vitest'
import { mkdtempSync, writeFileSync, mkdirSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { checkDocStructure } from '../doc-structure.js'

describe('checkDocStructure', () => {
  it('warns on legacy path writes', () => {
    const warnings = checkDocStructure(
      ['docs/superpowers/specs/new.md'],
      [],
      '/fake',
    )
    expect(warnings.some((w) => w.code === 'DOC_LEGACY_PATH')).toBe(true)
  })

  it('warns when spec missing Requirement link', () => {
    const base = mkdtempSync(join(tmpdir(), 'sp-'))
    const specPath = join(base, 'specs', '01-dev-spec.md')
    mkdirSync(join(base, 'specs'), { recursive: true })
    writeFileSync(specPath, '# spec\n\nno header\n')
    const mod = {
      root: base,
      name: '测试',
      type: 'feature',
      dirs: [
        { name: 'requirements', exists: true },
        { name: 'specs', exists: true },
        { name: 'plans', exists: true },
        { name: 'archive', exists: true },
      ],
    }
    const warnings = checkDocStructure([], [mod], base)
    expect(warnings.some((w) => w.code === 'DOC_MISSING_REQUIREMENT_LINK')).toBe(true)
  })

  it('warns when plan missing Spec link', () => {
    const base = mkdtempSync(join(tmpdir(), 'sp-'))
    const planPath = join(base, 'plans', '01-dev-plan.md')
    mkdirSync(join(base, 'plans'), { recursive: true })
    writeFileSync(planPath, '# plan\n\nno header\n')
    const mod = {
      root: base,
      name: '测试',
      type: 'feature',
      dirs: [
        { name: 'requirements', exists: true },
        { name: 'specs', exists: true },
        { name: 'plans', exists: true },
        { name: 'archive', exists: true },
      ],
    }
    const warnings = checkDocStructure([], [mod], base)
    expect(warnings.some((w) => w.code === 'DOC_MISSING_SPEC_LINK')).toBe(true)
  })
})
