<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  sentence: { type: String, default: 'True Focus' },
  separator: { type: String, default: ' ' },
  blurAmount: { type: Number, default: 5 },
  borderColor: { type: String, default: '#6366f1' },
  glowColor: { type: String, default: 'rgba(99, 102, 241, 0.6)' },
  animationDuration: { type: Number, default: 0.5 },
  pauseBetweenAnimations: { type: Number, default: 1.2 },
  fontSize: { type: String, default: 'clamp(48px, 10vw, 100px)' },
})

const words = computed(() => props.sentence.split(props.separator))
const currentIndex = ref(0)
const containerRef = ref(null)
const wordRefs = ref([])
const focusRect = ref({ x: 0, y: 0, width: 0, height: 0 })
const visible = ref(false)

let intervalId = null

function setWordRef(el, index) {
  wordRefs.value[index] = el
}

function updateRect() {
  if (currentIndex.value < 0 || !wordRefs.value[currentIndex.value] || !containerRef.value) return
  const parentRect = containerRef.value.getBoundingClientRect()
  const activeRect = wordRefs.value[currentIndex.value].getBoundingClientRect()
  focusRect.value = {
    x: activeRect.left - parentRect.left,
    y: activeRect.top - parentRect.top,
    width: activeRect.width,
    height: activeRect.height,
  }
  visible.value = true
}

onMounted(() => {
  intervalId = setInterval(() => {
    currentIndex.value = (currentIndex.value + 1) % words.value.length
    requestAnimationFrame(updateRect)
  }, (props.animationDuration + props.pauseBetweenAnimations) * 1000)

  // Initial update
  setTimeout(updateRect, 100)

  window.addEventListener('resize', updateRect)
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
  window.removeEventListener('resize', updateRect)
})
</script>

<template>
  <div ref="containerRef" class="true-focus-container" :style="{ fontSize }">
    <span
      v-for="(word, i) in words"
      :key="i"
      :ref="(el) => setWordRef(el, i)"
      class="focus-word"
      :class="{ active: i === currentIndex }"
      :style="{
        filter: i === currentIndex ? 'blur(0px)' : `blur(${blurAmount}px)`,
        transition: `filter ${animationDuration}s ease`,
      }"
    >{{ word }}</span>

    <div
      v-show="visible"
      class="focus-rect"
      :style="{
        left: `${focusRect.x}px`,
        top: `${focusRect.y}px`,
        width: `${focusRect.width}px`,
        height: `${focusRect.height}px`,
        opacity: currentIndex >= 0 ? 1 : 0,
        transition: `left ${animationDuration}s ease, top ${animationDuration}s ease, width ${animationDuration}s ease, height ${animationDuration}s ease, opacity ${animationDuration}s ease`,
        '--border-color': borderColor,
        '--glow-color': glowColor,
      }"
    >
      <span class="corner corner-tl"></span>
      <span class="corner corner-tr"></span>
      <span class="corner corner-bl"></span>
      <span class="corner corner-br"></span>
    </div>
  </div>
</template>

<style scoped>
.true-focus-container {
  position: relative;
  display: flex;
  gap: 0.3em;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  font-family: 'Space Grotesk', 'Noto Sans SC', sans-serif;
  font-weight: 700;
  letter-spacing: -4px;
  color: #e8e6e3;
  outline: none;
  user-select: none;
  filter: drop-shadow(0 0 80px rgba(99, 102, 241, 0.3)) drop-shadow(0 0 160px rgba(99, 102, 241, 0.1));
}

.focus-word {
  display: inline-block;
  will-change: filter;
}

.focus-rect {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  box-sizing: border-box;
}

.corner {
  position: absolute;
  width: 16px;
  height: 16px;
  border: 3px solid var(--border-color);
  border-radius: 3px;
  filter: drop-shadow(0 0 4px var(--glow-color));
}

.corner-tl {
  top: -10px;
  left: -10px;
  border-right: 0;
  border-bottom: 0;
}

.corner-tr {
  top: -10px;
  right: -10px;
  border-left: 0;
  border-bottom: 0;
}

.corner-bl {
  bottom: -10px;
  left: -10px;
  border-right: 0;
  border-top: 0;
}

.corner-br {
  bottom: -10px;
  right: -10px;
  border-left: 0;
  border-top: 0;
}
</style>
