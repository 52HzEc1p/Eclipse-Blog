<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'

const props = defineProps({
  lineThickness: { type: Number, default: 1.0 },
  linesColor: { type: String, default: '#2F293A' },
  scanColor: { type: String, default: '#a78bfa' },
  gridScale: { type: Number, default: 0.12 },
  lineStyle: { type: String, default: 'solid' }, // solid | dashed | dotted
  lineJitter: { type: Number, default: 0.2 },
  scanOpacity: { type: Number, default: 0.3 },
  scanDirection: { type: String, default: 'pingpong' },
  scanGlow: { type: Number, default: 0.5 },
  scanSoftness: { type: Number, default: 2.0 },
  scanPhaseTaper: { type: Number, default: 0.9 },
  scanDuration: { type: Number, default: 2.5 },
  scanDelay: { type: Number, default: 3.0 },
  noiseIntensity: { type: Number, default: 0.008 },
  mouseInteraction: { type: Boolean, default: true },
  sensitivity: { type: Number, default: 0.45 },
  snapBackDelay: { type: Number, default: 300 },
})

const containerRef = ref(null)
let renderer = null
let material = null
let animationId = null
let container = null

const vert = `
varying vec2 vUv;
void main(){
  vUv = uv;
  gl_Position = vec4(position.xy, 0.0, 1.0);
}
`

const frag = `
precision highp float;
uniform vec3 iResolution;
uniform float iTime;
uniform vec2 uSkew;
uniform float uTilt;
uniform float uYaw;
uniform float uLineThickness;
uniform vec3 uLinesColor;
uniform vec3 uScanColor;
uniform float uGridScale;
uniform float uLineStyle;
uniform float uLineJitter;
uniform float uScanOpacity;
uniform float uNoise;
uniform float uBloomOpacity;
uniform float uScanGlow;
uniform float uScanSoftness;
uniform float uPhaseTaper;
uniform float uScanDuration;
uniform float uScanDelay;
uniform float uScanDirection;
uniform float uScanStarts[8];
uniform float uScanCount;
varying vec2 vUv;

const int MAX_SCANS = 8;

float smoother01(float a, float b, float x){
  float t = clamp((x - a) / max(1e-5, (b - a)), 0.0, 1.0);
  return t * t * t * (t * (t * 6.0 - 15.0) + 10.0);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord)
{
    vec2 p = (2.0 * fragCoord - iResolution.xy) / iResolution.y;

    vec3 ro = vec3(0.0);
    vec3 rd = normalize(vec3(p, 2.0));

    float cR = cos(uTilt), sR = sin(uTilt);
    rd.xy = mat2(cR, -sR, sR, cR) * rd.xy;

    float cY = cos(uYaw), sY = sin(uYaw);
    rd.xz = mat2(cY, -sY, sY, cY) * rd.xz;

    vec2 skew = clamp(uSkew, vec2(-0.7), vec2(0.7));
    rd.xy += skew * rd.z;

    vec3 color = vec3(0.0);
    float minT = 1e20;
    float gridScale = max(1e-5, uGridScale);
    float fadeStrength = 2.0;
    vec2 gridUV = vec2(0.0);

    float hitIsY = 1.0;
    for (int i = 0; i < 4; i++)
    {
        float isY = float(i < 2);
        float pos = mix(-0.2, 0.2, float(i)) * isY + mix(-0.5, 0.5, float(i - 2)) * (1.0 - isY);
        float num = pos - (isY * ro.y + (1.0 - isY) * ro.x);
        float den = isY * rd.y + (1.0 - isY) * rd.x;
        float t = num / den;
        vec3 h = ro + rd * t;

        float depthBoost = smoothstep(0.0, 3.0, h.z);
        h.xy += skew * 0.15 * depthBoost;

        bool use = t > 0.0 && t < minT;
        gridUV = use ? mix(h.zy, h.xz, isY) / gridScale : gridUV;
        minT = use ? t : minT;
        hitIsY = use ? isY : hitIsY;
    }

    vec3 hit = ro + rd * minT;
    float dist = length(hit - ro);

    float jitterAmt = clamp(uLineJitter, 0.0, 1.0);
    if (jitterAmt > 0.0) {
        vec2 j = vec2(
            sin(gridUV.y * 2.7 + iTime * 1.8),
            cos(gridUV.x * 2.3 - iTime * 1.6)
        ) * (0.15 * jitterAmt);
        gridUV += j;
    }
    float fx = fract(gridUV.x);
    float fy = fract(gridUV.y);
    float ax = min(fx, 1.0 - fx);
    float ay = min(fy, 1.0 - fy);
    float wx = fwidth(gridUV.x);
    float wy = fwidth(gridUV.y);
    float halfPx = max(0.0, uLineThickness) * 0.5;

    float tx = halfPx * wx;
    float ty = halfPx * wy;

    float aax = wx;
    float aay = wy;

    float lineX = 1.0 - smoothstep(tx, tx + aax, ax);
    float lineY = 1.0 - smoothstep(ty, ty + aay, ay);
    if (uLineStyle > 0.5) {
        float dashRepeat = 4.0;
        float dashDuty = 0.5;
        float vy = fract(gridUV.y * dashRepeat);
        float vx = fract(gridUV.x * dashRepeat);
        float dashMaskY = step(vy, dashDuty);
        float dashMaskX = step(vx, dashDuty);
        if (uLineStyle < 1.5) {
            lineX *= dashMaskY;
            lineY *= dashMaskX;
        } else {
            float dotRepeat = 6.0;
            float dotWidth = 0.18;
            float cy = abs(fract(gridUV.y * dotRepeat) - 0.5);
            float cx = abs(fract(gridUV.x * dotRepeat) - 0.5);
            float dotMaskY = 1.0 - smoothstep(dotWidth, dotWidth + fwidth(gridUV.y * dotRepeat), cy);
            float dotMaskX = 1.0 - smoothstep(dotWidth, dotWidth + fwidth(gridUV.x * dotRepeat), cx);
            lineX *= dotMaskY;
            lineY *= dotMaskX;
        }
    }
    float primaryMask = max(lineX, lineY);

    vec2 gridUV2 = (hitIsY > 0.5 ? hit.xz : hit.zy) / gridScale;
    if (jitterAmt > 0.0) {
        vec2 j2 = vec2(
            cos(gridUV2.y * 2.1 - iTime * 1.4),
            sin(gridUV2.x * 2.5 + iTime * 1.7)
        ) * (0.15 * jitterAmt);
        gridUV2 += j2;
    }
    float fx2 = fract(gridUV2.x);
    float fy2 = fract(gridUV2.y);
    float ax2 = min(fx2, 1.0 - fx2);
    float ay2 = min(fy2, 1.0 - fy2);
    float wx2 = fwidth(gridUV2.x);
    float wy2 = fwidth(gridUV2.y);
    float tx2 = halfPx * wx2;
    float ty2 = halfPx * wy2;
    float aax2 = wx2;
    float aay2 = wy2;
    float lineX2 = 1.0 - smoothstep(tx2, tx2 + aax2, ax2);
    float lineY2 = 1.0 - smoothstep(ty2, ty2 + aay2, ay2);
    if (uLineStyle > 0.5) {
        float dashRepeat2 = 4.0;
        float dashDuty2 = 0.5;
        float vy2m = fract(gridUV2.y * dashRepeat2);
        float vx2m = fract(gridUV2.x * dashRepeat2);
        float dashMaskY2 = step(vy2m, dashDuty2);
        float dashMaskX2 = step(vx2m, dashDuty2);
        if (uLineStyle < 1.5) {
            lineX2 *= dashMaskY2;
            lineY2 *= dashMaskX2;
        } else {
            float dotRepeat2 = 6.0;
            float dotWidth2 = 0.18;
            float cy2 = abs(fract(gridUV2.y * dotRepeat2) - 0.5);
            float cx2 = abs(fract(gridUV2.x * dotRepeat2) - 0.5);
            float dotMaskY2 = 1.0 - smoothstep(dotWidth2, dotWidth2 + fwidth(gridUV2.y * dotRepeat2), cy2);
            float dotMaskX2 = 1.0 - smoothstep(dotWidth2, dotWidth2 + fwidth(gridUV2.x * dotRepeat2), cx2);
            lineX2 *= dotMaskY2;
            lineY2 *= dotMaskX2;
        }
    }
    float altMask = max(lineX2, lineY2);

    float edgeDistX = min(abs(hit.x - (-0.5)), abs(hit.x - 0.5));
    float edgeDistY = min(abs(hit.y - (-0.2)), abs(hit.y - 0.2));
    float edgeDist = mix(edgeDistY, edgeDistX, hitIsY);
    float edgeGate = 1.0 - smoothstep(gridScale * 0.5, gridScale * 2.0, edgeDist);
    altMask *= edgeGate;

    float lineMask = max(primaryMask, altMask);

    float fade = exp(-dist * fadeStrength);

    float dur = max(0.05, uScanDuration);
    float del = max(0.0, uScanDelay);
    float scanZMax = 2.0;
    float widthScale = max(0.1, uScanGlow);
    float sigma = max(0.001, 0.18 * widthScale * uScanSoftness);
    float sigmaA = sigma * 2.0;

    float combinedPulse = 0.0;
    float combinedAura = 0.0;

    float cycle = dur + del;
    float tCycle = mod(iTime, cycle);
    float scanPhase = clamp((tCycle - del) / dur, 0.0, 1.0);
    float phase = scanPhase;
    if (uScanDirection > 0.5 && uScanDirection < 1.5) {
        phase = 1.0 - phase;
    } else if (uScanDirection > 1.5) {
        float t2 = mod(max(0.0, iTime - del), 2.0 * dur);
        phase = (t2 < dur) ? (t2 / dur) : (1.0 - (t2 - dur) / dur);
    }
    float scanZ = phase * scanZMax;
    float dz = abs(hit.z - scanZ);
    float lineBand = exp(-0.5 * (dz * dz) / (sigma * sigma));
    float taper = clamp(uPhaseTaper, 0.0, 0.49);
    float headW = taper;
    float tailW = taper;
    float headFade = smoother01(0.0, headW, phase);
    float tailFade = 1.0 - smoother01(1.0 - tailW, 1.0, phase);
    float phaseWindow = headFade * tailFade;
    float pulseBase = lineBand * phaseWindow;
    combinedPulse += pulseBase * clamp(uScanOpacity, 0.0, 1.0);
    float auraBand = exp(-0.5 * (dz * dz) / (sigmaA * sigmaA));
    combinedAura += (auraBand * 0.25) * phaseWindow * clamp(uScanOpacity, 0.0, 1.0);

    for (int i = 0; i < MAX_SCANS; i++) {
        if (float(i) >= uScanCount) break;
        float tActiveI = iTime - uScanStarts[i];
        float phaseI = clamp(tActiveI / dur, 0.0, 1.0);
        if (uScanDirection > 0.5 && uScanDirection < 1.5) {
            phaseI = 1.0 - phaseI;
        } else if (uScanDirection > 1.5) {
            phaseI = (phaseI < 0.5) ? (phaseI * 2.0) : (1.0 - (phaseI - 0.5) * 2.0);
        }
        float scanZI = phaseI * scanZMax;
        float dzI = abs(hit.z - scanZI);
        float lineBandI = exp(-0.5 * (dzI * dzI) / (sigma * sigma));
        float headFadeI = smoother01(0.0, headW, phaseI);
        float tailFadeI = 1.0 - smoother01(1.0 - tailW, 1.0, phaseI);
        float phaseWindowI = headFadeI * tailFadeI;
        combinedPulse += lineBandI * phaseWindowI * clamp(uScanOpacity, 0.0, 1.0);
        float auraBandI = exp(-0.5 * (dzI * dzI) / (sigmaA * sigmaA));
        combinedAura += (auraBandI * 0.25) * phaseWindowI * clamp(uScanOpacity, 0.0, 1.0);
    }

    float lineVis = lineMask;
    vec3 gridCol = uLinesColor * lineVis * fade;
    vec3 scanCol = uScanColor * combinedPulse;
    vec3 scanAura = uScanColor * combinedAura;

    color = gridCol + scanCol + scanAura;

    float n = fract(sin(dot(gl_FragCoord.xy + vec2(iTime * 123.4), vec2(12.9898,78.233))) * 43758.5453123);
    color += (n - 0.5) * uNoise;
    color = clamp(color, 0.0, 1.0);
    float alpha = clamp(max(lineVis, combinedPulse), 0.0, 1.0);
    float gx = 1.0 - smoothstep(tx * 2.0, tx * 2.0 + aax * 2.0, ax);
    float gy = 1.0 - smoothstep(ty * 2.0, ty * 2.0 + aay * 2.0, ay);
    float halo = max(gx, gy) * fade;
    alpha = max(alpha, halo * clamp(uBloomOpacity, 0.0, 1.0));
    fragColor = vec4(color, alpha);
}

void main(){
    vec4 c;
    mainImage(c, vUv * iResolution.xy);
    gl_FragColor = c;
}
`

function srgbColor(hex) {
  const c = new THREE.Color(hex)
  return c.convertSRGBToLinear()
}

function lineStyleVal(style) {
  if (style === 'dashed') return 1
  if (style === 'dotted') return 2
  return 0
}

function scanDirVal(dir) {
  if (dir === 'backward') return 1
  if (dir === 'pingpong') return 2
  return 0
}

function smoothDamp(current, target, velRef, smoothTime, maxSpeed, dt) {
  smoothTime = Math.max(0.0001, smoothTime)
  const omega = 2 / smoothTime
  const x = omega * dt
  const exp = 1 / (1 + x + 0.48 * x * x + 0.235 * x * x * x)

  let change = current - target
  const originalTo = target

  const maxChange = maxSpeed * smoothTime
  change = Math.sign(change) * Math.min(Math.abs(change), maxChange)

  target = current - change
  const temp = (velRef.v + omega * change) * dt
  velRef.v = (velRef.v - omega * temp) * exp

  let out = target + (change + temp) * exp

  const origMinusCurrent = originalTo - current
  const outMinusOrig = out - originalTo
  if (origMinusCurrent * outMinusOrig > 0) {
    out = originalTo
    velRef.v = 0
  }
  return { value: out, v: velRef.v }
}

function smoothDampVec2(current, target, velRef, smoothTime, maxSpeed, dt) {
  smoothTime = Math.max(0.0001, smoothTime)
  const omega = 2 / smoothTime
  const x = omega * dt
  const exp = 1 / (1 + x + 0.48 * x * x + 0.235 * x * x * x)

  let change = current.clone().sub(target)
  const originalTo = target.clone()

  const maxChange = maxSpeed * smoothTime
  if (change.length() > maxChange) change.setLength(maxChange)

  target = current.clone().sub(change)
  const temp = velRef.clone().addScaledVector(change, omega).multiplyScalar(dt)
  velRef.sub(temp.clone().multiplyScalar(omega))
  velRef.multiplyScalar(exp)

  const out = target.clone().add(change.add(temp).multiplyScalar(exp))

  const origMinusCurrent = originalTo.clone().sub(current)
  const outMinusOrig = out.clone().sub(originalTo)
  if (origMinusCurrent.dot(outMinusOrig) > 0) {
    out.copy(originalTo)
    velRef.set(0, 0)
  }
  return out
}

function initScene() {
  container = containerRef.value
  if (!container) return

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))
  renderer.setSize(container.clientWidth, container.clientHeight)
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.toneMapping = THREE.NoToneMapping
  renderer.setClearColor(0x000000, 0)
  container.appendChild(renderer.domElement)

  const MAX_SCANS = 8
  const uniforms = {
    iResolution: { value: new THREE.Vector3(container.clientWidth, container.clientHeight, renderer.getPixelRatio()) },
    iTime: { value: 0 },
    uSkew: { value: new THREE.Vector2(0, 0) },
    uTilt: { value: 0 },
    uYaw: { value: 0 },
    uLineThickness: { value: props.lineThickness },
    uLinesColor: { value: srgbColor(props.linesColor) },
    uScanColor: { value: srgbColor(props.scanColor) },
    uGridScale: { value: props.gridScale },
    uLineStyle: { value: lineStyleVal(props.lineStyle) },
    uLineJitter: { value: Math.max(0, Math.min(1, props.lineJitter)) },
    uScanOpacity: { value: props.scanOpacity },
    uNoise: { value: props.noiseIntensity },
    uBloomOpacity: { value: 0 },
    uScanGlow: { value: props.scanGlow },
    uScanSoftness: { value: props.scanSoftness },
    uPhaseTaper: { value: props.scanPhaseTaper },
    uScanDuration: { value: props.scanDuration },
    uScanDelay: { value: props.scanDelay },
    uScanDirection: { value: scanDirVal(props.scanDirection) },
    uScanStarts: { value: new Array(MAX_SCANS).fill(0) },
    uScanCount: { value: 0 },
  }

  material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: vert,
    fragmentShader: frag,
    transparent: true,
    depthWrite: false,
    depthTest: false,
  })

  const scene = new THREE.Scene()
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1)
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), material)
  scene.add(quad)

  const onResize = () => {
    if (!container) return
    renderer.setSize(container.clientWidth, container.clientHeight)
    material.uniforms.iResolution.value.set(
      container.clientWidth,
      container.clientHeight,
      renderer.getPixelRatio(),
    )
  }
  window.addEventListener('resize', onResize)

  // Mouse interaction
  const s = THREE.MathUtils.clamp(props.sensitivity, 0, 1)
  const skewScale = THREE.MathUtils.lerp(0.06, 0.2, s)
  const tiltScale = THREE.MathUtils.lerp(0.12, 0.3, s)
  const yawScale = THREE.MathUtils.lerp(0.1, 0.28, s)
  const smoothTime = THREE.MathUtils.lerp(0.45, 0.12, s)
  const maxSpeed = Infinity
  const yBoost = THREE.MathUtils.lerp(1.2, 1.6, s)

  const lookTarget = new THREE.Vector2(0, 0)
  const lookCurrent = new THREE.Vector2(0, 0)
  const lookVel = new THREE.Vector2(0, 0)
  const tiltTarget = { current: 0 }
  const tiltCurrent = { current: 0 }
  const tiltVel = { v: 0 }
  const yawTarget = { current: 0 }
  const yawCurrent = { current: 0 }
  const yawVel = { v: 0 }

  let leaveTimer = null

  function onMove(e) {
    if (leaveTimer) {
      clearTimeout(leaveTimer)
      leaveTimer = null
    }
    const rect = container.getBoundingClientRect()
    const nx = ((e.clientX - rect.left) / rect.width) * 2 - 1
    const ny = -(((e.clientY - rect.top) / rect.height) * 2 - 1)
    lookTarget.set(nx, ny)
  }

  function onLeave() {
    if (leaveTimer) clearTimeout(leaveTimer)
    leaveTimer = setTimeout(
      () => {
        lookTarget.set(0, 0)
        tiltTarget.current = 0
        yawTarget.current = 0
      },
      Math.max(0, props.snapBackDelay),
    )
  }

  if (props.mouseInteraction) {
    container.addEventListener('mousemove', onMove)
    container.addEventListener('mouseleave', onLeave)
  }

  let last = performance.now()

  function tick() {
    const now = performance.now()
    const dt = Math.max(0, Math.min(0.1, (now - last) / 1000))
    last = now

    const newLook = smoothDampVec2(lookCurrent, lookTarget, lookVel, smoothTime, maxSpeed, dt)
    lookCurrent.copy(newLook)

    const tiltSm = smoothDamp(tiltCurrent.current, tiltTarget.current, tiltVel, smoothTime, maxSpeed, dt)
    tiltCurrent.current = tiltSm.value
    tiltVel.v = tiltSm.v

    const yawSm = smoothDamp(yawCurrent.current, yawTarget.current, yawVel, smoothTime, maxSpeed, dt)
    yawCurrent.current = yawSm.value
    yawVel.v = yawSm.v

    const skew = new THREE.Vector2(lookCurrent.x * skewScale, -lookCurrent.y * yBoost * skewScale)
    material.uniforms.uSkew.value.set(skew.x, skew.y)
    material.uniforms.uTilt.value = tiltCurrent.current * tiltScale
    material.uniforms.uYaw.value = THREE.MathUtils.clamp(yawCurrent.current * yawScale, -0.6, 0.6)

    material.uniforms.iTime.value = now / 1000

    renderer.render(scene, camera)
    animationId = requestAnimationFrame(tick)
  }
  animationId = requestAnimationFrame(tick)
}

onMounted(() => initScene())

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (renderer) {
    renderer.dispose()
    renderer.forceContextLoss()
  }
  renderer = null
  material = null
})
</script>

<template>
  <div ref="containerRef" class="gridscan-container"></div>
</template>

<style scoped>
.gridscan-container {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
  background: #0a0a0f;
}
</style>
