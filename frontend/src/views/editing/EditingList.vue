<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { POSTS_PAGE_SIZE, usePostStore } from '../../stores/post'
import { getSectionPage } from '../../api'
import { isExternalVideoPost } from '../../utils/postLinks'
import LightRays from '../../components/effects/LightRays.vue'
import PaginationControls from '../../components/common/PaginationControls.vue'

const postStore = usePostStore()
const activeCategory = ref(null)
const currentVideoIndex = ref(0)

const defaultSectionPage = {
  "title": "Projects",
  "eyebrow": "selected projects",
  "description": "作品展示的示例栏目。用一段演示视频介绍项目，再写下它的背景、制作过程和最终成果。",
  "manifesto": "",
  "index_label": "PROJECT",
  "stat_one": {
    "value": "01",
    "label": "selected work"
  },
  "stat_two": {
    "value": "Demo",
    "label": "project showcase"
  },
  "tags": [
    "projects",
    "design",
    "experiments",
    "process",
    "showcase"
  ],
  "filters": [
    {
      "name": "All",
      "slug": null
    }
  ],
  "empty_text": "暂时没有匹配的作品",
  "filter_aria_label": "作品分类",
  "extra": {
    "panel_topline_left": "PROJECT / 01",
    "panel_topline_right": "demo showcase",
    "featured_empty_label": "NO PROJECTS",
    "featured_empty_title": "暂时没有可展示的作品",
    "featured_empty_body": "发布第一条带视频的作品后，它会出现在这里。",
    "loading_title": "正在读取作品",
    "loading_label": "loading projects",
    "craft_eyebrow": "// project notes",
    "craft_title": "Behind the Project",
    "craft_cards": [
      {
        "id": "idea",
        "title": "The Idea",
        "body": "介绍项目从何而来，以及你希望解决的问题。",
        "meta": [
          "idea",
          "context"
        ]
      },
      {
        "id": "process",
        "title": "The Process",
        "body": "记录设计、尝试和调整，补充关键的过程图片。",
        "meta": [
          "draft",
          "iteration"
        ]
      },
      {
        "id": "result",
        "title": "The Result",
        "body": "展示完成后的成果，也可以写下下一步计划。",
        "meta": [
          "demo",
          "next step"
        ]
      }
    ]
  }
}

const sectionPage = ref({ ...defaultSectionPage })
const sectionExtra = computed(() => ({ ...defaultSectionPage.extra, ...(sectionPage.value.extra || {}) }))
const filters = computed(() => sectionPage.value.filters?.length ? sectionPage.value.filters : defaultSectionPage.filters)
const tags = computed(() => sectionPage.value.tags?.length ? sectionPage.value.tags : defaultSectionPage.tags)
const videoPosts = computed(() => postStore.posts.filter(isExternalVideoPost))
const currentVideo = computed(() => videoPosts.value[currentVideoIndex.value] || videoPosts.value[0] || null)
const sidePosts = computed(() => {
  if (!currentVideo.value) return videoPosts.value.slice(0, 4)
  return videoPosts.value.filter(post => post.id !== currentVideo.value.id).slice(0, 4)
})

onMounted(async () => {
  try {
    const data = await getSectionPage('editing')
    sectionPage.value = {
      ...defaultSectionPage,
      ...data,
      extra: { ...defaultSectionPage.extra, ...(data.extra || {}) },
    }
  } catch {
    sectionPage.value = { ...defaultSectionPage }
  }
  fetchPage(1)
})

watch(videoPosts, () => {
  currentVideoIndex.value = 0
})

function filterByCategory(slug) {
  activeCategory.value = activeCategory.value === slug ? null : slug
  fetchPage(1)
}

function fetchPage(page) {
  postStore.fetchPosts({
    section: 'editing',
    category: activeCategory.value || undefined,
    page,
    page_size: POSTS_PAGE_SIZE,
  })
}

function nextVideo() {
  if (!videoPosts.value.length) return
  currentVideoIndex.value = (currentVideoIndex.value + 1) % videoPosts.value.length
}

function videoHref(post) {
  return post?.video_url || '#'
}

function categoryName(post) {
  return post.category_name || post.category?.name || post.section || 'work'
}
</script>

<template>
  <section class="frame-page">
    <LightRays
      rays-color="#f472b6"
      rays-origin="top-center"
      :rays-speed="0.8"
      :light-spread="1.82"
      :ray-length="3.8"
      :pulsating="true"
      :follow-mouse="true"
      :mouse-influence="0.14"
      :saturation="1.28"
    />
    <div class="frame-vignette"></div>
    <div class="film-lines" aria-hidden="true">
      <span></span>
      <span></span>
      <span></span>
    </div>

    <div class="frame-shell">
      <header class="showcase-hero">
        <div class="showcase-copy">
          <span class="showcase-kicker">{{ sectionPage.eyebrow }}</span>
          <h1>{{ sectionPage.title }}</h1>
          <p>{{ sectionPage.description }}</p>

          <nav class="showcase-filters" :aria-label="sectionPage.filter_aria_label">
            <button
              v-for="filter in filters"
              :key="filter.slug || 'all'"
              type="button"
              class="showcase-chip"
              :class="{ active: activeCategory === filter.slug || (!activeCategory && !filter.slug) }"
              @click="filterByCategory(filter.slug)"
            >
              {{ filter.name }}
            </button>
          </nav>
        </div>

        <aside class="showcase-panel liquid-glass">
          <div class="panel-topline">
            <span>{{ sectionExtra.panel_topline_left }}</span>
            <span>{{ sectionExtra.panel_topline_right }}</span>
          </div>
          <div class="panel-stats">
            <div>
              <strong>{{ sectionPage.stat_one.value }}</strong>
              <span>{{ sectionPage.stat_one.label }}</span>
            </div>
            <div>
              <strong>{{ sectionPage.stat_two.value }}</strong>
              <span>{{ sectionPage.stat_two.label }}</span>
            </div>
          </div>
          <div class="signal-list">
            <span v-for="tag in tags" :key="tag">{{ tag }}</span>
          </div>
        </aside>
      </header>

      <main class="showcase-layout">
        <a
          v-if="currentVideo"
          class="prime-work liquid-glass"
          :href="videoHref(currentVideo)"
          target="_blank"
          rel="noreferrer"
        >
          <div class="work-media">
            <img
              v-if="currentVideo.cover_image"
              :src="currentVideo.cover_image"
              :alt="currentVideo.title"
              loading="eager"
            />
            <div v-else class="work-fallback">
              <small>{{ categoryName(currentVideo) }}</small>
              <span>REEL</span>
            </div>
          </div>
          <div class="work-copy">
            <div class="work-meta">
              <span>{{ categoryName(currentVideo) }}</span>
              <span>{{ currentVideo.views_count || 0 }} views</span>
            </div>
            <h2>{{ currentVideo.title }}</h2>
            <p>{{ currentVideo.excerpt }}</p>
            <button
              type="button"
              class="switch-btn"
              :disabled="videoPosts.length < 2"
              aria-label="切换到下一个视频"
              @click.prevent="nextVideo"
            >
              Next video
            </button>
          </div>
        </a>

        <div v-else-if="!postStore.loading" class="prime-work empty-work liquid-glass">
          <span>{{ sectionExtra.featured_empty_label }}</span>
          <h2>{{ sectionExtra.featured_empty_title }}</h2>
          <p>{{ sectionExtra.featured_empty_body }}</p>
        </div>

        <aside class="side-works">
          <a
            v-for="(post, index) in sidePosts"
            :key="post.id"
            class="side-work liquid-glass"
            :href="videoHref(post)"
            target="_blank"
            rel="noreferrer"
          >
            <span>{{ String(index + 2).padStart(2, '0') }}</span>
            <div>
              <strong>{{ post.title }}</strong>
              <small>{{ categoryName(post) }}</small>
            </div>
          </a>
          <div v-if="!sidePosts.length && postStore.loading" class="side-work liquid-glass">
            <span>...</span>
            <div>
              <strong>{{ sectionExtra.loading_title }}</strong>
              <small>{{ sectionExtra.loading_label }}</small>
            </div>
          </div>
        </aside>
      </main>

      <PaginationControls
        :current-page="postStore.currentPage"
        :total-count="postStore.totalCount"
        :page-size="POSTS_PAGE_SIZE"
        :loading="postStore.loading"
        accent="#f472b6"
        @change="fetchPage"
      />
    </div>
  </section>
</template>

<style lang="scss" scoped>
.frame-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: #07050a;
  color: var(--color-ink);
}

:deep(.light-rays-container) {
  position: fixed;
  inset: 0;
  z-index: 0;
  opacity: 1;
  filter: brightness(1.32) saturate(1.18);
}

.frame-vignette {
  position: fixed;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  background:
    radial-gradient(circle at 58% 10%, rgba(244, 114, 182, 0.3), transparent 36%),
    linear-gradient(90deg, rgba(7, 5, 10, 0.68) 0%, rgba(7, 5, 10, 0.24) 48%, rgba(7, 5, 10, 0.62) 100%),
    linear-gradient(180deg, rgba(7, 5, 10, 0.02) 0%, rgba(7, 5, 10, 0.74) 100%);
}

.film-lines {
  position: fixed;
  inset: 120px 9% auto auto;
  width: min(42vw, 520px);
  aspect-ratio: 16 / 10;
  z-index: 1;
  pointer-events: none;
  opacity: 0.38;

  span {
    position: absolute;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(244, 114, 182, 0.5), transparent);

    &:nth-child(1) { top: 18%; }
    &:nth-child(2) { top: 50%; }
    &:nth-child(3) { top: 82%; }
  }
}

.frame-shell {
  width: min(1180px, calc(100% - 48px));
  margin: 0 auto;
  padding: 116px 0 76px;
  position: relative;
  z-index: 2;
}

.showcase-hero {
  min-height: 54vh;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(300px, 390px);
  align-items: center;
  gap: 34px;
}

.showcase-copy {
  max-width: 780px;

  h1 {
    margin: 18px 0;
    max-width: 100%;
    font-family: var(--font-heading);
    font-size: clamp(58px, 10vw, 132px);
    line-height: 0.82;
    color: #fff2fa;
    text-shadow: 0 0 46px rgba(244, 114, 182, 0.24);
    overflow-wrap: anywhere;
  }

  p {
    max-width: 650px;
    color: rgba(249, 235, 245, 0.73);
    font-size: clamp(15px, 1.6vw, 18px);
    line-height: 1.8;
  }
}

.showcase-kicker {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 5px 12px;
  border: 1px solid rgba(244, 114, 182, 0.32);
  border-radius: 999px;
  color: #ff9bd0;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  background: rgba(20, 7, 16, 0.38);
}

.showcase-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 28px;
}

.showcase-chip,
.switch-btn {
  min-height: 40px;
  padding: 0 15px;
  border: 1px solid rgba(255, 210, 236, 0.18);
  border-radius: 999px;
  color: rgba(255, 236, 247, 0.76);
  background: rgba(29, 10, 22, 0.42);
  cursor: pointer;
  transition: border-color 0.25s ease, color 0.25s ease, background 0.25s ease, transform 0.25s ease;

  &.active,
  &:hover:not(:disabled) {
    color: #180612;
    border-color: rgba(244, 114, 182, 0.86);
    background: #f472b6;
    transform: translateY(-1px);
  }

  &:disabled {
    cursor: not-allowed;
    opacity: 0.42;
  }
}

.liquid-glass {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 232, 246, 0.09);
  border-radius: 8px;
  background: rgba(20, 8, 18, 0.32);
  backdrop-filter: blur(10px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 14px 40px rgba(0, 0, 0, 0.24);
}

.showcase-panel {
  padding: 24px;
}

.panel-topline,
.work-meta {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  color: rgba(255, 220, 241, 0.6);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.panel-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin: 44px 0 24px;

  div {
    min-height: 118px;
    padding: 18px;
    border: 1px solid rgba(244, 114, 182, 0.17);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.04);
  }

  strong {
    display: block;
    color: #fff3fa;
    font-family: var(--font-heading);
    font-size: 40px;
    line-height: 1;
  }

  span {
    display: block;
    margin-top: 10px;
    color: rgba(255, 232, 246, 0.6);
    font-size: 12px;
  }
}

.signal-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  span {
    padding: 6px 10px;
    border-radius: 999px;
    color: rgba(255, 232, 246, 0.76);
    background: rgba(255, 255, 255, 0.06);
    font-size: 12px;
  }
}

.showcase-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 18px;
  align-items: stretch;
}

.prime-work {
  min-height: 390px;
  display: grid;
  grid-template-columns: minmax(280px, 0.95fr) minmax(0, 1fr);
  color: inherit;
  text-decoration: none;
}

.work-media {
  min-height: 100%;
  background:
    linear-gradient(135deg, rgba(244, 114, 182, 0.2), transparent 44%),
    rgba(255, 255, 255, 0.04);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
}

.work-fallback {
  height: 100%;
  min-height: 390px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: rgba(255, 155, 208, 0.34);
  font-family: var(--font-heading);
  background:
    linear-gradient(90deg, rgba(255, 155, 208, 0.07) 1px, transparent 1px),
    linear-gradient(180deg, rgba(255, 155, 208, 0.06) 1px, transparent 1px),
    radial-gradient(circle at 50% 42%, rgba(255, 155, 208, 0.18), transparent 36%);
  background-size: 34px 34px, 34px 34px, auto;

  small {
    color: rgba(255, 210, 236, 0.68);
    font-family: var(--font-mono);
    font-size: 11px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
  }

  span {
    font-size: clamp(54px, 8vw, 112px);
    line-height: 0.86;
  }
}

.work-copy {
  padding: 28px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;

  h2 {
    margin: 62px 0 14px;
    color: #fff3fa;
    font-family: var(--font-heading);
    font-size: clamp(34px, 4.6vw, 66px);
    line-height: 0.94;
  }

  p {
    color: rgba(255, 232, 246, 0.7);
    line-height: 1.65;
  }
}

.switch-btn {
  align-self: flex-start;
  margin-top: 22px;
}

.empty-work {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 32px;

  > span {
    color: #ff9bd0;
    letter-spacing: 0.16em;
    font-size: 12px;
  }
}

.side-works {
  display: grid;
  gap: 12px;
}

.side-work {
  min-height: 80px;
  padding: 16px;
  display: grid;
  grid-template-columns: 42px 1fr;
  gap: 14px;
  align-items: center;
  color: inherit;
  text-decoration: none;

  > span {
    color: #f472b6;
    font-family: var(--font-heading);
    font-size: 30px;
  }

  strong {
    display: block;
    color: rgba(255, 242, 250, 0.92);
    line-height: 1.25;
  }

  small {
    display: block;
    margin-top: 8px;
    color: rgba(255, 232, 246, 0.54);
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
}

@media (max-width: 900px) {
  .frame-shell {
    width: min(100% - 32px, 720px);
    padding-top: 96px;
  }

  .showcase-hero,
  .showcase-layout,
  .prime-work {
    grid-template-columns: 1fr;
  }

  .showcase-hero {
    min-height: auto;
  }

  .showcase-panel {
    order: -1;
  }

  .work-media,
  .work-fallback {
    min-height: 230px;
  }
}

@media (max-width: 560px) {
  .showcase-copy h1 {
    font-size: clamp(42px, 17vw, 68px);
    line-height: 0.86;
  }

  .showcase-filters {
    gap: 8px;
  }

  .showcase-chip {
    min-height: 38px;
    padding: 0 12px;
  }

  .panel-stats {
    grid-template-columns: 1fr;
    margin-top: 28px;
  }

  .work-copy {
    padding: 22px;

    h2 {
      margin-top: 30px;
    }
  }
}
</style>
