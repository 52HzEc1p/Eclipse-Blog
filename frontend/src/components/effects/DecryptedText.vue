<script setup>
import { ref, onUnmounted } from 'vue'

const props = defineProps({
  text: { type: String, required: true },
  speed: { type: Number, default: 50 },
  maxIterations: { type: Number, default: 10 },
  characters: {
    type: String,
    default: 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+',
  },
})

const displayText = ref(props.text)
const isAnimating = ref(false)
const isRevealed = ref(true)
let intervalId = null

const availableChars = props.characters.split('')

function shuffleText(currentRevealed) {
  return props.text
    .split('')
    .map((char, i) => {
      if (char === ' ') return ' '
      if (currentRevealed.has(i)) return props.text[i]
      return availableChars[Math.floor(Math.random() * availableChars.length)]
    })
    .join('')
}

function triggerDecrypt() {
  if (isAnimating.value) return
  isAnimating.value = true
  isRevealed.value = false
  const revealed = new Set()
  let iterations = 0

  intervalId = setInterval(() => {
    displayText.value = shuffleText(revealed)
    iterations++
    if (iterations >= props.maxIterations) {
      clearInterval(intervalId)
      intervalId = null
      displayText.value = props.text
      isAnimating.value = false
      isRevealed.value = true
    }
  }, props.speed)
}

function onMouseEnter() {
  triggerDecrypt()
}

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
})
</script>

<template>
  <span
    class="decrypted-text"
    :class="{ revealed: isRevealed, animating: isAnimating }"
    @mouseenter="onMouseEnter"
  >
    <span aria-hidden="true">{{ displayText }}</span>
    <span class="sr-only">{{ text }}</span>
  </span>
</template>

<style scoped>
.decrypted-text {
  display: inline-block;
  font-family: var(--font-heading);
  font-size: inherit;
  font-weight: inherit;
  color: var(--color-ink);
  cursor: default;
  letter-spacing: inherit;
  user-select: none;
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
</style>
