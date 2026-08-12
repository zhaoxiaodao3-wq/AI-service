#!/usr/bin/env node
import { runHarnessStatus } from './validators/module-status.js'

const args = process.argv.slice(2)
let match = ''
let json = false

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--match' && args[i + 1]) {
    match = args[++i]
  } else if (args[i] === '--json') {
    json = true
  } else if (args[i] === '--help' || args[i] === '-h') {
    console.log(`用法: node scripts/harness/status.mjs [--match <关键词>] [--json]

示例:
  node scripts/harness/status.mjs
  node scripts/harness/status.mjs --match 语言可理解度
  pnpm harness:status -- --match fix`)
    process.exit(0)
  }
}

const result = runHarnessStatus({ cwd: process.cwd(), match })

if (json) {
  console.log(JSON.stringify(result, null, 2))
  process.exit(result.noMatch ? 1 : 0)
}

console.log(`Superpowers ${result.version} | 模块 ${result.total} 个`)
if (result.match) console.log(`筛选: "${result.match}"`)

if (result.noMatch) {
  console.log('\n未匹配到模块 → 阶段: NO_MODULE → 下一步: create-demand')
  process.exit(1)
}

if (result.modules.length === 0) {
  console.log('\n（当前版本下无需求模块）')
  process.exit(0)
}

for (const m of result.modules) {
  const miss = m.missing.length ? ` | 缺: ${m.missing.join(', ')}` : ''
  console.log(`\n${m.type}/${m.name}`)
  console.log(`  阶段: ${m.phase}`)
  console.log(`  下一步: ${m.next}${miss}`)
}

process.exit(0)
