<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Renderer, Program, Triangle, Mesh } from 'ogl'

const props = defineProps({
  raysOrigin: { type: String, default: 'top-center' },
  raysColor: { type: String, default: '#ffffff' },
  raysSpeed: { type: Number, default: 1 },
  lightSpread: { type: Number, default: 1 },
  rayLength: { type: Number, default: 2 },
  pulsating: { type: Boolean, default: false },
  fadeDistance: { type: Number, default: 1.0 },
  saturation: { type: Number, default: 1.0 },
  followMouse: { type: Boolean, default: true },
  mouseInfluence: { type: Number, default: 0.1 },
  noiseAmount: { type: Number, default: 0.0 },
  distortion: { type: Number, default: 0.0 },
})

const containerRef = ref(null)
let renderer = null
let uniforms = null
let animationId = null
let mouse = { x: 0.5, y: 0.5 }
let smoothMouse = { x: 0.5, y: 0.5 }

function hexToRgb(hex) {
  const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return m
    ? [parseInt(m[1], 16) / 255, parseInt(m[2], 16) / 255, parseInt(m[3], 16) / 255]
    : [1, 1, 1]
}

function getAnchorAndDir(origin, w, h) {
  const outside = 0.2
  switch (origin) {
    case 'top-left': return { anchor: [0, -outside * h], dir: [0, 1] }
    case 'top-right': return { anchor: [w, -outside * h], dir: [0, 1] }
    case 'left': return { anchor: [-outside * w, 0.5 * h], dir: [1, 0] }
    case 'right': return { anchor: [(1 + outside) * w, 0.5 * h], dir: [-1, 0] }
    case 'bottom-left': return { anchor: [0, (1 + outside) * h], dir: [0, -1] }
    case 'bottom-center': return { anchor: [0.5 * w, (1 + outside) * h], dir: [0, -1] }
    case 'bottom-right': return { anchor: [w, (1 + outside) * h], dir: [0, -1] }
    default: return { anchor: [0.5 * w, -outside * h], dir: [0, 1] }
  }
}

const VERT = `
attribute vec2 position;
varying vec2 vUv;
void main() {
  vUv = position * 0.5 + 0.5;
  gl_Position = vec4(position, 0.0, 1.0);
}`

const FRAG = `precision highp float;

uniform float iTime;
uniform vec2  iResolution;
uniform vec2  rayPos;
uniform vec2  rayDir;
uniform vec3  raysColor;
uniform float raysSpeed;
uniform float lightSpread;
uniform float rayLength;
uniform float pulsating;
uniform float fadeDistance;
uniform float saturation;
uniform vec2  mousePos;
uniform float mouseInfluence;
uniform float noiseAmount;
uniform float distortion;

varying vec2 vUv;

float noise(vec2 st) {
  return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
}

float rayStrength(vec2 raySource, vec2 rayRefDirection, vec2 coord,
                  float seedA, float seedB, float speed) {
  vec2 sourceToCoord = coord - raySource;
  vec2 dirNorm = normalize(sourceToCoord);
  float cosAngle = dot(dirNorm, rayRefDirection);
  float distortedAngle = cosAngle + distortion * sin(iTime * 2.0 + length(sourceToCoord) * 0.01) * 0.2;
  float spreadFactor = pow(max(distortedAngle, 0.0), 1.0 / max(lightSpread, 0.001));
  float distance = length(sourceToCoord);
  float maxDistance = iResolution.x * rayLength;
  float lengthFalloff = clamp((maxDistance - distance) / maxDistance, 0.0, 1.0);
  float fadeFalloff = clamp((iResolution.x * fadeDistance - distance) / (iResolution.x * fadeDistance), 0.5, 1.0);
  float pulse = pulsating > 0.5 ? (0.8 + 0.2 * sin(iTime * speed * 3.0)) : 1.0;
  float baseStrength = clamp(
    (0.45 + 0.15 * sin(distortedAngle * seedA + iTime * speed)) +
    (0.3 + 0.2 * cos(-distortedAngle * seedB + iTime * speed)),
    0.0, 1.0
  );
  return baseStrength * lengthFalloff * fadeFalloff * spreadFactor * pulse;
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 coord = vec2(fragCoord.x, iResolution.y - fragCoord.y);
  vec2 finalRayDir = rayDir;
  if (mouseInfluence > 0.0) {
    vec2 mouseScreenPos = mousePos * iResolution.xy;
    vec2 mouseDirection = normalize(mouseScreenPos - rayPos);
    finalRayDir = normalize(mix(rayDir, mouseDirection, mouseInfluence));
  }
  vec4 rays1 = vec4(1.0) * rayStrength(rayPos, finalRayDir, coord, 36.2214, 21.11349, 1.5 * raysSpeed);
  vec4 rays2 = vec4(1.0) * rayStrength(rayPos, finalRayDir, coord, 22.3991, 18.0234, 1.1 * raysSpeed);
  fragColor = rays1 * 0.5 + rays2 * 0.4;
  if (noiseAmount > 0.0) {
    float n = noise(coord * 0.01 + iTime * 0.1);
    fragColor.rgb *= (1.0 - noiseAmount + noiseAmount * n);
  }
  float brightness = 1.0 - (coord.y / iResolution.y);
  fragColor.x *= 0.4 + brightness * 0.6;
  fragColor.y *= 0.5 + brightness * 0.5;
  fragColor.z *= 0.6 + brightness * 0.4;
  if (saturation != 1.0) {
    float gray = dot(fragColor.rgb, vec3(0.299, 0.587, 0.114));
    fragColor.rgb = mix(vec3(gray), fragColor.rgb, saturation);
  }
  fragColor.rgb *= raysColor;
  fragColor.rgb *= 1.6;
}

void main() {
  vec4 color;
  mainImage(color, gl_FragCoord.xy);
  gl_FragColor = color;
}`

function initWebGL() {
  if (!containerRef.value) return

  renderer = new Renderer({ dpr: Math.min(window.devicePixelRatio, 2), alpha: true })
  const gl = renderer.gl
  gl.canvas.style.width = '100%'
  gl.canvas.style.height = '100%'

  containerRef.value.innerHTML = ''
  containerRef.value.appendChild(gl.canvas)

  uniforms = {
    iTime: { value: 0 },
    iResolution: { value: [1, 1] },
    rayPos: { value: [0, 0] },
    rayDir: { value: [0, 1] },
    raysColor: { value: hexToRgb(props.raysColor) },
    raysSpeed: { value: props.raysSpeed },
    lightSpread: { value: props.lightSpread },
    rayLength: { value: props.rayLength },
    pulsating: { value: props.pulsating ? 1.0 : 0.0 },
    fadeDistance: { value: props.fadeDistance },
    saturation: { value: props.saturation },
    mousePos: { value: [0.5, 0.5] },
    mouseInfluence: { value: props.mouseInfluence },
    noiseAmount: { value: props.noiseAmount },
    distortion: { value: props.distortion },
  }

  const geometry = new Triangle(gl)
  const program = new Program(gl, { vertex: VERT, fragment: FRAG, uniforms })
  const mesh = new Mesh(gl, { geometry, program })

  function updatePlacement() {
    if (!containerRef.value || !renderer) return
    renderer.dpr = Math.min(window.devicePixelRatio, 2)
    const { clientWidth: wCSS, clientHeight: hCSS } = containerRef.value
    renderer.setSize(wCSS, hCSS)
    const dpr = renderer.dpr
    const w = wCSS * dpr
    const h = hCSS * dpr
    uniforms.iResolution.value = [w, h]
    const { anchor, dir } = getAnchorAndDir(props.raysOrigin, w, h)
    uniforms.rayPos.value = anchor
    uniforms.rayDir.value = dir
  }

  function loop(t) {
    if (!renderer || !uniforms) return
    uniforms.iTime.value = t * 0.001
    if (props.followMouse && props.mouseInfluence > 0) {
      smoothMouse.x = smoothMouse.x * 0.92 + mouse.x * 0.08
      smoothMouse.y = smoothMouse.y * 0.92 + mouse.y * 0.08
      uniforms.mousePos.value = [smoothMouse.x, smoothMouse.y]
    }
    renderer.render({ scene: mesh })
    animationId = requestAnimationFrame(loop)
  }

  window.addEventListener('resize', updatePlacement)
  updatePlacement()
  animationId = requestAnimationFrame(loop)
}

function handleMouseMove(e) {
  if (!containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  mouse.x = (e.clientX - rect.left) / rect.width
  mouse.y = (e.clientY - rect.top) / rect.height
}

onMounted(() => {
  initWebGL()
  if (props.followMouse) window.addEventListener('mousemove', handleMouseMove)
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  window.removeEventListener('mousemove', handleMouseMove)
  if (renderer) {
    const gl = renderer.gl
    gl.getExtension('WEBGL_lose_context')?.loseContext()
  }
  renderer = null
  uniforms = null
})
</script>

<template>
  <div ref="containerRef" class="light-rays-container"></div>
</template>

<style scoped>
.light-rays-container {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}
</style>
