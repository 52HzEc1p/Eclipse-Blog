<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  src: { type: String, required: true },
})

const videoRef = ref(null)
let rafId = null
let fadingOutRef = false
let listeners = []

const FADE_MS = 500
const FADE_OUT_LEAD = 0.55

function fadeTo(target, duration) {
  if (rafId) cancelAnimationFrame(rafId)

  const video = videoRef.value
  if (!video) return

  const startOpacity = parseFloat(video.style.opacity) || 0
  const startTime = performance.now()

  function step(now) {
    const elapsed = now - startTime
    const progress = Math.min(elapsed / duration, 1)
    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3)
    video.style.opacity = startOpacity + (target - startOpacity) * eased

    if (progress < 1) {
      rafId = requestAnimationFrame(step)
    } else {
      video.style.opacity = target
      rafId = null
    }
  }

  rafId = requestAnimationFrame(step)
}

function onLoadedData() {
  const video = videoRef.value
  if (!video) return
  video.style.opacity = '0'
  video.play()
  fadeTo(1, FADE_MS)
}

function onTimeUpdate() {
  const video = videoRef.value
  if (!video || fadingOutRef) return
  const remaining = video.duration - video.currentTime
  if (remaining <= FADE_OUT_LEAD && remaining > 0) {
    fadingOutRef = true
    fadeTo(0, FADE_MS)
  }
}

function onEnded() {
  const video = videoRef.value
  if (!video) return
  video.style.opacity = '0'
  setTimeout(() => {
    video.currentTime = 0
    video.play()
    fadingOutRef = false
    fadeTo(1, FADE_MS)
  }, 100)
}

onMounted(() => {
  const video = videoRef.value
  if (!video) return
  video.style.opacity = '0'

  video.addEventListener('loadeddata', onLoadedData)
  video.addEventListener('timeupdate', onTimeUpdate)
  video.addEventListener('ended', onEnded)
  listeners = [
    ['loadeddata', onLoadedData],
    ['timeupdate', onTimeUpdate],
    ['ended', onEnded],
  ]
})

onUnmounted(() => {
  if (rafId) cancelAnimationFrame(rafId)
  const video = videoRef.value
  if (video) {
    listeners.forEach(([event, handler]) => video.removeEventListener(event, handler))
  }
})
</script>

<template>
  <video
    ref="videoRef"
    :src="src"
    muted
    playsinline
    preload="auto"
    class="fading-video"
  ></video>
</template>

<style scoped>
.fading-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}
</style>
