<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import gsap from 'gsap'

const props = defineProps({
  text: { type: String, required: true },
  delay: { type: Number, default: 0 },
  animateByWord: { type: Boolean, default: true },
})

const containerRef = ref(null)
const isVisible = ref(false)
let observer = null

const words = computed(() => props.text.split(' '))

function animateWords() {
  if (!containerRef.value) return
  const spans = containerRef.value.querySelectorAll('.blur-word')
  gsap.fromTo(
    spans,
    { filter: 'blur(10px)', opacity: 0, y: 50 },
    {
      filter: 'blur(0px)',
      opacity: 1,
      y: 0,
      duration: 0.7,
      stagger: 0.1,
      delay: props.delay,
      ease: 'power3.out',
    }
  )
}

onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && !isVisible.value) {
        isVisible.value = true
        animateWords()
        observer.disconnect()
      }
    },
    { threshold: 0.1 }
  )
  if (containerRef.value) {
    observer.observe(containerRef.value)
  }
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<template>
  <p ref="containerRef" class="blur-text-container">
    <span
      v-for="(word, i) in words"
      :key="i"
      class="blur-word"
    >{{ word }}</span>
  </p>
</template>

<style scoped>
.blur-text-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  row-gap: 0.1em;
}

.blur-word {
  display: inline-block;
  margin-right: 0.28em;
  will-change: filter, opacity, transform;
}
</style>
