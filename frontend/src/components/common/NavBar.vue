<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GooeyNav from '../effects/GooeyNav.vue'
import DecryptedText from '../effects/DecryptedText.vue'
import { site } from '../../config/site'

const route = useRoute()
const router = useRouter()
const mobileMenuOpen = ref(false)

const navLinks = [
  { name: '首页', path: '/' },
  { name: 'Articles', path: '/ctf' },
  { name: 'Projects', path: '/editing' },
  { name: 'Gallery', path: '/games' },
]

const socialLinks = [
  {
    name: 'Bilibili',
    url: import.meta.env.VITE_BILIBILI_URL || 'https://space.bilibili.com/',
    icon: 'bilibili',
  },
  {
    name: 'Douyin',
    url: import.meta.env.VITE_DOUYIN_URL || 'https://www.douyin.com/',
    icon: 'douyin',
  },
  {
    name: 'GitHub',
    url: import.meta.env.VITE_GITHUB_URL || 'https://github.com/',
    icon: 'github',
  },
]

const gooeyItems = navLinks.map(l => ({ label: l.name, href: l.path }))

const activeIndex = computed(() => {
  if (route.path === '/about') return -1
  if (route.path === '/') return 0
  const idx = navLinks.findIndex(l => l.path !== '/' && (route.path === l.path || route.path.startsWith(l.path + '/')))
  return idx >= 0 ? idx : 0
})

function requestRoute(path) {
  mobileMenuOpen.value = false
  if (document.activeElement instanceof HTMLElement) {
    document.activeElement.blur()
  }
  if (route.path === path) return

  if (route.path === '/' && path === '/about') {
    window.dispatchEvent(new CustomEvent('eclipse:home-close-and-navigate', { detail: { path } }))
    return
  }

  router.push(path)
}

function handleNavigate(item) {
  requestRoute(item.href)
}

function getSocialIcon(icon) {
  const icons = {
    bilibili: `<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M14.7 13.4 10.9 8.8M33.3 13.4l3.8-4.6"/><rect x="7.5" y="14.5" width="33" height="25" rx="6.5"/><path d="M18 25.8v5.1M30 25.8v5.1M17.8 35h12.4"/></svg>`,
    douyin: `<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M29.8 8.5v21.1c0 6.5-4.5 10.9-10.6 10.9-5.3 0-9.2-3.5-9.2-8.4 0-5 3.9-8.4 9.2-8.4 1.1 0 2.1.2 3 .5v6.1c-.8-.5-1.7-.8-2.7-.8-1.9 0-3.2 1.1-3.2 2.7 0 1.6 1.3 2.7 3.1 2.7 2.2 0 3.5-1.5 3.5-4V8.5h6.9c.8 4.8 3.6 7.8 8.2 8.8v6.9c-3.4-.4-6.2-1.7-8.2-3.7Z"/></svg>`,
    github: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 19c-4.5 1.4-4.5-2.2-6-2.7M15 22v-3.9c0-1 .1-1.5-.5-2 2.8-.3 5.7-1.4 5.7-6.1 0-1.4-.5-2.5-1.3-3.4.1-.3.6-1.7-.1-3.4 0 0-1.1-.3-3.6 1.3a12.2 12.2 0 0 0-6.5 0C6.2 2.9 5.1 3.2 5.1 3.2c-.7 1.7-.2 3.1-.1 3.4A4.8 4.8 0 0 0 3.7 10c0 4.7 2.9 5.8 5.7 6.1-.4.4-.7 1-.7 1.9V22"/></svg>`,
  }
  return icons[icon] || ''
}
</script>

<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <div class="brand-cluster">
        <a
          href="/about"
          class="about-link"
          :class="{ active: route.path === '/about' }"
          @mousedown.prevent.stop="requestRoute('/about')"
          @pointerdown.prevent.stop="requestRoute('/about')"
          @click.prevent.stop="requestRoute('/about')"
        >
          About
        </a>

        <a href="/" class="navbar-logo" aria-label="返回首页" @click.prevent="requestRoute('/')">
          <DecryptedText
            :text="site.name"
            :speed="40"
            :max-iterations="8"
            class="logo-text"
          />
        </a>

        <div class="social-links" aria-label="社交媒体">
          <a
            v-for="social in socialLinks"
            :key="social.name"
            class="social-link"
            :href="social.url"
            :aria-label="social.name"
            target="_blank"
            rel="noreferrer"
            v-html="getSocialIcon(social.icon)"
          ></a>
        </div>
      </div>

      <div class="navbar-center">
        <GooeyNav
          :items="gooeyItems"
          :initial-active-index="activeIndex"
          :animation-time="500"
          :particle-count="8"
          :particle-distances="[46, 7]"
          :particle-r="46"
          :time-variance="250"
          @navigate="handleNavigate"
        />
      </div>

      <div class="navbar-spacer"></div>

      <button
        class="mobile-menu-btn"
        type="button"
        :aria-expanded="mobileMenuOpen"
        aria-label="打开导航"
        @click="mobileMenuOpen = !mobileMenuOpen"
      >
        <span :class="{ open: mobileMenuOpen }"></span>
      </button>
    </div>

    <div class="mobile-menu" :class="{ open: mobileMenuOpen }">
      <a
        href="/about"
        class="mobile-link"
        @mousedown.prevent.stop="requestRoute('/about')"
        @pointerdown.prevent.stop="requestRoute('/about')"
        @click.prevent.stop="requestRoute('/about')"
      >
        About
      </a>
      <a
        v-for="link in navLinks"
        :key="link.path"
        :href="link.path"
        class="mobile-link"
        @click.prevent="requestRoute(link.path)"
      >
        {{ link.name }}
      </a>
      <div class="mobile-socials">
        <a
          v-for="social in socialLinks"
          :key="social.name"
          :href="social.url"
          :aria-label="social.name"
          target="_blank"
          rel="noreferrer"
        >
          {{ social.name }}
        </a>
      </div>
    </div>
  </nav>
</template>

<style lang="scss" scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(10, 10, 15, 0.42);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.navbar-inner {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand-cluster {
  min-width: 260px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.about-link {
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  padding: 0 12px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 8px;
  color: rgba(236, 241, 255, 0.72);
  text-decoration: none;
  font-size: 13px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.035);
  transition: color 0.22s ease, border-color 0.22s ease, background 0.22s ease;

  &:hover,
  &.active {
    color: #ffffff;
    border-color: rgba(125, 139, 255, 0.52);
    background: rgba(99, 102, 241, 0.14);
  }
}

.navbar-logo {
  text-decoration: none;
  flex-shrink: 0;

  .logo-text {
    font-family: var(--font-heading);
    font-size: 20px;
    font-weight: 700;
    color: var(--color-ink);
    letter-spacing: 0;
  }
}

.social-links {
  display: flex;
  align-items: center;
  gap: 6px;
}

.social-link {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  color: rgba(235, 240, 255, 0.74);
  border: 1px solid transparent;
  transition: color 0.22s ease, border-color 0.22s ease, background 0.22s ease, transform 0.22s ease;

  :deep(svg) {
    width: 22px;
    height: 22px;
    fill: none;
    stroke: currentColor;
    stroke-width: 3.1;
    stroke-linecap: round;
    stroke-linejoin: round;
  }

  &:hover {
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.14);
    background: rgba(255, 255, 255, 0.075);
    transform: translateY(-1px);
  }
}

.navbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.navbar-spacer {
  width: 260px;
  flex-shrink: 0;
  visibility: hidden;
}

.mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  width: 44px;
  height: 44px;
  position: relative;
  flex-shrink: 0;

  span,
  span::before,
  span::after {
    display: block;
    width: 20px;
    height: 2px;
    background: var(--color-ink);
    transition: all 0.3s;
    position: absolute;
  }

  span { top: 21px; left: 12px; }
  span::before { content: ''; top: -6px; }
  span::after { content: ''; top: 6px; }

  span.open { background: transparent; }
  span.open::before { transform: rotate(45deg); top: 0; }
  span.open::after { transform: rotate(-45deg); top: 0; }
}

.mobile-menu {
  display: none;
  flex-direction: column;
  padding: 0 24px 16px;
  background: rgba(10, 10, 15, 0.96);

  &.open {
    display: flex;
  }

  .mobile-link {
    padding: 12px 0;
    color: var(--color-ink-muted);
    text-decoration: none;
    font-size: 16px;
    border-bottom: 1px solid var(--color-hairline);
  }
}

.mobile-socials {
  display: flex;
  gap: 12px;
  padding-top: 14px;

  a {
    min-height: 40px;
    display: inline-flex;
    align-items: center;
    color: rgba(236, 241, 255, 0.8);
    text-decoration: none;
    font-size: 14px;
  }
}

@media (max-width: 980px) {
  .brand-cluster {
    min-width: auto;
  }

  .navbar-spacer {
    width: 190px;
  }

  .social-links {
    display: none;
  }
}

@media (max-width: 768px) {
  .navbar-center { display: none; }
  .navbar-spacer { display: none; }
  .mobile-menu-btn { display: block; }
  .about-link { display: none; }
}
</style>
