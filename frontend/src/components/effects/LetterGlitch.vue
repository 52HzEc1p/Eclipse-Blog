<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  glitchColors: {
    type: Array,
    default: () => ['#2b4539', '#61dca3', '#61b3dc'],
  },
  glitchSpeed: { type: Number, default: 50 },
  centerVignette: { type: Boolean, default: false },
  outerVignette: { type: Boolean, default: true },
  smooth: { type: Boolean, default: true },
  characters: {
    type: String,
    default: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$&*()-_+=/[]{};:<>.,0123456789',
  },
})

const canvasRef = ref(null)
let animationId = null
let letters = []
let grid = { columns: 0, rows: 0 }
let ctx = null
let lastGlitchTime = Date.now()

const fontSize = 16
const charWidth = 10
const charHeight = 20

const lettersAndSymbols = Array.from(props.characters)

function getRandomChar() {
  return lettersAndSymbols[Math.floor(Math.random() * lettersAndSymbols.length)]
}

function getRandomColor() {
  return props.glitchColors[Math.floor(Math.random() * props.glitchColors.length)]
}

function hexToRgb(hex) {
  const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i
  hex = hex.replace(shorthandRegex, (_m, r, g, b) => r + r + g + g + b + b)
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result
    ? { r: parseInt(result[1], 16), g: parseInt(result[2], 16), b: parseInt(result[3], 16) }
    : null
}

function interpolateColor(start, end, factor) {
  const r = Math.round(start.r + (end.r - start.r) * factor)
  const g = Math.round(start.g + (end.g - start.g) * factor)
  const b = Math.round(start.b + (end.b - start.b) * factor)
  return `rgb(${r}, ${g}, ${b})`
}

function calculateGrid(width, height) {
  const columns = Math.ceil(width / charWidth)
  const rows = Math.ceil(height / charHeight)
  return { columns, rows }
}

function initializeLetters(columns, rows) {
  grid = { columns, rows }
  const totalLetters = columns * rows
  letters = Array.from({ length: totalLetters }, () => ({
    char: getRandomChar(),
    color: getRandomColor(),
    targetColor: getRandomColor(),
    colorProgress: 1,
  }))
}

function drawLetters() {
  if (!ctx || letters.length === 0 || !canvasRef.value) return
  const { width, height } = canvasRef.value.getBoundingClientRect()
  ctx.clearRect(0, 0, width, height)
  ctx.font = `${fontSize}px monospace`
  ctx.textBaseline = 'top'

  letters.forEach((letter, index) => {
    const x = (index % grid.columns) * charWidth
    const y = Math.floor(index / grid.columns) * charHeight
    ctx.fillStyle = letter.color
    ctx.fillText(letter.char, x, y)
  })
}

function updateLetters() {
  if (!letters || letters.length === 0) return
  const updateCount = Math.max(1, Math.floor(letters.length * 0.05))

  for (let i = 0; i < updateCount; i++) {
    const index = Math.floor(Math.random() * letters.length)
    if (!letters[index]) continue

    letters[index].char = getRandomChar()
    letters[index].targetColor = getRandomColor()

    if (!props.smooth) {
      letters[index].color = letters[index].targetColor
      letters[index].colorProgress = 1
    } else {
      letters[index].colorProgress = 0
    }
  }
}

function handleSmoothTransitions() {
  let needsRedraw = false
  letters.forEach(letter => {
    if (letter.colorProgress < 1) {
      letter.colorProgress += 0.05
      if (letter.colorProgress > 1) letter.colorProgress = 1

      const startRgb = hexToRgb(letter.color)
      const endRgb = hexToRgb(letter.targetColor)
      if (startRgb && endRgb) {
        letter.color = interpolateColor(startRgb, endRgb, letter.colorProgress)
        needsRedraw = true
      }
    }
  })

  if (needsRedraw) drawLetters()
}

function animate() {
  const now = Date.now()
  if (now - lastGlitchTime >= props.glitchSpeed) {
    updateLetters()
    drawLetters()
    lastGlitchTime = now
  }

  if (props.smooth) handleSmoothTransitions()

  animationId = requestAnimationFrame(animate)
}

function resizeCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return
  const parent = canvas.parentElement
  if (!parent) return

  const dpr = window.devicePixelRatio || 1
  const rect = parent.getBoundingClientRect()

  canvas.width = rect.width * dpr
  canvas.height = rect.height * dpr
  canvas.style.width = `${rect.width}px`
  canvas.style.height = `${rect.height}px`

  if (ctx) ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

  const { columns, rows } = calculateGrid(rect.width, rect.height)
  initializeLetters(columns, rows)
  drawLetters()
}

onMounted(() => {
  const canvas = canvasRef.value
  if (!canvas) return
  ctx = canvas.getContext('2d')
  resizeCanvas()
  animate()

  let resizeTimeout
  const handleResize = () => {
    clearTimeout(resizeTimeout)
    resizeTimeout = setTimeout(() => {
      cancelAnimationFrame(animationId)
      resizeCanvas()
      animate()
    }, 100)
  }
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
})
</script>

<template>
  <div class="letter-glitch-container">
    <canvas ref="canvasRef" class="glitch-canvas" />
    <div v-if="outerVignette" class="vignette outer" />
    <div v-if="centerVignette" class="vignette center" />
  </div>
</template>

<style scoped>
.letter-glitch-container {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  background: #000;
  overflow: hidden;
}

.glitch-canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.vignette {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.vignette.outer {
  background: radial-gradient(circle, rgba(0,0,0,0) 60%, rgba(0,0,0,1) 100%);
}

.vignette.center {
  background: radial-gradient(circle, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 60%);
}
</style>
