import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getPosts, getPost, getFeaturedPosts } from '../api'

export const POSTS_PAGE_SIZE = 8

export const usePostStore = defineStore('post', () => {
  // 状态
  const posts = ref([])           // 文章列表
  const currentPost = ref(null)   // 当前文章详情
  const featured = ref([])        // 精选文章
  const loading = ref(false)      // 加载状态
  const totalCount = ref(0)       // 文章总数
  const currentPage = ref(1)      // 当前页码
  const latestWorks = ref([])     // 最新作品

  // 获取文章列表
  async function fetchPosts(params = {}) {
    loading.value = true
    try {
      const data = await getPosts(params)
      posts.value = data.results
      totalCount.value = data.count
      currentPage.value = Number(params.page || 1)
    } finally {
      loading.value = false
    }
  }

  // 获取文章详情
  async function fetchPost(slug) {
    loading.value = true
    try {
      currentPost.value = await getPost(slug)
    } finally {
      loading.value = false
    }
  }

  // 获取精选文章
  async function fetchFeatured() {
    featured.value = await getFeaturedPosts()
  }

  // 获取最新作品 (剪辑板块)
  async function fetchLatestWorks() {
    const data = await getPosts({ section: 'editing', page_size: POSTS_PAGE_SIZE })
    latestWorks.value = (data.results || []).slice(0, 4)
  }

  return {
    posts, currentPost, featured, latestWorks, loading, totalCount, currentPage,
    fetchPosts, fetchPost, fetchFeatured, fetchLatestWorks,
  }
})
