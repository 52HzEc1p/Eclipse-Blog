import MarkdownIt from 'markdown-it'
// 按需注册语言，避免引入全量 highlight.js（全量约 1MB）
import hljs from 'highlight.js/lib/core'
import bash from 'highlight.js/lib/languages/bash'
import shell from 'highlight.js/lib/languages/shell'
import sql from 'highlight.js/lib/languages/sql'
import python from 'highlight.js/lib/languages/python'
import javascript from 'highlight.js/lib/languages/javascript'
import typescript from 'highlight.js/lib/languages/typescript'
import json from 'highlight.js/lib/languages/json'
import http from 'highlight.js/lib/languages/http'
import nginx from 'highlight.js/lib/languages/nginx'
import php from 'highlight.js/lib/languages/php'
import java from 'highlight.js/lib/languages/java'
import c from 'highlight.js/lib/languages/c'
import cpp from 'highlight.js/lib/languages/cpp'
import csharp from 'highlight.js/lib/languages/csharp'
import powershell from 'highlight.js/lib/languages/powershell'
import yaml from 'highlight.js/lib/languages/yaml'
import markdown from 'highlight.js/lib/languages/markdown'
import xml from 'highlight.js/lib/languages/xml'
import ini from 'highlight.js/lib/languages/ini'
import dockerfile from 'highlight.js/lib/languages/dockerfile'
import go from 'highlight.js/lib/languages/go'
import rust from 'highlight.js/lib/languages/rust'
import diff from 'highlight.js/lib/languages/diff'
import css from 'highlight.js/lib/languages/css'
import scss from 'highlight.js/lib/languages/scss'
import lua from 'highlight.js/lib/languages/lua'
import ruby from 'highlight.js/lib/languages/ruby'
import perl from 'highlight.js/lib/languages/perl'
import plaintext from 'highlight.js/lib/languages/plaintext'

hljs.registerLanguage('bash', bash)
hljs.registerLanguage('shell', shell)
hljs.registerLanguage('sh', shell)
hljs.registerLanguage('sql', sql)
hljs.registerLanguage('python', python)
hljs.registerLanguage('py', python)
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('js', javascript)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('ts', typescript)
hljs.registerLanguage('json', json)
hljs.registerLanguage('http', http)
hljs.registerLanguage('nginx', nginx)
hljs.registerLanguage('php', php)
hljs.registerLanguage('java', java)
hljs.registerLanguage('c', c)
hljs.registerLanguage('cpp', cpp)
hljs.registerLanguage('csharp', csharp)
hljs.registerLanguage('cs', csharp)
hljs.registerLanguage('powershell', powershell)
hljs.registerLanguage('ps1', powershell)
hljs.registerLanguage('yaml', yaml)
hljs.registerLanguage('yml', yaml)
hljs.registerLanguage('markdown', markdown)
hljs.registerLanguage('md', markdown)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('html', xml)
hljs.registerLanguage('ini', ini)
hljs.registerLanguage('dockerfile', dockerfile)
hljs.registerLanguage('go', go)
hljs.registerLanguage('rust', rust)
hljs.registerLanguage('diff', diff)
hljs.registerLanguage('css', css)
hljs.registerLanguage('scss', scss)
hljs.registerLanguage('lua', lua)
hljs.registerLanguage('ruby', ruby)
hljs.registerLanguage('perl', perl)
hljs.registerLanguage('plaintext', plaintext)
hljs.registerLanguage('text', plaintext)

// 配置 markdown-it
const md = new MarkdownIt({
  html: false,        // 禁用原始 HTML (安全)
  linkify: true,      // 自动识别链接
  typographer: true,  // 智能引号
  highlight(str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        const result = hljs.highlight(str, { language: lang })
        return `<pre class="hljs-code"><code class="hljs language-${lang}">${result.value}</code></pre>`
      } catch (_) {}
    }
    // 无语言标记时自动检测
    const result = hljs.highlightAuto(str)
    return `<pre class="hljs-code"><code class="hljs">${result.value}</code></pre>`
  },
})

// 给标题加 id (用于目录锚点)
md.renderer.rules.heading_open = (tokens, idx) => {
  const token = tokens[idx]
  const nextToken = tokens[idx + 1]
  const level = token.tag
  const text = nextToken.children.reduce((acc, t) => acc + t.content, '')
  const slug = text.toLowerCase().replace(/\s+/g, '-').replace(/[^\w一-龥-]/g, '')
  return `<${level} id="${slug}">`
}

// 给代码块添加 data-lang 属性 (方便前端提取语言标签)
const defaultFence = md.renderer.rules.fence || ((tokens, idx, options, env, self) => {
  return self.renderToken(tokens, idx, options)
})
md.renderer.rules.fence = (tokens, idx, options, env, self) => {
  const token = tokens[idx]
  const lang = token.info.trim().split(/\s+/)[0] || ''
  const result = defaultFence(tokens, idx, options, env, self)
  return result.replace('<pre', `<pre data-lang="${lang}"`)
}

// 给 <table> 包裹容器 (支持横向滚动)
const defaultTableOpen = md.renderer.rules.table_open || ((tokens, idx, options, env, self) => {
  return self.renderToken(tokens, idx, options)
})
md.renderer.rules.table_open = (tokens, idx, options, env, self) => {
  return '<div class="table-wrapper">' + defaultTableOpen(tokens, idx, options, env, self)
}
const defaultTableClose = md.renderer.rules.table_close || ((tokens, idx, options, env, self) => {
  return self.renderToken(tokens, idx, options)
})
md.renderer.rules.table_close = (tokens, idx, options, env, self) => {
  return defaultTableClose(tokens, idx, options, env, self) + '</div>'
}

// 给 <img> 添加 loading="lazy"
const defaultImage = md.renderer.rules.image || ((tokens, idx, options, env, self) => {
  return self.renderToken(tokens, idx, options)
})
md.renderer.rules.image = (tokens, idx, options, env, self) => {
  const token = tokens[idx]
  const src = token.attrGet('src') || ''
  const alt = token.attrGet('alt') || ''
  const title = token.attrGet('title') || ''
  let result = `<img src="${src}" alt="${alt}" loading="lazy"`
  if (title) result += ` title="${title}"`
  result += ' />'
  return result
}

/**
 * 渲染 Markdown 为 HTML
 */
export function renderMarkdown(content) {
  if (!content) return ''
  return md.render(content)
}

/**
 * 从 Markdown 内容提取目录 (TOC)
 */
export function extractTOC(content) {
  if (!content) return []

  const headingRegex = /^(#{1,3})\s+(.+)$/gm
  const toc = []
  let match

  while ((match = headingRegex.exec(content)) !== null) {
    const level = match[1].length
    const text = match[2].trim()
    const slug = text.toLowerCase().replace(/\s+/g, '-').replace(/[^\w一-龥-]/g, '')
    toc.push({ level, text, slug })
  }

  return toc
}
