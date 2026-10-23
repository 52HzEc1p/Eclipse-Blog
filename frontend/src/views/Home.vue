<script setup>
import { onMounted, onUnmounted, ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import gsap from 'gsap'
import { getSectionPage } from '../api'
import EvilEye from '../components/effects/EvilEye.vue'
import BorderGlow from '../components/effects/BorderGlow.vue'
import TrueFocus from '../components/effects/TrueFocus.vue'
import ShinyText from '../components/effects/ShinyText.vue'
import { site } from '../config/site'

const router = useRouter()
const heroRef = ref(null)
const titleRef = ref(null)
const sloganRef = ref(null)
const scrollRef = ref(null)
const sectionsRef = ref(null)
const prefersReducedMotion = ref(false)
const eyeState = reactive({
  openProgress: 0.04,
})
let introTimeline = null
let isClosingForNavigation = false

// 视频背景: 为空时只显示 EvilEye 效果，有值时渲染视频
const videoSrc = ref('')
const hasVideo = computed(() => !!videoSrc.value)

const defaultSectionLinks = [
  {
    section: 'ctf',
    name: 'Articles',
    path: '/ctf',
    color: 'var(--color-ctf)',
    desc: '文章 · 笔记 · 随笔',
    icon: 'article',
    glowColors: ['#22d3ee', '#38bdf8', '#6366f1'],
  },
  {
    section: 'editing',
    name: 'Projects',
    path: '/editing',
    color: 'var(--color-editing)',
    desc: '作品 · 演示 · 创作过程',
    icon: 'film',
    glowColors: ['#f472b6', '#e879f9', '#fb7185'],
  },
  {
    section: 'games',
    name: 'Gallery',
    path: '/games',
    color: 'var(--color-games)',
    desc: '影像 · 片段 · 灵感收藏',
    icon: 'image',
    glowColors: ['#a78bfa', '#c084fc', '#818cf8'],
  },
]
const sectionLinks = ref(defaultSectionLinks.map(link => ({ ...link })))

function getIcon(name) {
  const icons = {
    article: `<svg viewBox="0 0 24 24" aria-hidden="true"><rect class="icon-fill" x="5" y="3" width="14" height="18" rx="2"/><rect class="icon-stroke icon-shell" x="5" y="3" width="14" height="18" rx="2"/><path class="icon-stroke icon-bright" d="M9 8h6M9 12h6M9 16h4"/></svg>`,
    film: `<svg viewBox="0 0 24 24" aria-hidden="true"><rect class="icon-fill" x="4" y="4" width="16" height="16" rx="2.5"/><rect class="icon-stroke icon-shell" x="4" y="4" width="16" height="16" rx="2.5"/><path class="icon-stroke" d="M9 4v16M15 4v16"/><path class="icon-stroke icon-bright" d="m11.2 9.6 3.6 2.4-3.6 2.4z"/><circle class="icon-dot" cx="6.5" cy="9" r="0.55"/><circle class="icon-dot" cx="6.5" cy="15" r="0.55"/><circle class="icon-dot" cx="17.5" cy="9" r="0.55"/><circle class="icon-dot" cx="17.5" cy="15" r="0.55"/></svg>`,
    image: `<svg viewBox="0 0 24 24" aria-hidden="true"><rect class="icon-fill" x="3" y="3" width="18" height="18" rx="2"/><rect class="icon-stroke icon-shell" x="3" y="3" width="18" height="18" rx="2"/><circle class="icon-dot" cx="8" cy="8" r="1.5"/><path class="icon-stroke icon-bright" d="m3 17 5-5 4 4 4-6 5 7"/></svg>`,
  }
  return icons[name] || ''
}

function navigateTo(path) {
  router.push(path)
}

function closeEyeAndNavigate(path) {
  if (!path || isClosingForNavigation) return
  isClosingForNavigation = true
  introTimeline?.kill()
  gsap.killTweensOf(eyeState)
  gsap.killTweensOf(heroRef.value)
  window.scrollTo({ top: 0, left: 0, behavior: 'auto' })
  gsap.set(heroRef.value, { opacity: 1, y: 0, filter: 'none' })
  const eyeDuration = prefersReducedMotion.value ? 1.4 : 2.4

  const closingTargets = [
    titleRef.value,
    sloganRef.value,
    scrollRef.value,
  ].filter(Boolean)

  const tl = gsap.timeline({
    onComplete: () => router.push(path),
  })

  tl.to(closingTargets, {
    opacity: 0,
    y: -16,
    duration: 0.62,
    ease: 'power2.in',
  }, 0)
  .to(eyeState, {
    openProgress: 0.012,
    duration: eyeDuration,
    ease: 'power3.inOut',
  }, 0)
}

function handleCloseAndNavigate(event) {
  closeEyeAndNavigate(event.detail?.path)
}

onMounted(() => {
  Promise.all(
    defaultSectionLinks.map(async (link) => {
      try {
        const page = await getSectionPage(link.section)
        return {
          ...link,
          name: page.title || link.name,
          desc: page.description || link.desc,
        }
      } catch {
        return link
      }
    })
  ).then((links) => {
    sectionLinks.value = links
  })

  window.scrollTo({ top: 0, left: 0, behavior: 'auto' })
  window.addEventListener('eclipse:home-close-and-navigate', handleCloseAndNavigate)
  prefersReducedMotion.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const introDuration = prefersReducedMotion.value ? 1.4 : 2.4
  const titleDelay = prefersReducedMotion.value ? 0.65 : 1.25

  const tl = gsap.timeline({ delay: 0.05 })
  introTimeline = tl
  gsap.set(heroRef.value, { opacity: 1, y: 0, filter: 'none' })

  tl.to(eyeState, {
    openProgress: 1,
    duration: introDuration,
    ease: 'power3.inOut',
  }, 0)
  .from(titleRef.value, {
    y: 40,
    opacity: 0,
    duration: 1.2,
    ease: 'power3.out',
  }, titleDelay)
  .from(sloganRef.value, {
    y: 20,
    opacity: 0,
    duration: 0.8,
    ease: 'power3.out',
  }, '-=0.6')
  .from(scrollRef.value, {
    opacity: 0,
    duration: 0.6,
    ease: 'power2.out',
  }, '-=0.3')

  // 滚动时 Hero 淡出
  gsap.to(heroRef.value, {
    opacity: 0,
    y: -50,
    scrollTrigger: {
      trigger: heroRef.value,
      start: 'top top',
      end: '80% top',
      scrub: true,
    },
  })

  // 板块卡片交错入场
  if (sectionsRef.value) {
    gsap.from(sectionsRef.value.querySelectorAll('.section-card-wrapper'), {
      y: 40,
      opacity: 0,
      duration: 0.7,
      stagger: 0.12,
      ease: 'power3.out',
      scrollTrigger: { trigger: sectionsRef.value, start: 'top 80%' },
    })
  }
})

onUnmounted(() => {
  window.removeEventListener('eclipse:home-close-and-navigate', handleCloseAndNavigate)
  introTimeline?.kill()
})
</script>

<template>
  <div class="home">
    <!-- Hero 区域 -->
    <section ref="heroRef" class="hero">
      <!-- 视频背景 -->
      <video
        v-if="hasVideo"
        class="hero-video"
        :src="videoSrc"
        autoplay
        muted
        loop
        playsinline
      ></video>

      <!-- EvilEye 邪眼背景 -->
      <EvilEye
        eye-color="#6366f1"
        :intensity="0.96"
        :pupil-size="0.68"
        :iris-width="0.25"
        :glow-intensity="0.52"
        :scale="0.95"
        :noise-scale="1"
        :pupil-follow="1.0"
        :flame-speed="0.62"
        :open-progress="eyeState.openProgress"
        :tremor-intensity="0.72"
        :tremor-speed="1.15"
        background-color="#0a0a0f"
      />

      <!-- 暗色渐变遮罩 (保证文字可读性) -->
      <div class="hero-overlay"></div>

      <!-- 内容 -->
      <div class="hero-content">
        <h1 class="sr-only">{{ site.heroTitle }}</h1>
        <div ref="titleRef" class="hero-title-wrap">
          <TrueFocus
            :sentence="site.heroTitle"
            :blur-amount="6"
            border-color="#6366f1"
            glow-color="rgba(99, 102, 241, 0.5)"
            :animation-duration="0.6"
            :pause-between-animations="1.5"
            font-size="clamp(48px, 10vw, 100px)"
          />
        </div>
        <div ref="sloganRef" class="hero-slogan">
          <ShinyText
            :text="site.slogan"
            :speed="3"
            color="#8a8a9a"
            shine-color="#c4b5fd"
            :spread="120"
            class="slogan-text"
          />
        </div>
        <div ref="scrollRef" class="scroll-hint">
          <span class="scroll-arrow"></span>
        </div>
      </div>
    </section>

    <!-- 板块入口 -->
    <section ref="sectionsRef" class="sections container">
      <div class="section-cards">
        <div
          v-for="s in sectionLinks"
          :key="s.path"
          class="section-card-wrapper"
        >
          <BorderGlow
            :background-color="'rgba(18, 18, 26, 0.8)'"
            :colors="s.glowColors"
            :edge-sensitivity="25"
            :glow-radius="30"
            :glow-intensity="1.2"
            :border-radius="8"
            :fill-opacity="0.4"
          >
            <router-link
              :to="s.path"
              class="section-card"
              :style="{ '--accent': s.color }"
            >
              <div class="card-icon" v-html="getIcon(s.icon)"></div>
              <h3>{{ s.name }}</h3>
              <p>{{ s.desc }}</p>
              <span class="card-arrow">→</span>
            </router-link>
          </BorderGlow>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="container">
        <p class="footer-text">{{ site.name }} · {{ site.slogan }}</p>
        <p v-if="site.icpNumber" class="footer-icp">
          <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">
            {{ site.icpNumber }}
          </a>
        </p>
      </div>
    </footer>
  </div>
</template>

<style lang="scss" scoped>
.home {
  // Keep the card glow, but do not let its padded edge create horizontal page scrolling.
  overflow-x: clip;
}

// === Hero ===
.hero {
  height: 100vh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #0a0a0f;
}

.hero-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}

:deep(.evil-eye-container) {
  z-index: 1;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(10, 10, 15, 0.12) 0%,
    rgba(10, 10, 15, 0.22) 50%,
    rgba(10, 10, 15, 0.86) 100%
  );
  z-index: 3;
  pointer-events: none;
}

.hero-content {
  position: relative;
  z-index: 4;
  text-align: center;
}

.hero-title-wrap {
  display: flex;
  justify-content: center;
  filter: drop-shadow(0 0 80px rgba(99, 102, 241, 0.3)) drop-shadow(0 0 160px rgba(99, 102, 241, 0.1));
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.hero-slogan {
  font-size: 18px;
  margin-top: 16px;
  letter-spacing: 4px;
  font-family: var(--font-heading);

  .slogan-text {
    font-family: inherit;
  }
}

.scroll-hint {
  margin-top: 64px;
  display: flex;
  justify-content: center;

  .scroll-arrow {
    display: block;
    width: 24px;
    height: 24px;
    border-right: 2px solid var(--color-ink-muted);
    border-bottom: 2px solid var(--color-ink-muted);
    transform: rotate(45deg);
    animation: scrollBounce 2s infinite;
  }
}

@keyframes scrollBounce {
  0%, 100% { transform: rotate(45deg) translateY(0); opacity: 1; }
  50% { transform: rotate(45deg) translateY(8px); opacity: 0.5; }
}

// === 板块入口 ===
.sections {
  padding: 80px 24px;
}

.section-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
  align-items: stretch;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.section-card-wrapper {
  cursor: pointer;
  height: 100%;
}

:deep(.border-glow-card),
:deep(.border-glow-inner) {
  height: 100%;
}

.section-card {
  display: flex;
  flex-direction: column;
  padding: 40px 32px;
  text-decoration: none;
  color: var(--color-ink);
  position: relative;
  min-height: 230px;
  height: 100%;

  .card-icon {
    width: 64px;
    height: 64px;
    display: grid;
    place-items: center;
    margin-bottom: 22px;
    color: var(--accent);
    position: relative;
    isolation: isolate;
    overflow: hidden;
    border: 1px solid color-mix(in srgb, var(--accent) 34%, transparent);
    border-radius: 8px;
    background:
      radial-gradient(circle at 28% 18%, color-mix(in srgb, var(--accent) 34%, transparent), transparent 34%),
      linear-gradient(145deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.02) 44%, rgba(0, 0, 0, 0.2));
    box-shadow:
      inset 0 1px 0 rgba(255, 255, 255, 0.16),
      0 16px 36px color-mix(in srgb, var(--accent) 22%, transparent);

    &::before {
      content: '';
      position: absolute;
      inset: -42% 18% 38% -42%;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.36), transparent 58%);
      transform: rotate(-12deg);
      opacity: 0.58;
      z-index: -1;
    }

    :deep(svg) {
      width: 48px;
      height: 48px;
      filter: drop-shadow(0 8px 18px color-mix(in srgb, var(--accent) 42%, transparent));
      transition: transform 0.3s ease, filter 0.3s ease;
    }

    :deep(.icon-fill) {
      fill: currentColor;
      opacity: 0.16;
    }

    :deep(.icon-stroke) {
      fill: none;
      stroke: currentColor;
      stroke-width: 1.8;
      stroke-linecap: round;
      stroke-linejoin: round;
      opacity: 0.82;
    }

    :deep(.icon-shell) {
      opacity: 0.95;
    }

    :deep(.icon-bright) {
      stroke-width: 2.1;
      opacity: 1;
    }

    :deep(.icon-dot) {
      fill: currentColor;
      opacity: 0.95;
    }
  }

  h3 {
    font-family: var(--font-heading);
    font-size: 28px;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 8px;
  }

  p {
    font-size: 15px;
    color: var(--color-ink-muted);
    line-height: 1.6;
    min-height: 48px;
    max-width: 28ch;
    padding-right: 28px;
  }

  .card-arrow {
    position: absolute;
    bottom: 28px;
    right: 28px;
    font-size: 22px;
    color: var(--accent);
    transition: transform 0.3s;
  }

  &:hover .card-arrow {
    transform: translateX(6px);
  }

  &:hover .card-icon {
    border-color: color-mix(in srgb, var(--accent) 62%, transparent);
    box-shadow:
      inset 0 1px 0 rgba(255, 255, 255, 0.18),
      0 18px 44px color-mix(in srgb, var(--accent) 34%, transparent);

    :deep(svg) {
      transform: translateY(-2px) scale(1.05);
      filter: drop-shadow(0 10px 24px color-mix(in srgb, var(--accent) 52%, transparent));
    }
  }
}

// === 页脚 ===
.footer {
  padding: 40px 0;
  border-top: 1px solid var(--color-hairline);
  text-align: center;

  .footer-text {
    font-size: 13px;
    color: var(--color-ink-muted);
  }

  .footer-icp {
    margin-top: 8px;
    font-size: 13px;

    a {
      color: var(--color-ink-muted);

      &:hover {
        color: var(--color-accent-glow);
      }
    }
  }
}
</style>
