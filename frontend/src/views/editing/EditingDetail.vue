<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { usePostStore } from '../../stores/post'
import PostDetail from '../../components/common/PostDetail.vue'

const route = useRoute()
const postStore = usePostStore()

onMounted(() => {
  postStore.fetchPost(route.params.slug)
})
</script>

<template>
  <PostDetail
    v-if="postStore.currentPost"
    :post="postStore.currentPost"
    section-label="作品"
    section-class="editing"
  />
  <div v-else class="loading">加载中...</div>
</template>

<style scoped>
.loading {
  text-align: center;
  padding: 120px 0;
  color: var(--color-ink-muted);
}
</style>
