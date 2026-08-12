import { existsSync, readdirSync, statSync } from 'node:fs'
import { join } from 'node:path'

const TYPES = ['feature', 'ui-style', 'api-adapter', 'fix']

export function discoverModules(versionRoot) {
  if (!existsSync(versionRoot)) return []
  const modules = []
  for (const type of TYPES) {
    const typeDir = join(versionRoot, type)
    if (!existsSync(typeDir)) continue
    for (const name of readdirSync(typeDir)) {
      const moduleRoot = join(typeDir, name)
      if (!statSync(moduleRoot).isDirectory()) continue
      modules.push({
        type,
        name,
        root: moduleRoot,
        hasSpec: existsSync(join(moduleRoot, 'specs', '01-dev-spec.md')),
        hasPlan: existsSync(join(moduleRoot, 'plans', '01-dev-plan.md')),
        dirs: ['requirements', 'specs', 'plans', 'archive'].map((d) => ({
          name: d,
          exists: existsSync(join(moduleRoot, d)),
        })),
      })
    }
  }
  return modules
}
