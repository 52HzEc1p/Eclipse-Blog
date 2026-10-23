<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Renderer, Program, Mesh, Triangle, Texture } from 'ogl'

const props = defineProps({
  eyeColor: { type: String, default: '#FF6F37' },
  intensity: { type: Number, default: 1.5 },
  pupilSize: { type: Number, default: 0.6 },
  irisWidth: { type: Number, default: 0.25 },
  glowIntensity: { type: Number, default: 0.35 },
  scale: { type: Number, default: 0.8 },
  noiseScale: { type: Number, default: 1.0 },
  pupilFollow: { type: Number, default: 1.0 },
  flameSpeed: { type: Number, default: 1.0 },
  backgroundColor: { type: String, default: '#000000' },
  openProgress: { type: Number, default: 1.0 },
  tremorIntensity: { type: Number, default: 0 },
  tremorSpeed: { type: Number, default: 1.0 },
})

const containerRef = ref(null)
let animationFrameId = null
let cleanupFn = null

function hexToVec3(hex) {
  const h = hex.replace('#', '')
  return [
    parseInt(h.slice(0, 2), 16) / 255,
    parseInt(h.slice(2, 4), 16) / 255,
    parseInt(h.slice(4, 6), 16) / 255,
  ]
}

function generateNoiseTexture(size = 256) {
  const data = new Uint8Array(size * size * 4)
  function hash(x, y, s) {
    let n = x * 374761393 + y * 668265263 + s * 1274126177
    n = Math.imul(n ^ (n >>> 13), 1274126177)
    return ((n ^ (n >>> 16)) >>> 0) / 4294967296
  }
  function noise(px, py, freq, seed) {
    const fx = (px / size) * freq
    const fy = (py / size) * freq
    const ix = Math.floor(fx)
    const iy = Math.floor(fy)
    const tx = fx - ix
    const ty = fy - iy
    const w = freq | 0
    const v00 = hash(((ix % w) + w) % w, ((iy % w) + w) % w, seed)
    const v10 = hash((((ix + 1) % w) + w) % w, ((iy % w) + w) % w, seed)
    const v01 = hash(((ix % w) + w) % w, (((iy + 1) % w) + w) % w, seed)
    const v11 = hash((((ix + 1) % w) + w) % w, (((iy + 1) % w) + w) % w, seed)
    return v00 * (1 - tx) * (1 - ty) + v10 * tx * (1 - ty) + v01 * (1 - tx) * ty + v11 * tx * ty
  }
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      let v = 0
      let amp = 0.4
      let totalAmp = 0
      for (let o = 0; o < 8; o++) {
        const f = 32 * (1 << o)
        v += amp * noise(x, y, f, o * 31)
        totalAmp += amp
        amp *= 0.65
      }
      v /= totalAmp
      v = (v - 0.5) * 2.2 + 0.5
      v = Math.max(0, Math.min(1, v))
      const val = Math.round(v * 255)
      const i = (y * size + x) * 4
      data[i] = val
      data[i + 1] = val
      data[i + 2] = val
      data[i + 3] = 255
    }
  }
  return data
}

const vertexShader = `
attribute vec2 uv;
attribute vec2 position;
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = vec4(position, 0, 1);
}
`

const fragmentShader = `
precision highp float;

uniform float uTime;
uniform vec3 uResolution;
uniform sampler2D uNoiseTexture;
uniform float uPupilSize;
uniform float uIrisWidth;
uniform float uGlowIntensity;
uniform float uIntensity;
uniform float uScale;
uniform float uNoiseScale;
uniform vec2 uMouse;
uniform float uPupilFollow;
uniform float uFlameSpeed;
uniform float uOpenProgress;
uniform float uTremor;
uniform vec3 uEyeColor;
uniform vec3 uBgColor;

void main() {
  vec2 uv = (gl_FragCoord.xy * 2.0 - uResolution.xy) / uResolution.y;
  uv /= uScale;
  float openAmount = smoothstep(0.0, 1.0, uOpenProgress);

  uv += vec2(
    sin(uTime * 41.0) * 0.004 + sin(uTime * 87.0) * 0.002,
    sin(uTime * 53.0) * 0.010 + sin(uTime * 113.0) * 0.004
  ) * uTremor;

  float ft = uTime * uFlameSpeed;

  float polarRadius = length(uv) * 2.0;
  float polarAngle = (2.0 * atan(uv.x, uv.y)) / 6.28 * 0.3;
  vec2 polarUv = vec2(polarRadius, polarAngle);

  vec4 noiseA = texture2D(uNoiseTexture, polarUv * vec2(0.2, 7.0) * uNoiseScale + vec2(-ft * 0.1, 0.0));
  vec4 noiseB = texture2D(uNoiseTexture, polarUv * vec2(0.3, 4.0) * uNoiseScale + vec2(-ft * 0.2, 0.0));
  vec4 noiseC = texture2D(uNoiseTexture, polarUv * vec2(0.1, 5.0) * uNoiseScale + vec2(-ft * 0.1, 0.0));

  float distanceMask = 1.0 - length(uv);

  // Inner ring
  float innerRing = clamp(-1.0 * ((distanceMask - 0.7) / uIrisWidth), 0.0, 1.0);
  innerRing = (innerRing * distanceMask - 0.2) / 0.28;
  innerRing += noiseA.r - 0.5;
  innerRing *= 1.3;
  innerRing = clamp(innerRing, 0.0, 1.0);

  float outerRing = clamp(-1.0 * ((distanceMask - 0.5) / 0.2), 0.0, 1.0);
  outerRing = (outerRing * distanceMask - 0.1) / 0.38;
  outerRing += noiseC.r - 0.5;
  outerRing *= 1.3;
  outerRing = clamp(outerRing, 0.0, 1.0);

  innerRing += outerRing;

  // Inner eye
  float innerEye = distanceMask - 0.1 * 2.0;
  innerEye *= noiseB.r * 2.0;

  // Pupil with cursor tracking
  vec2 pupilOffset = uMouse * uPupilFollow * 0.12;
  vec2 pupilUv = uv - pupilOffset;
  float pupil = 1.0 - length(pupilUv * vec2(9.0, 2.3));
  pupil *= uPupilSize;
  pupil = clamp(pupil, 0.0, 1.0);
  pupil /= 0.35;

  vec2 outerUv = uv / 1.34;
  float outerPolarRadius = length(outerUv) * 2.0;
  float outerPolarAngle = (2.0 * atan(outerUv.x, outerUv.y)) / 6.28 * 0.3;
  vec2 outerPolarUv = vec2(outerPolarRadius, outerPolarAngle);
  vec4 outerNoise = texture2D(uNoiseTexture, outerPolarUv * vec2(0.1, 5.0) * uNoiseScale + vec2(-ft * 0.1, 0.0));
  float outerDistanceMask = 1.0 - length(outerUv);

  // Outer eye
  float outerEyeGlow = 1.0 - length(outerUv * vec2(0.5, 1.5));
  outerEyeGlow = clamp(outerEyeGlow + 0.5, 0.0, 1.0);
  outerEyeGlow += outerNoise.r - 0.5;
  float outerBgGlow = outerEyeGlow;
  outerEyeGlow = pow(outerEyeGlow, 2.0);
  outerEyeGlow += outerDistanceMask;
  outerEyeGlow *= uGlowIntensity;
  outerEyeGlow = clamp(outerEyeGlow, 0.0, 1.0);
  outerEyeGlow *= pow(1.0 - outerDistanceMask, 2.0) * 2.5;

  // Outer eye bg glow
  outerBgGlow += outerDistanceMask;
  outerBgGlow = pow(outerBgGlow, 0.5);
  outerBgGlow *= 0.2;

  vec3 color = uEyeColor * uIntensity * clamp(max(innerRing + innerEye, outerEyeGlow + outerBgGlow * 0.9) - pupil, 0.0, 3.0);
  color += uBgColor;

  float horizontalFalloff = pow(clamp(1.0 - abs(uv.x) / 5.4, 0.0, 1.0), 0.58);
  float lidCurve = 0.12 + horizontalFalloff * 0.88;
  float aperture = mix(0.012, 1.23, openAmount) * lidCurve;
  float lidSoftness = mix(0.01, 0.11, openAmount);
  float revealMask = 1.0 - smoothstep(aperture - lidSoftness, aperture + lidSoftness, abs(uv.y));
  revealMask *= smoothstep(0.03, 0.22, openAmount);

  float lidEdge = 1.0 - smoothstep(0.0, lidSoftness * 2.6, abs(abs(uv.y) - aperture));
  lidEdge *= smoothstep(0.06, 0.55, openAmount) * (1.0 - openAmount * 0.35);
  float lidShadow = smoothstep(aperture - lidSoftness * 5.5, aperture + lidSoftness * 0.8, abs(uv.y));
  color *= 1.0 - lidShadow * revealMask * 0.2;
  color += uEyeColor * lidEdge * 0.26;
  color = mix(uBgColor, color, revealMask);

  gl_FragColor = vec4(color, 1.0);
}
`

function initWebGL() {
  if (!containerRef.value) return
  const container = containerRef.value
  const renderer = new Renderer({ alpha: true, premultipliedAlpha: false })
  const gl = renderer.gl
  gl.clearColor(0, 0, 0, 0)

  const noiseData = generateNoiseTexture(256)
  const noiseTexture = new Texture(gl, {
    image: noiseData,
    width: 256,
    height: 256,
    generateMipmaps: false,
    flipY: false,
  })
  noiseTexture.minFilter = gl.LINEAR
  noiseTexture.magFilter = gl.LINEAR
  noiseTexture.wrapS = gl.REPEAT
  noiseTexture.wrapT = gl.REPEAT

  const mouse = { x: 0, y: 0, tx: 0, ty: 0 }

  function onMouseMove(e) {
    const rect = container.getBoundingClientRect()
    mouse.tx = ((e.clientX - rect.left) / rect.width) * 2 - 1
    mouse.ty = -(((e.clientY - rect.top) / rect.height) * 2 - 1)
  }
  function onMouseLeave() {
    mouse.tx = 0
    mouse.ty = 0
  }

  container.addEventListener('mousemove', onMouseMove)
  container.addEventListener('mouseleave', onMouseLeave)

  let program
  function resize() {
    renderer.setSize(container.offsetWidth, container.offsetHeight)
    if (program) {
      program.uniforms.uResolution.value = [gl.canvas.width, gl.canvas.height, gl.canvas.width / gl.canvas.height]
    }
  }
  window.addEventListener('resize', resize)
  resize()

  const geometry = new Triangle(gl)
  program = new Program(gl, {
    vertex: vertexShader,
    fragment: fragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uResolution: { value: [gl.canvas.width, gl.canvas.height, gl.canvas.width / gl.canvas.height] },
      uNoiseTexture: { value: noiseTexture },
      uPupilSize: { value: props.pupilSize },
      uIrisWidth: { value: props.irisWidth },
      uGlowIntensity: { value: props.glowIntensity },
      uIntensity: { value: props.intensity },
      uScale: { value: props.scale },
      uNoiseScale: { value: props.noiseScale },
      uMouse: { value: [0, 0] },
      uPupilFollow: { value: props.pupilFollow },
      uFlameSpeed: { value: props.flameSpeed },
      uOpenProgress: { value: props.openProgress },
      uTremor: { value: 0 },
      uEyeColor: { value: hexToVec3(props.eyeColor) },
      uBgColor: { value: hexToVec3(props.backgroundColor) },
    },
  })

  const mesh = new Mesh(gl, { geometry, program })
  container.appendChild(gl.canvas)

  function update(time) {
    animationFrameId = requestAnimationFrame(update)
    const elapsed = time * 0.001
    const tremorWindow = Math.max(0, Math.sin(elapsed * props.tremorSpeed * 1.55) - 0.88) / 0.12
    const tremor = props.openProgress > 0.98 ? tremorWindow * tremorWindow * props.tremorIntensity : 0
    mouse.x += (mouse.tx - mouse.x) * 0.05
    mouse.y += (mouse.ty - mouse.y) * 0.05
    program.uniforms.uMouse.value = [mouse.x, mouse.y]
    program.uniforms.uTime.value = elapsed
    program.uniforms.uOpenProgress.value = props.openProgress
    program.uniforms.uTremor.value = tremor
    renderer.render({ scene: mesh })
  }
  animationFrameId = requestAnimationFrame(update)

  cleanupFn = () => {
    cancelAnimationFrame(animationFrameId)
    window.removeEventListener('resize', resize)
    container.removeEventListener('mousemove', onMouseMove)
    container.removeEventListener('mouseleave', onMouseLeave)
    if (gl.canvas.parentNode) container.removeChild(gl.canvas)
    gl.getExtension('WEBGL_lose_context')?.loseContext()
  }
}

onMounted(() => {
  initWebGL()
})

onUnmounted(() => {
  cleanupFn?.()
})
</script>

<template>
  <div ref="containerRef" class="evil-eye-container" />
</template>

<style scoped>
.evil-eye-container {
  width: 100%;
  height: 100%;
  position: absolute;
  inset: 0;
  z-index: 0;
}
</style>
