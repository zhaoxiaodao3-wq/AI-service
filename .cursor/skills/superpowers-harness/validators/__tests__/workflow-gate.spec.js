import { describe, expect, it } from 'vitest'
import { checkWorkflowGate } from '../workflow-gate.js'

describe('checkWorkflowGate', () => {
  it('returns empty when no src changes', () => {
    expect(checkWorkflowGate([], [])).toEqual([])
  })

  it('warns when src changes but no active plan', () => {
    const warnings = checkWorkflowGate(['src/pages/foo.vue'], [
      { hasSpec: false, hasPlan: false },
    ])
    expect(warnings).toHaveLength(1)
    expect(warnings[0].code).toBe('WORKFLOW_GATE_NO_PLAN')
  })

  it('passes when module has spec and plan', () => {
    const warnings = checkWorkflowGate(['src/pages/foo.vue'], [
      { hasSpec: true, hasPlan: true },
    ])
    expect(warnings).toEqual([])
  })

  it('warns when no modules exist', () => {
    const warnings = checkWorkflowGate(['src/pages/foo.vue'], [])
    expect(warnings[0].code).toBe('WORKFLOW_GATE_NO_MODULE')
  })
})
