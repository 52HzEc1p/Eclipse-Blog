<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'

const props = defineProps({
  items: { type: Array, required: true },
  animationTime: { type: Number, default: 600 },
  particleCount: { type: Number, default: 15 },
  particleDistances: { type: Array, default: () => [90, 10] },
  particleR: { type: Number, default: 100 },
  timeVariance: { type: Number, default: 300 },
  colors: { type: Array, default: () => [1, 2, 3, 1, 2, 3, 1, 4] },
  initialActiveIndex: { type: Number, default: 0 },
})

const emit = defineEmits(['navigate'])

const containerRef = ref(null)
const navRef = ref(null)
const filterRef = ref(null)
const textRef = ref(null)
const activeIndex = ref(props.initialActiveIndex)

watch(() => props.initialActiveIndex, async (newVal) => {
  activeIndex.value = newVal
  await nextTick()
  if (newVal < 0) {
    textRef.value?.classList.remove('active')
    if (textRef.value) textRef.value.innerText = ''
    if (filterRef.value) {
      Object.assign(filterRef.value.style, { left: '0px', top: '0px', width: '0px', height: '0px' })
    }
    return
  }
  const activeLi = navRef.value?.querySelectorAll('li')[newVal]
  if (activeLi) {
    updateEffectPosition(activeLi)
    textRef.value?.classList.add('active')
  }
})

const colorVars = {
  1: '#6366f1',
  2: '#22d3ee',
  3: '#f472b6',
  4: '#a78bfa',
}

function noise(n = 1) {
  return n / 2 - Math.random() * n
}

function getXY(distance, pointIndex, totalPoints) {
  const angle = ((360 + noise(8)) / totalPoints) * pointIndex * (Math.PI / 180)
  return [distance * Math.cos(angle), distance * Math.sin(angle)]
}

function createParticle(i, t, d, r) {
  let rotate = noise(r / 10)
  return {
    start: getXY(d[0], props.particleCount - i, props.particleCount),
    end: getXY(d[1] + noise(7), props.particleCount - i, props.particleCount),
    time: t,
    scale: 1 + noise(0.2),
    color: props.colors[Math.floor(Math.random() * props.colors.length)],
    rotate: rotate > 0 ? (rotate + r / 20) * 10 : (rotate - r / 20) * 10,
  }
}

function makeParticles(element) {
  const d = props.particleDistances
  const r = props.particleR
  const bubbleTime = props.animationTime * 2 + props.timeVariance
  element.style.setProperty('--time', `${bubbleTime}ms`)

  for (let i = 0; i < props.particleCount; i++) {
    const t = props.animationTime * 2 + noise(props.timeVariance * 2)
    const p = createParticle(i, t, d, r)
    element.classList.remove('active')

    setTimeout(() => {
      const particle = document.createElement('span')
      const point = document.createElement('span')
      particle.classList.add('particle')
      particle.style.setProperty('--start-x', `${p.start[0]}px`)
      particle.style.setProperty('--start-y', `${p.start[1]}px`)
      particle.style.setProperty('--end-x', `${p.end[0]}px`)
      particle.style.setProperty('--end-y', `${p.end[1]}px`)
      particle.style.setProperty('--time', `${p.time}ms`)
      particle.style.setProperty('--scale', `${p.scale}`)
      particle.style.setProperty('--color', colorVars[p.color] || 'white')
      particle.style.setProperty('--rotate', `${p.rotate}deg`)

      point.classList.add('point')
      particle.appendChild(point)
      element.appendChild(particle)
      requestAnimationFrame(() => {
        element.classList.add('active')
      })
      setTimeout(() => {
        try { element.removeChild(particle) } catch {}
      }, t)
    }, 30)
  }
}

function updateEffectPosition(element) {
  if (!containerRef.value || !filterRef.value || !textRef.value) return
  const containerRect = containerRef.value.getBoundingClientRect()
  const pos = element.getBoundingClientRect()

  const styles = {
    left: `${pos.x - containerRect.x}px`,
    top: `${pos.y - containerRect.y}px`,
    width: `${pos.width}px`,
    height: `${pos.height}px`,
  }
  Object.assign(filterRef.value.style, styles)
  Object.assign(textRef.value.style, styles)
  textRef.value.innerText = element.innerText
}

function handleClick(e, index) {
  const liEl = e.currentTarget
  if (activeIndex.value === index) return

  activeIndex.value = index
  updateEffectPosition(liEl)

  if (filterRef.value) {
    const particles = filterRef.value.querySelectorAll('.particle')
    particles.forEach(p => filterRef.value.removeChild(p))
  }

  if (textRef.value) {
    textRef.value.classList.remove('active')
    void textRef.value.offsetWidth
    textRef.value.classList.add('active')
  }

  if (filterRef.value) {
    makeParticles(filterRef.value)
  }

  emit('navigate', props.items[index])
}

onMounted(() => {
  if (!navRef.value || !containerRef.value) return
  const activeLi = navRef.value.querySelectorAll('li')[activeIndex.value]
  if (activeLi) {
    updateEffectPosition(activeLi)
    textRef.value?.classList.add('active')
  }

  const resizeObserver = new ResizeObserver(() => {
    const currentActiveLi = navRef.value?.querySelectorAll('li')[activeIndex.value]
    if (currentActiveLi) {
      updateEffectPosition(currentActiveLi)
    }
  })
  resizeObserver.observe(containerRef.value)

  // Set color CSS variables on container
  if (containerRef.value) {
    Object.entries(colorVars).forEach(([key, val]) => {
      containerRef.value.style.setProperty(`--color-${key}`, val)
    })
  }
})
</script>

<template>
  <div ref="containerRef" class="gooey-nav-container">
    <nav>
      <ul ref="navRef">
        <li
          v-for="(item, index) in items"
          :key="index"
          :class="{ active: activeIndex === index }"
          @click="handleClick($event, index)"
        >
          <a :href="item.href || '#'" @click.prevent>{{ item.label }}</a>
        </li>
      </ul>
    </nav>
    <span ref="filterRef" class="effect filter" />
    <span ref="textRef" class="effect text" aria-hidden="true" />
  </div>
</template>

<style scoped>
:root {
  --linear-ease: linear(
    0,
    0.068,
    0.19 2.7%,
    0.804 8.1%,
    1.037,
    1.199 13.2%,
    1.245,
    1.27 15.8%,
    1.274,
    1.272 17.4%,
    1.249 19.1%,
    0.996 28%,
    0.949,
    0.928 33.3%,
    0.926,
    0.933 36.8%,
    1.001 45.6%,
    1.013,
    1.019 50.8%,
    1.018 54.4%,
    1 63.1%,
    0.995 68%,
    1.001 85%,
    1
  );
}

.gooey-nav-container {
  position: relative;
  font-size: 15px;
  font-weight: 700;
  line-height: 1;
}

.gooey-nav-container nav {
  display: flex;
  position: relative;
  transform: translate3d(0, 0, 0.01px);
}

.gooey-nav-container nav ul {
  display: flex;
  gap: 2em;
  list-style: none;
  padding: 0 1em;
  margin: 0;
  position: relative;
  z-index: 3;
  color: white;
  text-shadow: 0 1px 1px hsl(205deg 30% 10% / 0.14);
}

.gooey-nav-container nav ul li {
  border-radius: 100vw;
  position: relative;
  cursor: pointer;
  transition:
    background-color 0.3s ease,
    color 0.3s ease,
    box-shadow 0.3s ease;
  box-shadow: 0 0 0.5px 1.5px transparent;
  color: white;
}

.gooey-nav-container nav ul li a {
  display: inline-block;
  padding: 0.6em 1em;
  text-decoration: none;
  color: inherit;
  white-space: nowrap;
}

.gooey-nav-container nav ul li.active a {
  color: transparent;
  text-shadow: none;
}

.gooey-nav-container nav ul li:focus-within:has(:focus-visible) {
  box-shadow: 0 0 0.5px 1.5px white;
}

.gooey-nav-container nav ul li::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 10px;
  background: white;
  opacity: 0;
  transform: scale(0);
  transition: all 0.3s ease;
  z-index: -1;
}

.gooey-nav-container nav ul li.active {
  color: black;
  text-shadow: none;
}

.gooey-nav-container nav ul li.active::after {
  opacity: 1;
  transform: scale(1);
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.82);
}

.gooey-nav-container .effect {
  position: absolute;
  left: 0;
  top: 0;
  width: 0;
  height: 0;
  opacity: 1;
  pointer-events: none;
  display: grid;
  place-items: center;
  z-index: 1;
}

.gooey-nav-container .effect.text {
  color: white;
  transition: color 0.3s ease;
  white-space: nowrap;
}

.gooey-nav-container .effect.text.active {
  color: black;
}

.gooey-nav-container .effect.filter {
  filter: blur(2px) contrast(24);
  mix-blend-mode: lighten;
}

.gooey-nav-container .effect.filter::before {
  content: '';
  position: absolute;
  inset: -10px;
  z-index: -2;
  background: transparent;
}

.gooey-nav-container .effect.filter::after {
  content: '';
  position: absolute;
  inset: 0;
  background: white;
  transform: scale(0);
  opacity: 0;
  z-index: -1;
  border-radius: 100vw;
}

.gooey-nav-container .effect.active::after {
  animation: pill 0.3s ease both;
}

@keyframes pill {
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.particle,
.point {
  display: block;
  opacity: 0;
  width: 20px;
  height: 20px;
  border-radius: 100%;
  transform-origin: center;
}

.particle {
  --time: 5s;
  position: absolute;
  top: calc(50% - 8px);
  left: calc(50% - 8px);
  animation: particle calc(var(--time)) ease 1 -350ms;
}

.point {
  background: var(--color);
  opacity: 1;
  animation: point calc(var(--time)) ease 1 -350ms;
}

@keyframes particle {
  0% {
    transform: rotate(0deg) translate(calc(var(--start-x)), calc(var(--start-y)));
    opacity: 1;
    animation-timing-function: cubic-bezier(0.55, 0, 1, 0.45);
  }
  70% {
    transform: rotate(calc(var(--rotate) * 0.5)) translate(calc(var(--end-x) * 1.2), calc(var(--end-y) * 1.2));
    opacity: 1;
    animation-timing-function: ease;
  }
  85% {
    transform: rotate(calc(var(--rotate) * 0.66)) translate(calc(var(--end-x)), calc(var(--end-y)));
    opacity: 1;
  }
  100% {
    transform: rotate(calc(var(--rotate) * 1.2)) translate(calc(var(--end-x) * 0.5), calc(var(--end-y) * 0.5));
    opacity: 1;
  }
}

@keyframes point {
  0% {
    transform: scale(0);
    opacity: 0;
    animation-timing-function: cubic-bezier(0.55, 0, 1, 0.45);
  }
  25% {
    transform: scale(calc(var(--scale) * 0.25));
  }
  38% {
    opacity: 1;
  }
  65% {
    transform: scale(var(--scale));
    opacity: 1;
    animation-timing-function: ease;
  }
  85% {
    transform: scale(var(--scale));
    opacity: 1;
  }
  100% {
    transform: scale(0);
    opacity: 0;
  }
}
</style>
