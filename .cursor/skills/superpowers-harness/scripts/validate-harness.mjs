#!/usr/bin/env node
import { runHarnessValidation, writeWarningsLog } from '../validators/index.js'
import { formatWarning } from '../validators/lib/format-warning.js'

const strict = process.argv.includes('--strict')
const projectRoot = process.cwd()

const result = runHarnessValidation({ cwd: projectRoot, strict })

for (const w of result.warnings) {
  console.warn(formatWarning(w))
}

if (result.warnings.length > 0) {
  writeWarningsLog(projectRoot, result)
}

const exitCode = strict && result.warnings.length > 0 ? 1 : 0
process.exit(exitCode)
