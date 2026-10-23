<script setup>
import NavBar from './components/common/NavBar.vue'
</script>

<template>
  <div id="eclipse-app">
    <NavBar />
    <main class="main-content">
      <router-view v-slot="{ Component, route }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" :key="route.fullPath" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style lang="scss">
#eclipse-app {
  min-height: 100vh;
  background: var(--color-canvas);
  color: var(--color-ink);
}

.main-content {
  padding-top: 64px;
}

.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.42s ease, filter 0.42s ease;
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
  filter: blur(8px);
}
</style>
