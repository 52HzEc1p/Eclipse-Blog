<script setup>
import { computed, onMounted, onUnmounted, ref, nextTick, watch } from 'vue'
import { extractTOC, renderMarkdown } from '../../utils/markdown'
import ParticleCanvas from '../effects/ParticleCanvas.vue'

const props = defineProps({
  post: { type: Object, required: true },
  sectionLabel: { type: String, default: '' },
  sectionClass: { type: String, default: '' },
})

const renderedContent = computed(() => renderMarkdown(props.post.content))
const tocItems = computed(() => extractTOC(props.post.content).filter(item => item.level <= 3))
const mobileTocOpen = ref(false)

// 发布日期只展示年月日，避免原始 ISO 串直接上屏
const formattedDate = computed(() => {
  const v = props.post.published_at
  if (!v) return ''
  const d = new Date(String(v).replace(' ', 'T'))
  if (Number.isNaN(d.getTime())) return String(v).slice(0, 10)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
})

// 阅读进度
const progress = ref(0)

const videoEmbed = computed(() => {
  if (props.post.post_type !== 'video' || !props.post.video_url) return null
  const url = props.post.video_url

  const biliMatch = url.match(/bilibili\.com\/video\/(BV[\w]+)/)
  if (biliMatch) {
    return { type: 'bilibili', src: `https://player.bilibili.com/player.html?bvid=${biliMatch[1]}&high_quality=1` }
  }

  const ytMatch = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]+)/)
  if (ytMatch) {
    return { type: 'youtube', src: `https://www.youtube.com/embed/${ytMatch[1]}` }
  }

  const vimeoMatch = url.match(/vimeo\.com\/(\d+)/)
  if (vimeoMatch) {
    return { type: 'vimeo', src: `https://player.vimeo.com/video/${vimeoMatch[1]}` }
  }

  if (/\.(mp4|webm|mov)(\?.*)?$/i.test(url)) {
    return { type: 'video', src: url }
  }

  return null
})

// 代码块: 添加语言标签 + 复制按钮
onMounted(() => {
  window.addEventListener('scroll', updateProgress)
  updateProgress()

  nextTick(() => {
    enhanceCodeBlocks()
  })
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateProgress)
})

watch(() => props.post.id, () => {
  nextTick(() => {
    enhanceCodeBlocks()
  })
})

function updateProgress() {
  const scrollTop = window.scrollY
  const docHeight = document.documentElement.scrollHeight - window.innerHeight
  progress.value = docHeight > 0 ? Math.min(100, (scrollTop / docHeight) * 100) : 0
}

function enhanceCodeBlocks() {
  document.querySelectorAll('.article-body pre.hljs-code').forEach(pre => {
    if (pre.querySelector('.code-copy')) return

    const lang = pre.getAttribute('data-lang') || ''

    // 语言标签
    if (lang) {
      const label = document.createElement('span')
      label.className = 'code-lang'
      label.textContent = lang
      pre.appendChild(label)
    }

    // 复制按钮
    if (pre.scrollHeight > 560) {
      pre.classList.add('code-collapsible', 'is-collapsed')
      const expandBtn = document.createElement('button')
      expandBtn.type = 'button'
      expandBtn.className = 'code-expand'
      expandBtn.textContent = '展开代码'
      expandBtn.setAttribute('aria-expanded', 'false')
      expandBtn.addEventListener('click', () => {
        const collapsed = pre.classList.toggle('is-collapsed')
        expandBtn.textContent = collapsed ? '展开代码' : '收起代码'
        expandBtn.setAttribute('aria-expanded', String(!collapsed))
      })
      pre.appendChild(expandBtn)
    }

    const btn = document.createElement('button')
    btn.type = 'button'
    btn.className = 'code-copy'
    btn.setAttribute('aria-label', '复制代码')
    btn.innerHTML = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>'
    btn.addEventListener('click', () => {
      const code = pre.querySelector('code')
      if (!code) return
      navigator.clipboard.writeText(code.innerText).then(() => {
        btn.classList.add('copied')
        btn.setAttribute('aria-label', '代码已复制')
        btn.innerHTML = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
        setTimeout(() => {
          btn.classList.remove('copied')
          btn.setAttribute('aria-label', '复制代码')
          btn.innerHTML = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>'
        }, 2000)
      })
    })
    pre.appendChild(btn)
  })
}

</script>

<template>
  <div class="post-detail" :class="sectionClass">
    <!-- 粒子背景 -->
    <ParticleCanvas
      :enable-mouse-follow="false"
      :particle-density="0.15"
      :max-particles="160"
      :speed-multiplier="2.0"
      :connection-distance="130"
      :hue="200"
      :hue-range="40"
      :fixed="true"
    />

    <!-- 阅读进度条 -->
    <div class="reading-progress" :style="{ width: progress + '%' }"></div>

    <div v-if="tocItems.length" class="mobile-toc">
      <button
        type="button"
        class="mobile-toc-toggle"
        :aria-expanded="mobileTocOpen"
        aria-controls="mobile-article-toc"
        @click="mobileTocOpen = !mobileTocOpen"
      >
        目录
      </button>
      <div
        v-show="mobileTocOpen"
        id="mobile-article-toc"
        class="mobile-toc-panel"
      >
        <a
          v-for="item in tocItems"
          :key="`mobile-${item.slug}-${item.level}`"
          :href="`#${item.slug}`"
          class="mobile-toc-link"
          :class="`level-${item.level}`"
          @click="mobileTocOpen = false"
        >
          {{ item.text }}
        </a>
      </div>
    </div>

    <div class="container">
      <!-- 统一文章卡片 -->
      <div class="article-layout">
      <article class="article-card">
        <header class="article-header">
          <span class="section-tag" :class="sectionClass">{{ sectionLabel }}</span>
          <h1 class="article-title">{{ post.title }}</h1>
          <p class="article-excerpt" v-if="post.excerpt">{{ post.excerpt }}</p>
          <div class="article-meta">
            <span class="meta-item" v-if="post.category">{{ post.category.name }}</span>
            <span class="meta-item">{{ post.views_count }} 阅读</span>
            <span class="meta-item" v-if="formattedDate">{{ formattedDate }}</span>
          </div>
          <div class="article-tags" v-if="post.tags?.length">
            <span
              v-for="tag in post.tags"
              :key="tag.id"
              class="tag"
              :style="{ borderColor: tag.color, color: tag.color }"
            >{{ tag.name }}</span>
          </div>
        </header>

        <div class="article-divider"></div>

        <!-- 视频嵌入 (iframe) -->
        <div class="video-embed" v-if="videoEmbed && videoEmbed.type !== 'video'">
          <div class="video-wrapper">
            <iframe
              :src="videoEmbed.src"
              frameborder="0"
              allowfullscreen
              loading="lazy"
              :allow="videoEmbed.type !== 'bilibili' ? 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture' : ''"
            ></iframe>
          </div>
        </div>

        <!-- 视频嵌入 (MP4/WebM 直链) -->
        <div class="video-embed" v-if="videoEmbed && videoEmbed.type === 'video'">
          <video
            :src="videoEmbed.src"
            controls
            preload="metadata"
            class="direct-video"
          ></video>
        </div>

        <!-- 文章正文 -->
        <div class="article-body" v-html="renderedContent"></div>
      </article>

      <aside v-if="tocItems.length" class="toc-panel" aria-label="文章目录">
        <div class="toc-inner">
          <span class="toc-kicker">ON THIS PAGE</span>
          <a
            v-for="item in tocItems"
            :key="`${item.slug}-${item.level}`"
            :href="`#${item.slug}`"
            class="toc-link"
            :class="`level-${item.level}`"
          >
            {{ item.text }}
          </a>
        </div>
      </aside>
      </div>

    </div>
  </div>
</template>

<style lang="scss" scoped>
.post-detail {
  padding: 88px 0 110px;
  min-height: 100vh;
  background:
    radial-gradient(circle at 18% 0%, rgba(34, 211, 238, 0.09), transparent 32%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.015), transparent 28%);
}

.container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 20px;
  position: relative;
  z-index: 1;
}

.article-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 220px;
  gap: 22px;
  align-items: start;
}

.toc-panel {
  position: sticky;
  top: 92px;
}

.toc-inner {
  padding: 18px 16px;
  border: 1px solid rgba(34, 211, 238, 0.12);
  border-radius: 8px;
  background: rgba(9, 12, 18, 0.62);
  backdrop-filter: blur(16px);
}

.toc-kicker {
  display: block;
  margin-bottom: 12px;
  color: var(--color-ctf);
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.1em;
}

.toc-link {
  display: block;
  padding: 7px 0;
  color: rgba(224, 227, 229, 0.62);
  font-size: 13px;
  line-height: 1.35;
  text-decoration: none;
  border-top: 1px solid rgba(255, 255, 255, 0.045);
  transition: color 0.2s ease, transform 0.2s ease;

  &:hover {
    color: #8ef7ff;
    transform: translateX(3px);
  }

  &.level-3 {
    padding-left: 12px;
    font-size: 12px;
    color: rgba(224, 227, 229, 0.5);
  }
}

// === 统一文章卡片 ===
.article-card {
  min-width: 0;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.035), rgba(255, 255, 255, 0.012)),
    rgba(12, 13, 19, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  box-shadow:
    0 18px 70px rgba(0, 0, 0, 0.26),
    inset 0 1px 0 rgba(255, 255, 255, 0.06);
  overflow: hidden;
  padding: 40px 50px 48px;
}

.article-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.28), transparent);
  margin: 26px 0 30px;
}

// === 阅读进度条 ===
.reading-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 2px;
  background: var(--color-ctf);
  z-index: 200;
  transition: width 0.1s linear;
  box-shadow: 0 0 8px rgba(34, 211, 238, 0.4);
}

.mobile-toc {
  display: none;
}

.mobile-toc-toggle {
  position: fixed;
  right: 16px;
  bottom: 18px;
  z-index: 210;
  min-height: 44px;
  padding: 0 16px;
  border: 1px solid rgba(34, 211, 238, 0.3);
  border-radius: 999px;
  background: rgba(6, 10, 16, 0.86);
  color: #b8f4ff;
  font: 700 13px/1 var(--font-body);
  backdrop-filter: blur(16px);
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.32);
}

.mobile-toc-panel {
  position: fixed;
  left: 14px;
  right: 14px;
  bottom: 74px;
  z-index: 210;
  max-height: min(56vh, 420px);
  overflow: auto;
  padding: 12px;
  border: 1px solid rgba(34, 211, 238, 0.18);
  border-radius: 8px;
  background: rgba(7, 11, 18, 0.94);
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.42);
}

.mobile-toc-link {
  display: block;
  padding: 10px 8px;
  color: rgba(224, 247, 250, 0.78);
  font-size: 14px;
  line-height: 1.35;
  text-decoration: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);

  &.level-3 {
    padding-left: 22px;
    color: rgba(224, 247, 250, 0.58);
    font-size: 13px;
  }
}

// === 文章头部 ===
.article-header {
  max-width: 760px;
  text-align: left;
  margin: 0 auto;
}

.section-tag {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  padding: 6px 12px;
  border-radius: 999px;

  &.ctf { color: var(--color-ctf); background: rgba(34, 211, 238, 0.1); border: 1px solid rgba(34, 211, 238, 0.18); }
  &.editing { color: var(--color-editing); background: rgba(244, 114, 182, 0.1); border: 1px solid rgba(244, 114, 182, 0.18); }
  &.games { color: var(--color-games); background: rgba(167, 139, 250, 0.1); border: 1px solid rgba(167, 139, 250, 0.18); }
}

.article-title {
  font-family: var(--font-heading);
  font-size: clamp(28px, 4.2vw, 42px);
  font-weight: 700;
  letter-spacing: 0;
  line-height: 1.05;
  margin: 18px 0 14px;
  text-wrap: balance;
}

.article-excerpt {
  font-size: 15px;
  color: rgba(222, 229, 235, 0.68);
  line-height: 1.68;
}

.article-meta {
  display: flex;
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 20px;

  .meta-item {
    font-size: 13px;
    color: var(--color-ink-muted);
  }
}

.article-tags {
  display: flex;
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;

  .tag {
    font-size: 12px;
    padding: 4px 9px;
    border: 1px solid;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.035);
  }
}

// === 视频嵌入 ===
.video-embed {
  max-width: 100%;
  margin: 0 0 32px;
}

.video-wrapper {
  position: relative;
  padding-bottom: 56.25%;
  height: 0;
  overflow: hidden;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-hairline);

  iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }
}

.direct-video {
  width: 100%;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-hairline);
  aspect-ratio: 16 / 9;
  background: #000;
}

// === 文章正文 ===
.article-body {
  flex: 1;
  min-width: 0;
  max-width: 760px;
  margin: 0 auto;
  font-size: 14.75px;
  line-height: 1.72;
  color: rgba(224, 227, 229, 0.84);

  :deep(h1), :deep(h2), :deep(h3), :deep(h4), :deep(h5), :deep(h6) {
    font-family: var(--font-heading);
    font-weight: 700;
    color: var(--color-ink);
    scroll-margin-top: 88px;
  }

  :deep(h1) {
    font-size: 26px;
    letter-spacing: 0;
    line-height: 1.12;
    margin: 36px 0 14px;
  }
  :deep(h2) {
    position: relative;
    font-size: 21px;
    font-weight: 600;
    letter-spacing: 0;
    line-height: 1.18;
    margin: 34px 0 14px;
    padding: 10px 0 10px 14px;
    border-left: 3px solid var(--color-ctf);
    border-bottom: 1px solid rgba(34, 211, 238, 0.16);
    background: linear-gradient(90deg, rgba(34, 211, 238, 0.07), transparent 70%);
  }
  :deep(h3) {
    font-size: 17.5px;
    font-weight: 600;
    margin: 26px 0 10px;
    color: #eefcff;
  }

  :deep(h4) {
    font-size: 15.5px;
    margin: 22px 0 8px;
    color: #b8f4ff;
  }

  :deep(h5),
  :deep(h6) {
    font-size: 14px;
    margin: 18px 0 7px;
    color: rgba(184, 244, 255, 0.82);
  }

  :deep(p) {
    margin: 12px 0;
  }

  :deep(a) {
    color: var(--color-ctf);
    text-decoration: none;
    transition: color 0.2s;
  }

  :deep(a:hover) {
    color: #67e8f9;
  }

  :deep(ul), :deep(ol) {
    padding-left: 24px;
    margin: 14px 0;
  }

  :deep(li) {
    margin: 6px 0;
    padding: 6px 10px 6px 12px;
    border-left: 2px solid rgba(34, 211, 238, 0.22);
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.022);
  }

  :deep(strong) {
    color: #eefcff;
    font-weight: 700;
  }

  :deep(blockquote) {
    border-left: 3px solid var(--color-ctf);
    padding: 14px 18px;
    margin: 22px 0;
    background:
      linear-gradient(90deg, rgba(34, 211, 238, 0.1), rgba(34, 211, 238, 0.03)),
      rgba(255, 255, 255, 0.025);
    border-radius: 0 8px 8px 0;
    color: rgba(221, 245, 250, 0.78);

    p { margin: 6px 0; }
  }

  // 表格
  :deep(.table-wrapper) {
    overflow-x: auto;
    margin: 22px 0;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.025);
  }

  :deep(table) {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;

    th, td {
      padding: 10px 12px;
      border: 1px solid rgba(255, 255, 255, 0.07);
      text-align: left;
    }

    th {
      background: rgba(34, 211, 238, 0.08);
      font-weight: 600;
      color: var(--color-ink);
    }

    td {
      color: rgba(224, 227, 229, 0.82);
    }
  }

  // 代码块
  :deep(pre.hljs-code) {
    position: relative;
    background:
      linear-gradient(180deg, rgba(34, 211, 238, 0.055), transparent 48%),
      #090b12;
    border: 1px solid rgba(34, 211, 238, 0.2);
    border-radius: 8px;
    padding: 38px 16px 16px;
    overflow-x: auto;
    margin: 18px 0;
    max-width: 100%;
    box-sizing: border-box;
    font-family: var(--font-mono);
    font-size: 13px;
    line-height: 1.58;
    font-variant-ligatures: contextual;
    box-shadow:
      inset 0 1px 0 rgba(255, 255, 255, 0.05),
      0 14px 42px rgba(0, 0, 0, 0.18);
  }

  :deep(pre.hljs-code code) {
    font-family: var(--font-mono);
    font-size: inherit;
    letter-spacing: 0;
    tab-size: 2;
  }

  // 语言标签
  :deep(.code-lang) {
    position: absolute;
    top: 12px;
    left: 16px;
    transform: none;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #041015;
    background: var(--color-ctf);
    padding: 3px 10px;
    border-radius: 9999px;
    border: 1px solid rgba(142, 247, 255, 0.68);
    box-shadow: 0 0 16px rgba(34, 211, 238, 0.18);
  }

  // 复制按钮
  :deep(.code-copy) {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 32px;
    height: 32px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--color-ink-muted);
    cursor: pointer;
    display: grid;
    place-items: center;
    opacity: 0;
    transition: opacity 0.2s, background 0.2s, color 0.2s;
  }

  :deep(.code-copy:hover) {
    background: rgba(255, 255, 255, 0.08);
    color: var(--color-ink);
  }

  :deep(.code-copy:focus-visible),
  :deep(.code-expand:focus-visible) {
    opacity: 1;
    outline: 2px solid rgba(34, 211, 238, 0.65);
    outline-offset: 2px;
  }

  :deep(.code-copy.copied) {
    color: var(--color-ctf);
    border-color: rgba(34, 211, 238, 0.3);
  }

  :deep(pre.hljs-code:hover .code-copy) {
    opacity: 1;
  }

  :deep(pre.hljs-code.code-collapsible) {
    padding-bottom: 64px;
  }

  :deep(pre.hljs-code.code-collapsible.is-collapsed) {
    max-height: 560px;
    overflow-x: auto;
    overflow-y: hidden;
  }

  :deep(pre.hljs-code.code-collapsible.is-collapsed::after) {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 120px;
    pointer-events: none;
    background: linear-gradient(180deg, transparent, #090b12 72%);
  }

  :deep(.code-expand) {
    position: absolute;
    left: 50%;
    bottom: 14px;
    z-index: 2;
    min-height: 34px;
    transform: translateX(-50%);
    padding: 0 14px;
    border: 1px solid rgba(34, 211, 238, 0.24);
    border-radius: 999px;
    background: rgba(7, 13, 18, 0.92);
    color: #8ef7ff;
    font: 700 12px/1 var(--font-body);
    cursor: pointer;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.28);
  }

  :deep(code:not(.hljs)) {
    font-family: var(--font-mono);
    font-size: 0.9em;
    background: rgba(34, 211, 238, 0.12);
    border: 1px solid rgba(34, 211, 238, 0.12);
    padding: 2px 6px;
    border-radius: 5px;
    color: #8ef7ff;
  }

  // 图片
  :deep(img) {
    max-width: 100%;
    border-radius: 8px;
    margin: 24px auto;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 18px 60px rgba(0, 0, 0, 0.28);
    display: block;
  }

  :deep(hr) {
    border: none;
    border-top: 1px solid var(--color-hairline);
    margin: 32px 0;
  }
}

// === 响应式 ===
@media (max-width: 1080px) {
  .container {
    max-width: 960px;
  }

  .article-layout {
    display: block;
  }

  .toc-panel {
    display: none;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 0;
  }

  .article-layout {
    display: block;
  }

  .toc-panel {
    display: none;
  }

  .mobile-toc {
    display: block;
  }

  .article-card {
    border-radius: 0;
    border-left: none;
    border-right: none;
    padding: 26px 17px;
  }

  .article-body {
    font-size: 14.5px;
    line-height: 1.68;
  }
}
</style>
