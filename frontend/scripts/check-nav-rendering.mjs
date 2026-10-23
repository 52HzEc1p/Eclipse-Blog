import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const source = readFileSync(resolve(root, 'src/components/effects/GooeyNav.vue'), 'utf8')

const failures = []

if (!source.includes('class="effect text"')) {
  failures.push('GooeyNav should render the effect text layer used by the active pill.')
}

const navLinkRule = source.match(/\.gooey-nav-container nav ul li a\s*\{[\s\S]*?\}/)?.[0] || ''
if (!/white-space:\s*nowrap/.test(navLinkRule)) {
  failures.push('GooeyNav links should keep labels on one line.')
}

const activeLinkRule = source.match(/\.gooey-nav-container nav ul li\.active a\s*\{[\s\S]*?\}/)?.[0] || ''
if (!/color:\s*transparent/.test(activeLinkRule)) {
  failures.push('The active nav link text should be transparent so only the effect text is visible.')
}

const effectTextRule = source.match(/\.gooey-nav-container \.effect\.text\s*\{[\s\S]*?\}/)?.[0] || ''
if (!/white-space:\s*nowrap/.test(effectTextRule)) {
  failures.push('The effect text layer should keep labels on one line.')
}

if (failures.length) {
  console.error(failures.join('\n'))
  process.exit(1)
}

console.log('Nav rendering checks passed.')
