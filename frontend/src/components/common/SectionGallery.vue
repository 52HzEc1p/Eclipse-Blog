<script setup>
import { computed } from 'vue'
import PaginationControls from './PaginationControls.vue'
import { isExternalVideoPost } from '../../utils/postLinks'

const props = defineProps({
  sectionPath: { type: String, required: true },
  accent: { type: String, required: true },
  accentSoft: { type: String, required: true },
  title: { type: String, required: true },
  eyebrow: { type: String, required: true },
  description: { type: String, required: true },
  manifesto: { type: String, required: true },
  indexLabel: { type: String, required: true },
  statOne: { type: Object, required: true },
  statTwo: { type: Object, required: true },
  tags: { type: Array, default: () => [] },
  filters: { type: Array, default: () => [] },
  filterAriaLabel: { type: String, default: '内容分类' },
  activeCategory: { type: String, default: null },
  posts: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  currentPage: { type: Number, default: 1 },
  totalCount: { type: Number, default: 0 },
  pageSize: { type: Number, default: 8 },
  emptyText: { type: String, default: '暂无内容' },
})

const emit = defineEmits(['filter', 'change-page'])

const featuredPost = computed(() => props.posts.find(p => p.is_featured) || props.posts[0] || null)
const storyPosts = computed(() => {
  if (!featuredPost.value) return props.posts
  return props.posts.filter(p => p.id !== featuredPost.value.id)
})

function postTo(post) {
  return `${props.sectionPath}/${post.slug}`
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
  return { to: postTo(post) }
}

function categoryName(post) {
  return post.category_name || post.category?.name || post.section || 'note'
}

function postTypeLabel(type) {
  const labels = { article: 'Essay', gallery: 'Gallery', video: 'Video' }
  return labels[type] || 'Essay'
}
</script>

<template>
  <section
    class="gallery-page"
    :style="{ '--accent': accent, '--accent-soft': accentSoft }"
  >
    <slot name="background" />

    <div class="gallery-shell">
      <header class="gallery-hero">
        <div class="hero-copy">
          <span class="eyebrow">{{ eyebrow }}</span>
          <h1>{{ title }}</h1>
          <p class="description">{{ description }}</p>
        </div>

        <aside class="hero-panel liquid-glass">
          <p>{{ manifesto }}</p>
          <div class="hero-stats">
            <div>
              <strong>{{ statOne.value }}</strong>
              <span>{{ statOne.label }}</span>
            </div>
            <div>
              <strong>{{ statTwo.value }}</strong>
              <span>{{ statTwo.label }}</span>
            </div>
          </div>
        </aside>
      </header>

      <nav class="filter-strip" v-if="filters.length" :aria-label="filterAriaLabel">
        <button
          v-for="filter in filters"
          :key="filter.slug || 'all'"
          type="button"
          class="filter-chip"
          :class="{ active: activeCategory === filter.slug || (!activeCategory && !filter.slug) }"
          @click="emit('filter', filter.slug)"
        >
          {{ filter.name }}
        </button>
      </nav>

      <component
        :is="linkComponent(featuredPost)"
        v-if="featuredPost"
        class="featured-story liquid-glass"
        v-bind="linkAttrs(featuredPost)"
      >
        <div class="story-media featured-media">
          <img
            v-if="featuredPost.cover_image"
            :src="featuredPost.cover_image"
            :alt="featuredPost.title"
            loading="eager"
          />
          <div v-else class="media-fallback" :class="sectionPath.slice(1)">
            <small>{{ categoryName(featuredPost) }}</small>
            <span>{{ indexLabel }}</span>
          </div>
          <div class="media-overlay">
            <span class="plus-mark">+</span>
          </div>
          <span class="corner tl"></span>
          <span class="corner tr"></span>
          <span class="corner bl"></span>
          <span class="corner br"></span>
        </div>

        <div class="featured-copy">
          <div class="story-meta">
            <span>{{ indexLabel }}</span>
            <span>{{ postTypeLabel(featuredPost.post_type) }}</span>
          </div>
          <h2>{{ featuredPost.title }}</h2>
          <p>{{ featuredPost.excerpt }}</p>
          <div class="story-footer">
            <span>{{ categoryName(featuredPost) }}</span>
            <span>{{ featuredPost.views_count || 0 }} reads</span>
          </div>
        </div>
      </component>

      <div v-if="storyPosts.length" class="story-grid">
        <component
          :is="linkComponent(post)"
          v-for="(post, index) in storyPosts"
          :key="post.id"
          class="story-card liquid-glass"
          :class="{ 'no-cover': !post.cover_image }"
          v-bind="linkAttrs(post)"
        >
          <div class="story-media" v-if="post.cover_image">
            <img
              :src="post.cover_image"
              :alt="post.title"
              loading="lazy"
            />
            <div class="media-overlay">
              <span class="plus-mark">+</span>
            </div>
          </div>
          <div class="card-copy">
            <div class="story-meta">
              <span class="meta-cat">{{ categoryName(post) }}</span>
              <span class="meta-no">{{ String(index + 2).padStart(2, '0') }}</span>
            </div>
            <h3>{{ post.title }}</h3>
            <p>{{ post.excerpt }}</p>
            <div class="story-footer card-footer">
              <span>{{ postTypeLabel(post.post_type) }}</span>
              <span>{{ post.views_count || 0 }} reads</span>
            </div>
          </div>
        </component>
      </div>

      <div v-if="!posts.length && !loading" class="empty-state liquid-glass">
        {{ emptyText }}
      </div>

      <PaginationControls
        :current-page="currentPage"
        :total-count="totalCount"
        :page-size="pageSize"
        :loading="loading"
        :accent="accent"
        @change="page => emit('change-page', page)"
      />
    </div>
  </section>
</template>

<style lang="scss" scoped>
.gallery-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 8% 18%, color-mix(in srgb, var(--accent) 18%, transparent), transparent 28%),
    radial-gradient(circle at 90% 8%, rgba(255, 255, 255, 0.05), transparent 24%),
    linear-gradient(180deg, #08080d 0%, #0a0a0f 48%, #050508 100%);
  color: var(--color-ink);
}

.gallery-shell {
  width: min(1180px, calc(100% - 48px));
  margin: 0 auto;
  padding: 116px 0 72px;
  position: relative;
  z-index: 2;
}

.gallery-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(300px, 0.72fr);
  align-items: end;
  gap: 28px;
  margin-bottom: 22px;
}

.hero-copy {
  max-width: 760px;

  h1 {
    margin-top: 14px;
    font-family: var(--font-heading);
    font-size: clamp(52px, 9vw, 116px);
    line-height: 0.82;
    letter-spacing: 0;
    font-weight: 700;
    color: #f4f1eb;
    text-wrap: balance;
  }
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 4px 12px;
  border: 1px solid color-mix(in srgb, var(--accent) 42%, transparent);
  border-radius: 999px;
  color: color-mix(in srgb, var(--accent) 86%, white);
  background: rgba(255, 255, 255, 0.04);
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.description {
  max-width: 590px;
  margin-top: 22px;
  color: rgba(232, 230, 227, 0.7);
  font-size: 16px;
  line-height: 1.7;
}

.hero-panel {
  padding: 24px;
  min-height: 214px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  p {
    color: rgba(232, 230, 227, 0.76);
    line-height: 1.72;
    font-size: 14px;
  }
}

.hero-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 24px;

  div {
    padding-top: 14px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
  }

  strong {
    display: block;
    font-family: var(--font-heading);
    font-size: 30px;
    line-height: 1;
    color: var(--accent);
  }

  span {
    display: block;
    margin-top: 6px;
    color: rgba(232, 230, 227, 0.54);
    font-size: 12px;
  }
}

.filter-strip {
  display: flex;
  align-items: center;
  gap: 10px;
  overflow-x: auto;
  scrollbar-width: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.filter-strip {
  margin-bottom: 30px;
  padding: 6px;
  width: fit-content;
  max-width: 100%;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.07);
  backdrop-filter: blur(16px);
}

.filter-chip {
  flex: 0 0 auto;
  min-height: 34px;
  padding: 6px 14px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: rgba(232, 230, 227, 0.62);
  font: 600 12px/1 var(--font-body);
  cursor: pointer;
  transition: background 0.22s ease, color 0.22s ease, transform 0.22s ease;

  &:hover {
    color: #fff;
    transform: translateY(-1px);
  }

  &.active {
    color: #060609;
    background: var(--accent);
  }
}

.liquid-glass {
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.07);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.06),
    0 12px 36px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(8px);
  position: relative;
  overflow: hidden;
}

.liquid-glass::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(180deg, rgba(255,255,255,0.2), rgba(255,255,255,0.03) 38%, rgba(255,255,255,0.04) 68%, rgba(255,255,255,0.12));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.featured-story {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(320px, 0.82fr);
  min-height: 480px;
  color: inherit;
  text-decoration: none;
  margin-bottom: 22px;
  transition: transform 0.28s ease, border-color 0.28s ease;

  &:hover {
    transform: translateY(-4px);
    border-color: color-mix(in srgb, var(--accent) 42%, transparent);
  }
}

.story-media {
  position: relative;
  min-height: 230px;
  overflow: hidden;
  background:
    radial-gradient(circle at 30% 18%, var(--accent-soft), transparent 34%),
    linear-gradient(145deg, #151521, #07070b);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.55s cubic-bezier(0.33, 1, 0.68, 1), filter 0.55s ease;
  }
}

.featured-media {
  min-height: 480px;
}

.media-fallback {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background:
    linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px),
    linear-gradient(180deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    radial-gradient(circle at 50% 42%, color-mix(in srgb, var(--accent) 22%, transparent), transparent 36%);
  background-size: 34px 34px, 34px 34px, auto;

  small {
    font-family: var(--font-mono);
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: color-mix(in srgb, var(--accent) 80%, white);
    opacity: 0.72;
  }

  span {
    font-family: var(--font-mono);
    font-size: clamp(18px, 2.2vw, 28px);
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: color-mix(in srgb, var(--accent) 60%, white);
    opacity: 0.35;
  }
}

.media-overlay {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba(0, 0, 0, 0.26);
  opacity: 0;
  transition: opacity 0.35s ease;
}

.plus-mark {
  width: 64px;
  height: 64px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  color: #fff;
  font-size: 34px;
  font-weight: 300;
  transform: scale(0.72);
  transition: transform 0.3s ease;
  backdrop-filter: blur(8px);
}

.corner {
  position: absolute;
  width: 14px;
  height: 14px;
  border-color: rgba(255, 255, 255, 0.72);
  border-style: solid;
  border-width: 0;
  opacity: 0.72;

  &.tl { top: 16px; left: 16px; border-top-width: 1px; border-left-width: 1px; }
  &.tr { top: 16px; right: 16px; border-top-width: 1px; border-right-width: 1px; }
  &.bl { bottom: 16px; left: 16px; border-bottom-width: 1px; border-left-width: 1px; }
  &.br { bottom: 16px; right: 16px; border-bottom-width: 1px; border-right-width: 1px; }
}

.featured-copy,
.card-copy {
  position: relative;
  z-index: 1;
}

.featured-copy {
  padding: clamp(28px, 5vw, 58px);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;

  h2 {
    margin-top: 26px;
    font-family: var(--font-heading);
    font-size: clamp(32px, 4.8vw, 58px);
    line-height: 0.96;
    letter-spacing: 0;
    color: #f7f4ef;
    text-wrap: balance;
  }

  p {
    margin-top: 20px;
    max-width: 46ch;
    color: rgba(232, 230, 227, 0.68);
    line-height: 1.68;
  }
}

.story-meta,
.story-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: rgba(232, 230, 227, 0.52);
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.story-footer {
  margin-top: 36px;
  padding-top: 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.story-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.story-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  color: inherit;
  text-decoration: none;
  transition: transform 0.28s ease, border-color 0.28s ease;

  &.no-cover {
    border-top: 1px solid color-mix(in srgb, var(--accent) 35%, transparent);
  }

  &:hover {
    transform: translateY(-4px);
    border-color: color-mix(in srgb, var(--accent) 38%, transparent);
  }

  .story-media {
    aspect-ratio: 16 / 10;
    min-height: 0;
  }
}

.story-card:hover,
.featured-story:hover {
  .story-media img {
    transform: scale(1.08);
    filter: saturate(1.08);
  }

  .media-overlay {
    opacity: 1;
  }

  .plus-mark {
    transform: scale(1);
  }
}

.card-copy {
  padding: 22px;
  display: flex;
  flex-direction: column;
  flex: 1;

  h3 {
    margin-top: 14px;
    font-family: var(--font-heading);
    font-size: 21px;
    line-height: 1.18;
    letter-spacing: 0;
    color: #f5f2ed;
    text-wrap: balance;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  p {
    margin-top: 12px;
    color: rgba(232, 230, 227, 0.58);
    font-size: 14px;
    line-height: 1.62;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}

.empty-state {
  padding: 42px 24px;
  color: rgba(232, 230, 227, 0.6);
  text-align: center;
}

.meta-cat {
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--accent) 40%, transparent);
  color: color-mix(in srgb, var(--accent) 85%, white);
}

.meta-no {
  color: color-mix(in srgb, var(--accent) 70%, white);
  opacity: 0.65;
}

.card-footer {
  margin-top: auto;
  padding-top: 14px;
}

@media (max-width: 980px) {
  .gallery-hero,
  .featured-story {
    grid-template-columns: 1fr;
  }

  .featured-media {
    min-height: 340px;
  }

  .story-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 680px) {
  .gallery-shell {
    width: min(100% - 28px, 1180px);
    padding-top: 96px;
  }

  .hero-copy h1 {
    font-size: clamp(44px, 16vw, 76px);
  }

  .hero-panel {
    min-height: 0;
  }

  .filter-strip {
    width: 100%;
  }

  .featured-media {
    min-height: 260px;
  }

  .story-grid {
    grid-template-columns: 1fr;
  }
}
</style>
