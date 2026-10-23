<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  enableMouseFollow: { type: Boolean, default: true },
  particleDensity: { type: Number, default: 0.08 },
  maxParticles: { type: Number, default: 100 },
  speedMultiplier: { type: Number, default: 1 },
  connectionDistance: { type: Number, default: 150 },
  hue: { type: Number, default: 235 },
  hueRange: { type: Number, default: 30 },
  fixed: { type: Boolean, default: false },
})

const canvasRef = ref(null)
let animationId = null
let particles = []
let mouse = { x: -1000, y: -1000 }

class Particle {
  constructor(canvas, speedMult) {
    this.canvas = canvas
    this.speedMult = speedMult
    this.reset()
  }

  reset() {
    this.x = Math.random() * this.canvas.width
    this.y = Math.random() * this.canvas.height
    this.size = Math.random() * 2 + 0.5
    const baseSpeed = 0.3 * this.speedMult
    this.speedX = (Math.random() - 0.5) * baseSpeed * 2
    this.speedY = (Math.random() - 0.5) * baseSpeed * 2
    // 随机方向偏移，让漂浮更不规则
    this.driftAngle = Math.random() * Math.PI * 2
    this.driftSpeed = Math.random() * 0.15 * this.speedMult
    this.driftTimer = Math.random() * 200
    this.opacity = Math.random() * 0.5 + 0.1
    this.fadeSpeed = Math.random() * 0.005 + 0.002
    this.fadeDir = 1
    this.hue = props.hue + Math.random() * props.hueRange
  }

  update() {
    // 随机漂移
    this.driftTimer++
    if (this.driftTimer > 200) {
      this.driftAngle = Math.random() * Math.PI * 2
      this.driftSpeed = Math.random() * 0.15 * this.speedMult
      this.driftTimer = 0
    }

    this.x += this.speedX + Math.cos(this.driftAngle) * this.driftSpeed
    this.y += this.speedY + Math.sin(this.driftAngle) * this.driftSpeed

    // 微光闪烁
    this.opacity += this.fadeSpeed * this.fadeDir
    if (this.opacity >= 0.6) this.fadeDir = -1
    if (this.opacity <= 0.05) this.fadeDir = 1

    // 鼠标交互
    if (props.enableMouseFollow) {
      const dx = this.x - mouse.x
      const dy = this.y - mouse.y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < 120) {
        const force = (120 - dist) / 120 * 0.5
        this.x += (dx / dist) * force
        this.y += (dy / dist) * force
      }
    }

    // 边界循环
    if (this.x < -10) this.x = this.canvas.width + 10
    if (this.x > this.canvas.width + 10) this.x = -10
    if (this.y < -10) this.y = this.canvas.height + 10
    if (this.y > this.canvas.height + 10) this.y = -10
  }

  draw(ctx) {
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fillStyle = `hsla(${this.hue}, 70%, 70%, ${this.opacity})`
    ctx.fill()

    if (this.size > 1.2) {
      ctx.beginPath()
      ctx.arc(this.x, this.y, this.size * 3, 0, Math.PI * 2)
      ctx.fillStyle = `hsla(${this.hue}, 70%, 70%, ${this.opacity * 0.15})`
      ctx.fill()
    }
  }
}

function initCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  const dpr = window.devicePixelRatio || 1

  function resize() {
    canvas.width = window.innerWidth * dpr
    canvas.height = window.innerHeight * dpr
    canvas.style.width = window.innerWidth + 'px'
    canvas.style.height = window.innerHeight + 'px'
    ctx.scale(dpr, dpr)
  }

  resize()
  window.addEventListener('resize', resize)

  const count = Math.min(Math.floor(window.innerWidth * props.particleDensity), props.maxParticles)
  particles = Array.from({ length: count }, () => new Particle(canvas, props.speedMultiplier))

  function drawConnections(ctx) {
    if (props.connectionDistance === 0) return
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x
        const dy = particles[i].y - particles[j].y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < props.connectionDistance) {
          const opacity = (1 - dist / props.connectionDistance) * 0.15
          ctx.beginPath()
          ctx.moveTo(particles[i].x, particles[i].y)
          ctx.lineTo(particles[j].x, particles[j].y)
          ctx.strokeStyle = `rgba(99, 102, 241, ${opacity})`
          ctx.lineWidth = 0.5
          ctx.stroke()
        }
      }
    }
  }

  function animate() {
    ctx.clearRect(0, 0, canvas.width / dpr, canvas.height / dpr)

    particles.forEach(p => {
      p.update()
      p.draw(ctx)
    })

    drawConnections(ctx)

    animationId = requestAnimationFrame(animate)
  }

  animate()

  let onMouseMove, onMouseLeave

  if (props.enableMouseFollow) {
    onMouseMove = (e) => {
      mouse.x = e.clientX
      mouse.y = e.clientY
    }
    onMouseLeave = () => {
      mouse.x = -1000
      mouse.y = -1000
    }
    window.addEventListener('mousemove', onMouseMove)
    window.addEventListener('mouseleave', onMouseLeave)
  }

  onBeforeUnmount(() => {
    cancelAnimationFrame(animationId)
    window.removeEventListener('resize', resize)
    if (props.enableMouseFollow) {
      window.removeEventListener('mousemove', onMouseMove)
      window.removeEventListener('mouseleave', onMouseLeave)
    }
  })
}

onMounted(initCanvas)
</script>

<template>
  <canvas ref="canvasRef" class="particle-canvas" :class="{ fixed: fixed }"></canvas>
</template>

<style scoped>
.particle-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.particle-canvas.fixed {
  position: fixed;
}
</style>
