<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { POSTS_PAGE_SIZE, usePostStore } from '../../stores/post'
import { getSectionPage } from '../../api'
import { isExternalVideoPost } from '../../utils/postLinks'
import PaginationControls from '../../components/common/PaginationControls.vue'
import { site } from '../../config/site'

const postStore = usePostStore()
const activeCategory = ref(null)
const currentVideoIndex = ref(0)

const wallpaperSrc = site.gamesVideo

const defaultSectionPage = {
  "title": "Gallery",
  "eyebrow": "visual collection",
  "description": "影像与灵感的示例栏目。用短片、动态画面和简短说明，整理想要保存的片段。",
  "manifesto": "",
  "index_label": "GALLERY",
  "stat_one": {
    "value": "",
    "label": ""
  },
  "stat_two": {
    "value": "",
    "label": ""
  },
  "tags": [
    "visuals",
    "moments",
    "motion",
    "inspiration",
    "collection"
  ],
  "filters": [
    {
      "name": "All",
      "slug": null
    }
  ],
  "empty_text": "暂时没有匹配的影像",
  "filter_aria_label": "影像分类",
  "extra": {
    "background_label": "DEMO BACKGROUND",
    "voice_label": "COLLECTION NOTES",
    "voice_body": "为每个片段写一段简短说明：拍摄背景、创作想法，或收藏它的原因。",
    "featured_empty_label": "NO MEDIA",
    "featured_empty_title": "暂时没有可展示的影像",
    "featured_empty_body": "发布第一条带视频的内容后，它会出现在这里。",
    "loadout_label": "TOPICS",
    "run_log_label": "COLLECTION",
    "loading_text": "正在读取影像...",
    "no_more_text": "暂无更多影像。",
    "timeline": [
      {
        "year": "01",
        "role": "First Collection",
        "studio": "示例合集"
      },
      {
        "year": "02",
        "role": "Work in Progress",
        "studio": "创作片段"
      },
      {
        "year": "03",
        "role": "Small Moments",
        "studio": "日常灵感"
      }
    ]
  }
}

const sectionPage = ref({ ...defaultSectionPage })
const sectionExtra = computed(() => ({
  ...defaultSectionPage.extra,
  ...(sectionPage.value.extra || {}),
  featured_empty_label: defaultSectionPage.extra.featured_empty_label,
  featured_empty_title: defaultSectionPage.extra.featured_empty_title,
  featured_empty_body: defaultSectionPage.extra.featured_empty_body,
}))
const filters = computed(() => sectionPage.value.filters?.length ? sectionPage.value.filters : defaultSectionPage.filters)
const tools = computed(() => sectionPage.value.tags?.length ? sectionPage.value.tags : defaultSectionPage.tags)
const timeline = computed(() => sectionExtra.value.timeline || defaultSectionPage.extra.timeline)
const videoPosts = computed(() => postStore.posts.filter(isExternalVideoPost))
const currentVideo = computed(() => videoPosts.value[currentVideoIndex.value] || videoPosts.value[0] || null)
const compactPosts = computed(() => {
  if (!currentVideo.value) return postStore.posts.slice(0, 4)
  return postStore.posts.filter(post => post.id !== currentVideo.value.id).slice(0, 4)
})

onMounted(async () => {
  try {
    const data = await getSectionPage('games')
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
    section: 'games',
    category: activeCategory.value || undefined,
    page,
    page_size: POSTS_PAGE_SIZE,
  })
}

function nextVideo() {
  if (!videoPosts.value.length) return
  currentVideoIndex.value = (currentVideoIndex.value + 1) % videoPosts.value.length
}

function categoryName(post) {
  return post.category_name || post.category?.name || post.section || 'note'
}

function linkComponent(post) {
  return isExternalVideoPost(post) ? 'a' : 'router-link'
}

function linkAttrs(post) {
  if (isExternalVideoPost(post)) {
    return {
      href: post.video_url,
      target: '_blank',
      rel: 'noreferrer',
    }
  }
  return { to: `/games/${post.slug}` }
}
</script>

<template>
  <section class="playfield-page">
    <video
      class="playfield-video"
      :src="wallpaperSrc"
      autoplay
      muted
      loop
      playsinline
      preload="auto"
    ></video>
    <div class="playfield-shade"></div>

    <div class="playfield-shell">
      <header class="playfield-header">
        <div class="playfield-intro">
          <h1>{{ sectionPage.title }}</h1>
          <p>{{ sectionPage.description }}</p>
        </div>

        <nav class="playfield-filters" :aria-label="sectionPage.filter_aria_label">
          <button
            v-for="filter in filters"
            :key="filter.slug || 'all'"
            type="button"
            class="play-chip"
            :class="{ active: activeCategory === filter.slug || (!activeCategory && !filter.slug) }"
            @click="filterByCategory(filter.slug)"
          >
            {{ filter.name }}
          </button>
        </nav>
      </header>

      <main class="play-grid">
        <section class="play-card background-card">
          <video
            class="card-video"
            :src="wallpaperSrc"
            autoplay
            muted
            loop
            playsinline
          ></video>
          <div class="card-scrim"></div>

          <div class="stage-head">
            <div class="label-row">
              <span></span>
              <strong>{{ sectionExtra.background_label }}</strong>
              <span></span>
            </div>
            <button
              type="button"
              class="switch-video"
              :disabled="videoPosts.length < 2"
              aria-label="切换到下一个影像"
              @click="nextVideo"
            >
              Next video
            </button>
          </div>

          <a
            v-if="currentVideo"
            class="stage-video"
            :href="currentVideo.video_url"
            target="_blank"
            rel="noreferrer"
          >
            <img
              v-if="currentVideo.cover_image"
              :src="currentVideo.cover_image"
              :alt="currentVideo.title"
              loading="eager"
            />
            <div v-else class="feature-fallback" aria-hidden="true">
              <span>{{ categoryName(currentVideo) }}</span>
              <strong>PLAY</strong>
            </div>
            <div class="stage-copy">
              <span>{{ categoryName(currentVideo) }}</span>
              <h2>{{ currentVideo.title }}</h2>
              <p>{{ currentVideo.excerpt }}</p>
            </div>
          </a>

          <article v-else-if="!postStore.loading" class="stage-video empty-stage">
            <div class="stage-copy">
              <span>{{ sectionExtra.featured_empty_label }}</span>
              <h2>{{ sectionExtra.featured_empty_title }}</h2>
              <p>{{ sectionExtra.featured_empty_body }}</p>
            </div>
          </article>

          <div class="timeline">
            <div v-for="item in timeline" :key="item.year" class="timeline-row">
              <span>{{ item.year }}</span>
              <i></i>
              <strong>{{ item.role }}</strong>
              <small>{{ item.studio }}</small>
            </div>
          </div>
        </section>

        <section class="play-stack">
          <article class="play-card loadout-card">
            <div class="label-row">
              <span></span>
              <strong>{{ sectionExtra.loadout_label }}</strong>
              <span></span>
            </div>
            <div class="marquee">
              <div class="marquee-track left">
                <span v-for="(tool, index) in [...tools, ...tools]" :key="`a-${tool}-${index}`">{{ tool }}</span>
              </div>
            </div>
            <div class="marquee">
              <div class="marquee-track right">
                <span v-for="(tool, index) in [...tools].reverse().concat(tools)" :key="`b-${tool}-${index}`">{{ tool }}</span>
              </div>
            </div>
          </article>

          <article class="play-card notes-card noise-card">
            <div class="label-row align-left">
              <span></span>
              <strong>{{ sectionExtra.run_log_label }}</strong>
            </div>
            <component
              :is="linkComponent(post)"
              v-for="post in compactPosts"
              :key="post.id"
              class="note-link"
              v-bind="linkAttrs(post)"
            >
              <span>{{ categoryName(post) }}</span>
              <strong>{{ post.title }}</strong>
            </component>
            <p v-if="!compactPosts.length && postStore.loading" class="muted">{{ sectionExtra.loading_text }}</p>
            <p v-else-if="!compactPosts.length" class="muted">{{ sectionExtra.no_more_text }}</p>
          </article>
        </section>
      </main>

      <PaginationControls
        :current-page="postStore.currentPage"
        :total-count="postStore.totalCount"
        :page-size="POSTS_PAGE_SIZE"
        :loading="postStore.loading"
        accent="#fcd34d"
        @change="fetchPage"
      />
    </div>
  </section>
</template>

<style lang="scss" scoped>
.playfield-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: #060507;
  color: #f6f1ea;
}

.playfield-video,
.playfield-shade {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
}

.playfield-video {
  object-fit: cover;
  z-index: 0;
  filter: brightness(1.55) saturate(1.3) contrast(1.02);
}

.playfield-shade {
  z-index: 1;
  pointer-events: none;
  background:
    radial-gradient(circle at 50% 20%, rgba(255, 210, 120, 0.18), transparent 34%),
    linear-gradient(90deg, rgba(3, 3, 5, 0.28) 0%, rgba(3, 3, 5, 0.04) 50%, rgba(3, 3, 5, 0.28) 100%),
    linear-gradient(180deg, rgba(6, 5, 7, 0) 0%, rgba(6, 5, 7, 0.16) 68%, rgba(6, 5, 7, 0.54) 100%);
}

.playfield-shell {
  width: min(1260px, calc(100% - 48px));
  min-height: 100vh;
  margin: 0 auto;
  padding: 112px 0 48px;
  position: relative;
  z-index: 2;
}

.playfield-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 28px;
  margin-bottom: 24px;
}

.playfield-intro {
  max-width: 720px;

  h1 {
    color: #fff8ef;
    font-family: var(--font-heading);
    font-size: clamp(48px, 7vw, 96px);
    line-height: 0.9;
  }

  p {
    max-width: 680px;
    margin-top: 14px;
    color: rgba(246, 241, 234, 0.66);
    font-size: 15px;
    line-height: 1.8;
  }
}

.playfield-filters {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
  max-width: 460px;
}

.play-chip,
.switch-video {
  min-height: 38px;
  padding: 0 13px;
  border: 1px solid rgba(255, 241, 214, 0.18);
  border-radius: 999px;
  color: rgba(255, 248, 235, 0.72);
  background: rgba(255, 255, 255, 0.045);
  backdrop-filter: blur(10px);
  cursor: pointer;
  transition: background 0.25s ease, border-color 0.25s ease, color 0.25s ease, transform 0.25s ease;

  &.active,
  &:hover:not(:disabled) {
    color: #190f06;
    border-color: rgba(252, 211, 77, 0.78);
    background: #fcd34d;
    transform: translateY(-1px);
  }

  &:disabled {
    cursor: not-allowed;
    opacity: 0.42;
  }
}

.play-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.75fr) minmax(320px, 0.82fr);
  gap: 18px;
  min-height: 650px;
}

.play-stack {
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 18px;
}

.play-card {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 245, 228, 0.13);
  border-radius: 8px;
  background: rgba(13, 12, 12, 0.34);
  backdrop-filter: blur(14px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.09), 0 24px 58px rgba(0, 0, 0, 0.34);
}

.background-card {
  min-height: 650px;
  padding: 22px;
  display: grid;
  grid-template-rows: auto 1fr auto;
  gap: 18px;
}

.card-video,
.card-scrim {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.card-video {
  object-fit: cover;
  z-index: 0;
  filter: brightness(1.26) saturate(1.16);
}

.card-scrim {
  z-index: 1;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.08), rgba(0, 0, 0, 0.46));
}

.stage-head {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.label-row {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: rgba(255, 248, 235, 0.72);

  strong {
    font-size: 11px;
    letter-spacing: 0.22em;
    font-weight: 500;
    text-transform: uppercase;
  }

  span {
    width: 12px;
    height: 12px;
    display: inline-block;
    border: 1px solid currentColor;
    transform: rotate(45deg);
  }

  &.align-left {
    justify-content: flex-start;
  }
}

.stage-video {
  position: relative;
  z-index: 2;
  min-height: 380px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
  color: inherit;
  text-decoration: none;
  border: 1px solid rgba(255, 245, 228, 0.16);
  border-radius: 8px;
  background: rgba(6, 9, 18, 0.38);

  img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  &::after {
    content: '';
    position: absolute;
    inset: 0;
    background:
      linear-gradient(180deg, rgba(0, 0, 0, 0.02), rgba(0, 0, 0, 0.78)),
      radial-gradient(circle at 70% 18%, rgba(252, 211, 77, 0.16), transparent 32%);
  }
}

.feature-fallback {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background:
    linear-gradient(90deg, rgba(252, 211, 77, 0.08) 1px, transparent 1px),
    linear-gradient(180deg, rgba(252, 211, 77, 0.07) 1px, transparent 1px),
    radial-gradient(circle at 50% 42%, rgba(252, 211, 77, 0.18), transparent 36%);
  background-size: 36px 36px, 36px 36px, auto;

  span {
    color: rgba(252, 211, 77, 0.72);
    font-family: var(--font-mono);
    font-size: 11px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
  }

  strong {
    color: rgba(255, 248, 235, 0.2);
    font-family: var(--font-heading);
    font-size: clamp(66px, 10vw, 128px);
    line-height: 0.86;
  }
}

.empty-stage {
  background:
    linear-gradient(145deg, rgba(252, 211, 77, 0.13), transparent 46%),
    rgba(13, 12, 12, 0.56);
}

.stage-copy {
  position: relative;
  z-index: 2;
  padding: 24px;

  span {
    color: #fcd34d;
    font-size: 12px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }

  h2 {
    margin-top: 12px;
    color: #fff8ef;
    font-family: var(--font-heading);
    font-size: clamp(34px, 4vw, 60px);
    line-height: 0.96;
  }

  p {
    max-width: 58ch;
    margin-top: 12px;
    color: rgba(255, 248, 235, 0.7);
    line-height: 1.62;
  }
}

.timeline {
  position: relative;
  z-index: 2;
  display: grid;
  gap: 16px;
}

.timeline-row {
  display: grid;
  grid-template-columns: 84px 16px 1fr auto;
  gap: 12px;
  align-items: center;
  color: rgba(255, 248, 235, 0.82);

  span,
  small {
    color: rgba(255, 248, 235, 0.64);
    font-size: 12px;
  }

  i {
    width: 9px;
    height: 9px;
    border: 1px solid rgba(252, 211, 77, 0.8);
    transform: rotate(45deg);
  }
}

.notes-card,
.loadout-card {
  padding: 22px;
}

.noise-card::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.2;
  mix-blend-mode: soft-light;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");
}

.loadout-card {
  min-height: 250px;
}

.marquee {
  margin-top: 28px;
  overflow: hidden;
  mask-image: linear-gradient(to right, transparent, black 9%, black 91%, transparent);
}

.marquee-track {
  display: flex;
  width: max-content;
  gap: 10px;

  &.left {
    animation: marquee-left 22s linear infinite;
  }

  &.right {
    animation: marquee-right 26s linear infinite;
  }

  span {
    min-width: 118px;
    height: 54px;
    display: grid;
    place-items: center;
    border: 1px solid rgba(255, 245, 228, 0.14);
    border-radius: 8px;
    color: rgba(255, 248, 235, 0.72);
    background: rgba(255, 255, 255, 0.05);
    white-space: nowrap;
  }
}

.notes-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(55, 47, 38, 0.54);
}

.note-link {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 8px;
  padding: 15px 0;
  color: inherit;
  text-decoration: none;
  border-bottom: 1px solid rgba(255, 245, 228, 0.12);

  span {
    color: rgba(252, 211, 77, 0.86);
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }

  strong {
    color: rgba(255, 248, 235, 0.9);
    line-height: 1.3;
  }
}

.muted {
  position: relative;
  z-index: 1;
  color: rgba(255, 248, 235, 0.62);
}

@keyframes marquee-left {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}

@keyframes marquee-right {
  from { transform: translateX(-50%); }
  to { transform: translateX(0); }
}

@media (max-width: 1040px) {
  .playfield-header,
  .play-grid {
    grid-template-columns: 1fr;
  }

  .playfield-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .playfield-filters {
    justify-content: flex-start;
    max-width: none;
  }

  .background-card,
  .stage-video {
    min-height: 430px;
  }
}

@media (max-width: 640px) {
  .playfield-shell {
    width: min(100% - 32px, 720px);
    padding-top: 96px;
  }

  .play-stack {
    grid-template-rows: auto;
  }

  .stage-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .timeline-row {
    grid-template-columns: 70px 14px 1fr;

    small {
      grid-column: 3;
    }
  }

  .play-chip {
    min-height: 36px;
    padding: 0 11px;
  }
}
</style>
