<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="not-found">
    <p class="nf-code">404</p>
    <h1 class="nf-title">这个坐标没有信号</h1>
    <p class="nf-desc">你访问的页面不存在，可能已被移动或删除。</p>
    <div class="nf-actions">
      <button type="button" class="nf-btn primary" @click="router.push('/')">返回首页</button>
      <button type="button" class="nf-btn" @click="router.back()">回到上一页</button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 88px 24px 60px;
  text-align: center;
  background:
    radial-gradient(circle at 50% 20%, rgba(99, 102, 241, 0.12), transparent 45%),
    #05060a;
}

.nf-code {
  font-family: 'JetBrains Mono', monospace;
  font-size: clamp(72px, 14vw, 140px);
  font-weight: 700;
  line-height: 1;
  margin: 0;
  background: linear-gradient(120deg, #22d3ee, #a78bfa, #f472b6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.nf-title {
  font-size: 22px;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0;
}

.nf-desc {
  font-size: 14px;
  color: #9ca3af;
  margin: 0 0 12px;
}

.nf-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.nf-btn {
  padding: 10px 22px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.05);
  color: #d1d5db;
  font-size: 14px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;

  &:hover {
    border-color: rgba(34, 211, 238, 0.5);
    background: rgba(34, 211, 238, 0.08);
  }

  &.primary {
    background: linear-gradient(120deg, rgba(34, 211, 238, 0.18), rgba(167, 139, 250, 0.18));
    border-color: rgba(34, 211, 238, 0.4);
    color: #f3f4f6;
  }
}
</style>
