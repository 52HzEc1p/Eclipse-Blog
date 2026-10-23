<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: { type: Number, default: 1 },
  totalCount: { type: Number, default: 0 },
  pageSize: { type: Number, default: 8 },
  loading: { type: Boolean, default: false },
  accent: { type: String, default: 'var(--color-ctf)' },
})

const emit = defineEmits(['change'])

const totalPages = computed(() => Math.max(1, Math.ceil(props.totalCount / props.pageSize)))
const hasPages = computed(() => props.totalCount > props.pageSize)

function changePage(page) {
  const nextPage = Math.min(totalPages.value, Math.max(1, page))
  if (nextPage === props.currentPage || props.loading) return
  emit('change', nextPage)
}
</script>

<template>
  <nav
    v-if="hasPages"
    class="pagination-controls"
    :style="{ '--pager-accent': accent }"
    aria-label="内容分页"
  >
    <button
      type="button"
      :disabled="currentPage <= 1 || loading"
      @click="changePage(currentPage - 1)"
    >
      Prev
    </button>
    <span>{{ currentPage }} / {{ totalPages }}</span>
    <button
      type="button"
      :disabled="currentPage >= totalPages || loading"
      @click="changePage(currentPage + 1)"
    >
      Next
    </button>
  </nav>
</template>

<style lang="scss" scoped>
.pagination-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 26px;

  button,
  span {
    min-height: 40px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
  }

  button {
    min-width: 82px;
    padding: 0 16px;
    border: 1px solid color-mix(in srgb, var(--pager-accent) 42%, transparent);
    color: color-mix(in srgb, var(--pager-accent) 86%, white);
    background: rgba(255, 255, 255, 0.045);
    cursor: pointer;
    transition: background 0.22s ease, color 0.22s ease, transform 0.22s ease;

    &:hover:not(:disabled) {
      color: #050508;
      background: var(--pager-accent);
      transform: translateY(-1px);
    }

    &:disabled {
      cursor: not-allowed;
      opacity: 0.38;
    }
  }

  span {
    min-width: 70px;
    display: inline-grid;
    place-items: center;
    padding: 0 14px;
    color: rgba(239, 244, 255, 0.76);
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(255, 255, 255, 0.035);
  }
}
</style>
