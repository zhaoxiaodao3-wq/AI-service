import { describe, expect, it } from 'vitest'
import { runHarnessValidation } from '../index.js'

describe('runHarnessValidation', () => {
  it('returns loose mode by default', () => {
    const result = runHarnessValidation({ cwd: process.cwd(), strict: false })
    expect(result.mode).toBe('loose')
  })
})
