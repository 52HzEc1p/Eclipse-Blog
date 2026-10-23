<script setup>
import { computed } from 'vue'

const props = defineProps({
  text: { type: String, required: true },
  speed: { type: Number, default: 0.5 },
  enableShadows: { type: Boolean, default: true },
  enableOnHover: { type: Boolean, default: false },
})

const afterDuration = computed(() => `${props.speed * 3}s`)
const beforeDuration = computed(() => `${props.speed * 2}s`)
const afterShadow = computed(() => props.enableShadows ? '-5px 0 #ef4444' : 'none')
const beforeShadow = computed(() => props.enableShadows ? '5px 0 #22d3ee' : 'none')
</script>

<template>
  <div
    class="glitch-text"
    :class="{ 'glitch-hover': enableOnHover }"
    :data-text="text"
    :style="{
      '--after-duration': afterDuration,
      '--before-duration': beforeDuration,
      '--after-shadow': afterShadow,
      '--before-shadow': beforeShadow,
    }"
  >{{ text }}</div>
</template>

<style scoped>
.glitch-text {
  --after-duration: 1.5s;
  --before-duration: 1s;
  --after-shadow: -5px 0 #ef4444;
  --before-shadow: 5px 0 #22d3ee;

  position: relative;
  display: inline-block;
  font-family: 'Space Grotesk', 'Noto Sans SC', sans-serif;
  font-size: clamp(48px, 10vw, 100px);
  font-weight: 700;
  letter-spacing: -4px;
  color: #e8e6e3;
  user-select: none;
}

.glitch-text::before,
.glitch-text::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  color: #e8e6e3;
  overflow: hidden;
  clip-path: inset(0 0 0 0);
}

/* Default: always animating */
.glitch-text::before {
  left: -5px;
  text-shadow: var(--before-shadow);
  animation: glitch-before var(--before-duration) infinite linear alternate-reverse;
}

.glitch-text::after {
  left: 5px;
  text-shadow: var(--after-shadow);
  animation: glitch-after var(--after-duration) infinite linear alternate-reverse;
}

/* Hover-only mode */
.glitch-hover::before,
.glitch-hover::after {
  content: '';
  opacity: 0;
  text-shadow: none;
}

.glitch-hover:hover::before {
  content: attr(data-text);
  opacity: 1;
  text-shadow: var(--before-shadow);
  animation: glitch-before var(--before-duration) infinite linear alternate-reverse;
}

.glitch-hover:hover::after {
  content: attr(data-text);
  opacity: 1;
  text-shadow: var(--after-shadow);
  animation: glitch-after var(--after-duration) infinite linear alternate-reverse;
}

@keyframes glitch-before {
  0% { clip-path: inset(20% 0 50% 0); }
  5% { clip-path: inset(10% 0 60% 0); }
  10% { clip-path: inset(15% 0 55% 0); }
  15% { clip-path: inset(25% 0 35% 0); }
  20% { clip-path: inset(30% 0 40% 0); }
  25% { clip-path: inset(40% 0 20% 0); }
  30% { clip-path: inset(10% 0 60% 0); }
  35% { clip-path: inset(15% 0 55% 0); }
  40% { clip-path: inset(25% 0 35% 0); }
  45% { clip-path: inset(30% 0 40% 0); }
  50% { clip-path: inset(20% 0 50% 0); }
  55% { clip-path: inset(10% 0 60% 0); }
  60% { clip-path: inset(15% 0 55% 0); }
  65% { clip-path: inset(25% 0 35% 0); }
  70% { clip-path: inset(30% 0 40% 0); }
  75% { clip-path: inset(40% 0 20% 0); }
  80% { clip-path: inset(20% 0 50% 0); }
  85% { clip-path: inset(10% 0 60% 0); }
  90% { clip-path: inset(15% 0 55% 0); }
  95% { clip-path: inset(25% 0 35% 0); }
  100% { clip-path: inset(30% 0 40% 0); }
}

@keyframes glitch-after {
  0% { clip-path: inset(30% 0 40% 0); }
  5% { clip-path: inset(25% 0 35% 0); }
  10% { clip-path: inset(15% 0 55% 0); }
  15% { clip-path: inset(10% 0 60% 0); }
  20% { clip-path: inset(40% 0 20% 0); }
  25% { clip-path: inset(30% 0 40% 0); }
  30% { clip-path: inset(25% 0 35% 0); }
  35% { clip-path: inset(15% 0 55% 0); }
  40% { clip-path: inset(10% 0 60% 0); }
  45% { clip-path: inset(20% 0 50% 0); }
  50% { clip-path: inset(40% 0 20% 0); }
  55% { clip-path: inset(30% 0 40% 0); }
  60% { clip-path: inset(25% 0 35% 0); }
  65% { clip-path: inset(15% 0 55% 0); }
  70% { clip-path: inset(10% 0 60% 0); }
  75% { clip-path: inset(20% 0 50% 0); }
  80% { clip-path: inset(40% 0 20% 0); }
  85% { clip-path: inset(30% 0 40% 0); }
  90% { clip-path: inset(25% 0 35% 0); }
  95% { clip-path: inset(10% 0 60% 0); }
  100% { clip-path: inset(15% 0 55% 0); }
}
</style>
