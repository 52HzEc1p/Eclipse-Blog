<script setup>
defineProps({
  text: { type: String, required: true },
  disabled: { type: Boolean, default: false },
  speed: { type: Number, default: 2 },
  color: { type: String, default: '#8a8a9a' },
  shineColor: { type: String, default: '#ffffff' },
  spread: { type: Number, default: 120 },
  direction: { type: String, default: 'left' },
})
</script>

<template>
  <span
    class="shiny-text"
    :class="{ disabled }"
    :style="{
      '--shine-speed': `${speed}s`,
      '--shine-spread': `${spread}deg`,
      '--shine-color': color,
      '--shine-highlight': shineColor,
      '--shine-direction': direction === 'left' ? 'normal' : 'reverse',
    }"
  >{{ text }}</span>
</template>

<style scoped>
.shiny-text {
  display: inline-block;
  background-image: linear-gradient(
    var(--shine-spread, 120deg),
    var(--shine-color, #8a8a9a) 0%,
    var(--shine-color, #8a8a9a) 35%,
    var(--shine-highlight, #ffffff) 50%,
    var(--shine-color, #8a8a9a) 65%,
    var(--shine-color, #8a8a9a) 100%
  );
  background-size: 200% auto;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shine-move var(--shine-speed, 2s) linear infinite var(--shine-direction, normal);
}

.shiny-text.disabled {
  animation: none;
}

@keyframes shine-move {
  0% {
    background-position: 150% center;
  }
  100% {
    background-position: -50% center;
  }
}
</style>
