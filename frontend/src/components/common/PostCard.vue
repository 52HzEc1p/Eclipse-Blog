<script setup>
defineProps({
  post: { type: Object, required: true },
  to: { type: String, required: true },
  categoryIcon: { type: String, default: '' },
})
</script>

<template>
  <router-link :to="to" class="post-card">
    <div class="card-cover" v-if="post.cover_image">
      <img :src="post.cover_image" :alt="post.title" />
      <div class="type-overlay video-overlay" v-if="post.post_type === 'video'">
        <svg class="play-icon" viewBox="0 0 48 48" fill="none">
          <circle cx="24" cy="24" r="23" stroke="currentColor" stroke-width="2" fill="rgba(0,0,0,0.4)" />
          <polygon points="19,15 35,24 19,33" fill="currentColor" />
        </svg>
      </div>
      <div class="type-overlay gallery-overlay" v-else-if="post.post_type === 'gallery'">
        <svg class="stack-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="14" height="14" rx="2" />
          <rect x="7" y="7" width="14" height="14" rx="2" />
        </svg>
      </div>
    </div>
    <div class="card-body">
      <div class="card-meta">
        <span class="category-icon" v-if="categoryIcon" v-html="categoryIcon"></span>
        <span class="section-tag" :class="post.section">{{ post.section }}</span>
        <span class="post-type" v-if="post.post_type !== 'article'">{{ post.post_type }}</span>
      </div>
      <h3 class="card-title">{{ post.title }}</h3>
      <p class="card-excerpt">{{ post.excerpt }}</p>
      <div class="card-footer">
        <div class="tags">
          <span v-for="tag in post.tags" :key="tag.id" class="tag" :style="{ borderColor: tag.color, color: tag.color }">
            {{ tag.name }}
          </span>
        </div>
        <span class="views">{{ post.views_count }} 阅读</span>
      </div>
    </div>
  </router-link>
</template>

<style lang="scss" scoped>
.post-card {
  display: block;
  background: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-md);
  overflow: hidden;
  text-decoration: none;
  color: var(--color-ink);
  transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;

  &:hover {
    transform: translateY(-6px);
    border-color: var(--color-accent);
    box-shadow: 0 12px 40px rgba(99, 102, 241, 0.1);
  }
}

.card-cover {
  aspect-ratio: 16 / 9;
  overflow: hidden;
  position: relative;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s;
  }

  .post-card:hover & img {
    transform: scale(1.05);
  }
}

.type-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.25);
  opacity: 0;
  transition: opacity 0.3s ease;

  .post-card:hover & {
    opacity: 1;
  }
}

.play-icon {
  width: 48px;
  height: 48px;
  color: rgba(255, 255, 255, 0.9);
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.4));
}

.stack-icon {
  width: 32px;
  height: 32px;
  color: rgba(255, 255, 255, 0.9);
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.4));
}

.card-body {
  padding: 20px;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;

  .category-icon {
    width: 18px;
    height: 18px;
    display: grid;
    place-items: center;
    flex-shrink: 0;
    color: var(--color-ctf);

    :deep(svg) {
      width: 18px;
      height: 18px;
    }
    :deep(.icon-fill) { fill: currentColor; opacity: 0.14; }
    :deep(.icon-stroke) { fill: none; stroke: currentColor; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; opacity: 0.8; }
    :deep(.icon-bright) { opacity: 1; stroke-width: 3.2; }
    :deep(.icon-dot) { fill: currentColor; opacity: 0.9; }
    :deep(.icon-shell) { opacity: 0.9; }
  }

  .section-tag {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 4px;

    &.ctf { color: var(--color-ctf); background: rgba(34, 211, 238, 0.1); }
    &.editing { color: var(--color-editing); background: rgba(244, 114, 182, 0.1); }
    &.games { color: var(--color-games); background: rgba(167, 139, 250, 0.1); }
  }

  .post-type {
    font-size: 11px;
    color: var(--color-ink-muted);
    padding: 2px 8px;
    border: 1px solid var(--color-hairline);
    border-radius: 4px;
  }
}

.card-title {
  font-family: var(--font-heading);
  font-size: 18px;
  font-weight: 600;
  line-height: 1.3;
  margin-bottom: 8px;
}

.card-excerpt {
  font-size: 14px;
  color: var(--color-ink-muted);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;

  .tags {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;

    .tag {
      font-size: 11px;
      padding: 1px 6px;
      border: 1px solid;
      border-radius: 3px;
    }
  }

  .views {
    font-size: 12px;
    color: var(--color-ink-muted);
  }
}
</style>
