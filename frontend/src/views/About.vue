<script setup>
import { computed, onMounted, ref } from 'vue'
import gsap from 'gsap'
import { getAboutPage } from '../api'
import { site } from '../config/site'

const rootRef = ref(null)
const contentRef = ref(null)
const videoReady = ref(false)

const defaultAboutContent = {
  "brand_name": "Eclipse",
  "kicker": "ABOUT / DEMO",
  "hero_title": "你好，这里是你的名字。",
  "hero_body": "这是一段作者介绍示例。你可以在这里介绍自己正在做的事、感兴趣的领域，以及希望通过这个博客分享的内容。",
  "identity_mark": "YOU",
  "identity_name": "Your Name",
  "identity_meta": "Your role / Your interests",
  "current_direction_label": "正在做的事",
  "current_direction": "用一小段文字介绍近期的计划、正在推进的项目，或希望继续探索的方向。这里的示例文字可以全部替换。",
  "contact_label": "找到你",
  "facets": [
    {
      "label": "01 / WRITE",
      "title": "Articles",
      "text": "分享知识、记录学习，也可以写日常随笔。用文章介绍你关注的话题。"
    },
    {
      "label": "02 / CREATE",
      "title": "Projects",
      "text": "展示已经完成或正在进行的作品，补充项目背景、过程和成果。"
    },
    {
      "label": "03 / COLLECT",
      "title": "Gallery",
      "text": "收集影像、片段与灵感，让值得保存的画面有一个展示的位置。"
    }
  ],
  "contacts": [
    {
      "name": "GitHub",
      "value": "你的代码主页（示例链接）",
      "url": "https://github.com/"
    },
    {
      "name": "Website",
      "value": "你的其他网站（示例链接）",
      "url": "https://example.com/"
    }
  ]
}

const aboutContent = ref({ ...defaultAboutContent })

const facets = computed(() => aboutContent.value.facets?.length
  ? aboutContent.value.facets
  : defaultAboutContent.facets)

const contactLinks = computed(() => aboutContent.value.contacts?.length
  ? aboutContent.value.contacts
  : defaultAboutContent.contacts)

onMounted(() => {
  getAboutPage()
    .then((data) => {
      aboutContent.value = {
        ...defaultAboutContent,
        ...data,
        facets: data.facets?.length ? data.facets : defaultAboutContent.facets,
        contacts: data.contacts?.length ? data.contacts : defaultAboutContent.contacts,
      }
    })
    .catch(() => {
      aboutContent.value = { ...defaultAboutContent }
    })

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reduce) return

  gsap.fromTo(
    rootRef.value?.querySelectorAll('.about-lid'),
    { scaleY: 1 },
    { scaleY: 0, duration: 1.15, ease: 'power4.inOut', stagger: 0.05, delay: 0.12 }
  )

  gsap.from(contentRef.value?.querySelectorAll('.about-animate'), {
    y: 34,
    opacity: 0,
    duration: 0.9,
    stagger: 0.08,
    ease: 'power3.out',
    delay: 0.76,
  })
})
</script>

<template>
  <section ref="rootRef" class="about-page" :class="{ ready: videoReady }">
    <video
      class="about-video"
      :src="site.aboutVideo"
      autoplay
      muted
      loop
      playsinline
      @canplay="videoReady = true"
    ></video>

    <div class="about-scrim"></div>
    <div class="about-lid about-lid-top"></div>
    <div class="about-lid about-lid-bottom"></div>

    <div ref="contentRef" class="about-shell">
      <p class="about-kicker about-animate">{{ aboutContent.kicker }}</p>

      <div class="about-hero">
        <div class="about-title-group about-animate">
          <h1>{{ aboutContent.hero_title }}</h1>
          <p>{{ aboutContent.hero_body }}</p>
        </div>

        <aside class="identity-panel about-animate">
          <span class="identity-mark">{{ aboutContent.identity_mark }}</span>
          <p>{{ aboutContent.identity_name }}</p>
          <small>{{ aboutContent.identity_meta }}</small>
        </aside>
      </div>

      <div class="facet-grid">
        <article
          v-for="item in facets"
          :key="item.label"
          class="facet-card about-animate"
        >
          <span>{{ item.label }}</span>
          <h2>{{ item.title }}</h2>
          <p>{{ item.text }}</p>
        </article>
      </div>

      <div class="about-bottom">
        <div class="philosophy about-animate">
          <span>{{ aboutContent.current_direction_label }}</span>
          <p>{{ aboutContent.current_direction }}</p>
        </div>

        <div class="contact-panel about-animate">
          <span>{{ aboutContent.contact_label }}</span>
          <a
            v-for="link in contactLinks"
            :key="link.name"
            :href="link.url"
            target="_blank"
            rel="noreferrer"
          >
            <strong>{{ link.name }}</strong>
            <small>{{ link.value }}</small>
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<style lang="scss" scoped>
.about-page {
  position: relative;
  min-height: calc(100vh - 64px);
  overflow: hidden;
  background: #050508;
  isolation: isolate;
}

.about-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center center;
  opacity: 0;
  transform: translateZ(0);
  filter: saturate(1.02) contrast(1.08) brightness(1.2);
  transition: opacity 0.8s ease;
  z-index: 0;
}

.about-page.ready .about-video {
  opacity: 1;
}

.about-scrim {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(5, 5, 8, 0.52) 0%, rgba(5, 5, 8, 0.16) 46%, rgba(5, 5, 8, 0.44) 100%),
    linear-gradient(180deg, rgba(5, 5, 8, 0.42) 0%, rgba(5, 5, 8, 0.06) 44%, rgba(5, 5, 8, 0.58) 100%);
  z-index: 1;
}

.about-lid {
  position: absolute;
  left: 0;
  right: 0;
  height: 50vh;
  background: #050508;
  z-index: 4;
  pointer-events: none;
  transform-origin: center bottom;
}

.about-lid-top {
  top: 0;
  transform-origin: center top;
}

.about-lid-bottom {
  bottom: 0;
  transform-origin: center bottom;
}

.about-shell {
  position: relative;
  z-index: 3;
  width: min(1180px, calc(100% - 48px));
  min-height: calc(100vh - 64px);
  margin: 0 auto;
  padding: 82px 0 64px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 30px;
}

.about-kicker {
  margin: 0;
  color: rgba(229, 234, 255, 0.58);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.about-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 32px;
  align-items: end;
}

.about-title-group {
  max-width: 820px;

  h1 {
    margin: 0;
    max-width: 15ch;
    color: #f6f7ff;
    font-family: 'HarmonyOS Sans SC', 'MiSans', 'Alibaba PuHuiTi 3.0', 'Microsoft YaHei UI', 'PingFang SC', 'Noto Sans SC', sans-serif;
    font-size: clamp(42px, 6vw, 82px);
    font-weight: 850;
    line-height: 1.08;
    letter-spacing: 0;
    text-wrap: balance;
    text-shadow: 0 14px 48px rgba(0, 0, 0, 0.34);
  }

  p {
    max-width: 680px;
    margin: 28px 0 0;
    color: rgba(237, 241, 255, 0.74);
    font-size: 17px;
    line-height: 1.9;
  }
}

.identity-panel,
.facet-card,
.philosophy,
.contact-panel {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 8px;
  background: rgba(10, 12, 20, 0.42);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(18px);
}

.identity-panel {
  padding: 24px;
  min-height: 220px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;

  .identity-mark {
    color: rgba(126, 239, 255, 0.86);
    font-family: var(--font-code);
    font-size: 14px;
    font-weight: 700;
  }

  p {
    margin: 8px 0 2px;
    color: #ffffff;
    font-family: var(--font-heading);
    font-size: 42px;
    font-weight: 800;
    line-height: 1;
  }

  small {
    color: rgba(232, 237, 255, 0.56);
    font-size: 12px;
  }
}

.facet-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.facet-card {
  min-height: 190px;
  padding: 22px;
  display: grid;
  grid-template-rows: 18px auto 1fr;
  align-content: start;
  gap: 12px;

  span {
    align-self: start;
    color: rgba(126, 239, 255, 0.7);
    font-family: var(--font-code);
    font-size: 12px;
    line-height: 18px;
    font-weight: 700;
  }

  h2 {
    margin: 0;
    color: #ffffff;
    font-family: var(--font-heading);
    font-size: 24px;
    line-height: 1.08;
    letter-spacing: 0;
  }

  p {
    margin: 0;
    color: rgba(234, 238, 255, 0.66);
    font-size: 14px;
    line-height: 1.7;
  }
}

.about-bottom {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 14px;
}

.philosophy,
.contact-panel {
  padding: 24px;

  > span {
    color: rgba(255, 255, 255, 0.48);
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
  }
}

.philosophy p {
  max-width: 720px;
  margin: 14px 0 0;
  color: rgba(243, 246, 255, 0.78);
  font-size: 16px;
  line-height: 1.85;
}

.contact-panel {
  display: grid;
  gap: 10px;

  a {
    min-height: 58px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 12px 0;
    color: #ffffff;
    text-decoration: none;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  strong {
    font-size: 17px;
  }

  small {
    margin-top: 4px;
    color: rgba(234, 238, 255, 0.56);
    font-size: 12px;
  }
}

@media (max-width: 920px) {
  .about-hero,
  .about-bottom {
    grid-template-columns: 1fr;
  }

  .facet-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .about-title-group h1 {
    max-width: 14ch;
  }
}

@media (max-width: 620px) {
  .about-shell {
    width: min(100% - 32px, 1180px);
    padding: 48px 0;
  }

  .about-title-group h1 {
    font-size: clamp(36px, 11vw, 56px);
  }

  .about-title-group p {
    font-size: 15px;
    line-height: 1.8;
  }

  .facet-grid {
    grid-template-columns: 1fr;
  }

  .identity-panel,
  .facet-card {
    min-height: 170px;
  }

}

@media (prefers-reduced-motion: reduce) {
  .about-lid {
    display: none;
  }

  .about-video {
    transition: opacity 0.2s ease;
  }
}
</style>
