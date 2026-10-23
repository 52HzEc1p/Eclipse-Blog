<script setup>
import { onMounted, ref } from 'vue'
import { POSTS_PAGE_SIZE, usePostStore } from '../../stores/post'
import { getSectionPage } from '../../api'
import Galaxy from '../../components/effects/Galaxy.vue'
import SectionGallery from '../../components/common/SectionGallery.vue'

const postStore = usePostStore()
const activeCategory = ref(null)

const defaultSectionPage = {
  "title": "Articles",
  "eyebrow": "// article archive",
  "description": "文章与笔记的示例栏目。这里可以放学习记录、经验分享和日常随笔，按照自己的主题慢慢整理。",
  "manifesto": "从一个问题、一段经历或一个想法开始。用文字、代码和配图说明过程，让每篇文章都能独立阅读。",
  "index_label": "ARTICLE / NOTE",
  "stat_one": {
    "value": "Aa",
    "label": "ideas & stories"
  },
  "stat_two": {
    "value": "MD",
    "label": "article archive"
  },
  "tags": [
    "notes",
    "ideas",
    "guides",
    "learning",
    "journal"
  ],
  "filters": [
    {
      "name": "All",
      "slug": null
    },
    {
      "name": "Notes",
      "slug": "notes"
    },
    {
      "name": "Guides",
      "slug": "guides"
    }
  ],
  "empty_text": "暂时没有匹配的文章",
  "filter_aria_label": "文章分类",
  "extra": {}
}

const sectionPage = ref({ ...defaultSectionPage })

onMounted(async () => {
  try {
    sectionPage.value = { ...defaultSectionPage, ...(await getSectionPage('ctf')) }
  } catch {
    sectionPage.value = { ...defaultSectionPage }
  }
  fetchPage(1)
})

function filterByCategory(slug) {
  activeCategory.value = activeCategory.value === slug ? null : slug
  fetchPage(1)
}

function fetchPage(page) {
  postStore.fetchPosts({
    section: 'ctf',
    category: activeCategory.value || undefined,
    page,
    page_size: POSTS_PAGE_SIZE,
  })
}
</script>

<template>
  <SectionGallery
    section-path="/ctf"
    accent="var(--color-ctf)"
    accent-soft="rgba(34, 211, 238, 0.22)"
    :eyebrow="sectionPage.eyebrow"
    :title="sectionPage.title"
    :description="sectionPage.description"
    :manifesto="sectionPage.manifesto"
    :index-label="sectionPage.index_label"
    :stat-one="sectionPage.stat_one"
    :stat-two="sectionPage.stat_two"
    :tags="sectionPage.tags"
    :filters="sectionPage.filters"
    :filter-aria-label="sectionPage.filter_aria_label"
    :active-category="activeCategory"
    :posts="postStore.posts"
    :loading="postStore.loading"
    :empty-text="sectionPage.empty_text"
    :current-page="postStore.currentPage"
    :total-count="postStore.totalCount"
    :page-size="POSTS_PAGE_SIZE"
    @filter="filterByCategory"
    @change-page="fetchPage"
  >
    <template #background>
      <Galaxy
        :hue-shift="190"
        :glow-intensity="0.35"
        :auto-center-repulsion="0.24"
        :density="0.72"
        :rotation-speed="0.035"
        :star-speed="0.32"
        :saturation="0.18"
      />
    </template>
  </SectionGallery>
</template>
