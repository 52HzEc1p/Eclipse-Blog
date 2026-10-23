<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Renderer, Program, Mesh, Triangle } from 'ogl'

const props = defineProps({
  speed: { type: Number, default: 0.3 },
  innerLineCount: { type: Number, default: 32 },
  outerLineCount: { type: Number, default: 36 },
  warpIntensity: { type: Number, default: 1.0 },
  rotation: { type: Number, default: -45 },
  edgeFadeWidth: { type: Number, default: 0.0 },
  colorCycleSpeed: { type: Number, default: 1.0 },
  brightness: { type: Number, default: 0.2 },
  color1: { type: String, default: '#22d3ee' },
  color2: { type: String, default: '#6366f1' },
  color3: { type: String, default: '#22d3ee' },
  enableMouseInteraction: { type: Boolean, default: true },
  mouseInfluence: { type: Number, default: 2.0 },
})

const containerRef = ref(null)
let renderer = null
let animationId = null
let currentMouse = [0.5, 0.5]
let targetMouse = [0.5, 0.5]

function hexToVec3(hex) {
  const h = hex.replace('#', '')
  return [
    parseInt(h.slice(0, 2), 16) / 255,
    parseInt(h.slice(2, 4), 16) / 255,
    parseInt(h.slice(4, 6), 16) / 255,
  ]
}

const VERT = `
attribute vec2 uv;
attribute vec2 position;
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = vec4(position, 0, 1);
}`

const FRAG = `precision highp float;

uniform float uTime;
uniform vec3 uResolution;
uniform float uSpeed;
uniform float uInnerLines;
uniform float uOuterLines;
uniform float uWarpIntensity;
uniform float uRotation;
uniform float uEdgeFadeWidth;
uniform float uColorCycleSpeed;
uniform float uBrightness;
uniform vec3 uColor1;
uniform vec3 uColor2;
uniform vec3 uColor3;
uniform vec2 uMouse;
uniform float uMouseInfluence;
uniform bool uEnableMouse;

#define HALF_PI 1.5707963

float hashF(float n) {
  return fract(sin(n * 127.1) * 43758.5453123);
}

float smoothNoise(float x) {
  float i = floor(x);
  float f = fract(x);
  float u = f * f * (3.0 - 2.0 * f);
  return mix(hashF(i), hashF(i + 1.0), u);
}

float displaceA(float coord, float t) {
  float result = sin(coord * 2.123) * 0.2;
  result += sin(coord * 3.234 + t * 4.345) * 0.1;
  result += sin(coord * 0.589 + t * 0.934) * 0.5;
  return result;
}

float displaceB(float coord, float t) {
  float result = sin(coord * 1.345) * 0.3;
  result += sin(coord * 2.734 + t * 3.345) * 0.2;
  result += sin(coord * 0.189 + t * 0.934) * 0.3;
  return result;
}

vec2 rotate2D(vec2 p, float angle) {
  float c = cos(angle);
  float s = sin(angle);
  return vec2(p.x * c - p.y * s, p.x * s + p.y * c);
}

void main() {
  vec2 coords = gl_FragCoord.xy / uResolution.xy;
  coords = coords * 2.0 - 1.0;
  coords = rotate2D(coords, uRotation);

  float halfT = uTime * uSpeed * 0.5;
  float fullT = uTime * uSpeed;

  float mouseWarp = 0.0;
  if (uEnableMouse) {
    vec2 mPos = rotate2D(uMouse * 2.0 - 1.0, uRotation);
    float mDist = length(coords - mPos);
    mouseWarp = uMouseInfluence * exp(-mDist * mDist * 4.0);
  }

  float warpAx = coords.x + displaceA(coords.y, halfT) * uWarpIntensity + mouseWarp;
  float warpAy = coords.y - displaceA(coords.x * cos(fullT) * 1.235, halfT) * uWarpIntensity;
  float warpBx = coords.x + displaceB(coords.y, halfT) * uWarpIntensity + mouseWarp;
  float warpBy = coords.y - displaceB(coords.x * sin(fullT) * 1.235, halfT) * uWarpIntensity;

  vec2 fieldA = vec2(warpAx, warpAy);
  vec2 fieldB = vec2(warpBx, warpBy);
  vec2 blended = mix(fieldA, fieldB, mix(fieldA, fieldB, 0.5));

  float fadeTop = smoothstep(uEdgeFadeWidth, uEdgeFadeWidth + 0.4, blended.y);
  float fadeBottom = smoothstep(-uEdgeFadeWidth, -(uEdgeFadeWidth + 0.4), blended.y);
  float vMask = 1.0 - max(fadeTop, fadeBottom);

  float tileCount = mix(uOuterLines, uInnerLines, vMask);
  float scaledY = blended.y * tileCount;
  float nY = smoothNoise(abs(scaledY));

  float ridge = pow(
    step(abs(nY - blended.x) * 2.0, HALF_PI) * cos(2.0 * (nY - blended.x)),
    5.0
  );

  float lines = 0.0;
  for (float i = 1.0; i < 3.0; i += 1.0) {
    lines += pow(max(fract(scaledY), fract(-scaledY)), i * 2.0);
  }

  float pattern = vMask * lines;

  float cycleT = fullT * uColorCycleSpeed;
  float rChannel = (pattern + lines * ridge) * (cos(blended.y + cycleT * 0.234) * 0.5 + 1.0);
  float gChannel = (pattern + vMask * ridge) * (sin(blended.x + cycleT * 1.745) * 0.5 + 1.0);
  float bChannel = (pattern + lines * ridge) * (cos(blended.x + cycleT * 0.534) * 0.5 + 1.0);

  vec3 col = (rChannel * uColor1 + gChannel * uColor2 + bChannel * uColor3) * uBrightness;
  float alpha = clamp(length(col), 0.0, 1.0);

  gl_FragColor = vec4(col, alpha);
}`

function initWebGL() {
  if (!containerRef.value) return
  const container = containerRef.value

  renderer = new Renderer({ alpha: true, premultipliedAlpha: false })
  const gl = renderer.gl
  gl.clearColor(0, 0, 0, 0)

  const geometry = new Triangle(gl)
  const rotationRad = (props.rotation * Math.PI) / 180

  const program = new Program(gl, {
    vertex: VERT,
    fragment: FRAG,
    uniforms: {
      uTime: { value: 0 },
      uResolution: { value: [gl.canvas.width, gl.canvas.height, gl.canvas.width / gl.canvas.height] },
      uSpeed: { value: props.speed },
      uInnerLines: { value: props.innerLineCount },
      uOuterLines: { value: props.outerLineCount },
      uWarpIntensity: { value: props.warpIntensity },
      uRotation: { value: rotationRad },
      uEdgeFadeWidth: { value: props.edgeFadeWidth },
      uColorCycleSpeed: { value: props.colorCycleSpeed },
      uBrightness: { value: props.brightness },
      uColor1: { value: hexToVec3(props.color1) },
      uColor2: { value: hexToVec3(props.color2) },
      uColor3: { value: hexToVec3(props.color3) },
      uMouse: { value: new Float32Array([0.5, 0.5]) },
      uMouseInfluence: { value: props.mouseInfluence },
      uEnableMouse: { value: props.enableMouseInteraction },
    },
  })

  const mesh = new Mesh(gl, { geometry, program })
  container.appendChild(gl.canvas)

  function resize() {
    renderer.setSize(container.offsetWidth, container.offsetHeight)
    program.uniforms.uResolution.value = [gl.canvas.width, gl.canvas.height, gl.canvas.width / gl.canvas.height]
  }
  window.addEventListener('resize', resize)
  resize()

  function handleMouseMove(e) {
    const rect = gl.canvas.getBoundingClientRect()
    targetMouse = [
      (e.clientX - rect.left) / rect.width,
      1.0 - (e.clientY - rect.top) / rect.height,
    ]
  }
  function handleMouseLeave() {
    targetMouse = [0.5, 0.5]
  }

  if (props.enableMouseInteraction) {
    gl.canvas.addEventListener('mousemove', handleMouseMove)
    gl.canvas.addEventListener('mouseleave', handleMouseLeave)
  }

  function update(time) {
    animationId = requestAnimationFrame(update)
    program.uniforms.uTime.value = time * 0.001
    if (props.enableMouseInteraction) {
      currentMouse[0] += 0.05 * (targetMouse[0] - currentMouse[0])
      currentMouse[1] += 0.05 * (targetMouse[1] - currentMouse[1])
      program.uniforms.uMouse.value[0] = currentMouse[0]
      program.uniforms.uMouse.value[1] = currentMouse[1]
    }
    renderer.render({ scene: mesh })
  }
  animationId = requestAnimationFrame(update)
}

onMounted(() => initWebGL())

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (renderer) {
    renderer.gl.getExtension('WEBGL_lose_context')?.loseContext()
  }
  renderer = null
})
</script>

<template>
  <div ref="containerRef" class="line-waves-container"></div>
</template>

<style scoped>
.line-waves-container {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}
</style>
