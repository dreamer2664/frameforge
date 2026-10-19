// kinetic — dimension (r05). 40 s, 1080x1920 @30. All state is a pure function of t.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { AfterimagePass } from 'three/addons/postprocessing/AfterimagePass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { Text } from 'troika-three-text';

// ---------- constants ----------
const W = 1080, H = 1920, DUR = 40.0;
const COL = {
  bg: 0x07070b, coral: 0xff6b35, blue: 0x2b4fd8, cyan: 0x7fe8ff,
  cream: 0xf2eee6, ink: 0x0c0e16, navy: 0x0d1b3d,
};

// ---------- helpers ----------
const clamp01 = (x) => Math.min(1, Math.max(0, x));
const smooth = (a, b, x) => { const k = clamp01((x - a) / (b - a)); return k * k * (3 - 2 * k); };
const easeOutExpo = (k) => (k >= 1 ? 1 : 1 - Math.pow(2, -10 * k));
const easeOutCubic = (k) => 1 - Math.pow(1 - k, 3);
const easeInOutCubic = (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
const easeOutBack = (k) => { const c = 1.70158; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); };
const lerp = (a, b, k) => a + (b - a) * k;

function mulberry32(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ---------- renderer / scene ----------
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H, false);
renderer.setPixelRatio(1);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.82;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(COL.bg);
scene.fog = new THREE.FogExp2(COL.bg, 0.012);

const camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 220);
camera.position.set(0, 0.3, 9);

const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.06).texture;
scene.environmentIntensity = 0.38;

const keyWarm = new THREE.PointLight(COL.coral, 170, 60, 2); keyWarm.position.set(5, 4, 4); scene.add(keyWarm);
const keyCool = new THREE.PointLight(COL.blue, 140, 60, 2); keyCool.position.set(-5.5, 2, 3.5); scene.add(keyCool);
const keyTop = new THREE.PointLight(COL.cyan, 70, 80, 2); keyTop.position.set(0, 7, -2); scene.add(keyTop);
scene.add(new THREE.AmbientLight(0x232636, 1.2));

// ---------- global dust ----------
function dustSystem(count, spread) {
  const g = new THREE.BufferGeometry();
  const pos = new Float32Array(count * 3), seed = new Float32Array(count), size = new Float32Array(count);
  const rng = mulberry32(777);
  for (let i = 0; i < count; i++) {
    pos[i * 3] = (rng() - 0.5) * spread[0];
    pos[i * 3 + 1] = (rng() - 0.5) * spread[1];
    pos[i * 3 + 2] = (rng() - 0.5) * spread[2];
    seed[i] = rng(); size[i] = 0.5 + rng() * 1.1;
  }
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('aSeed', new THREE.BufferAttribute(seed, 1));
  g.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
  const m = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { uT: { value: 0 }, uOpacity: { value: 0.22 }, uScale: { value: H * 0.045 } },
    vertexShader: `
      attribute float aSeed; attribute float aSize;
      uniform float uT; uniform float uScale;
      varying float vA;
      void main(){
        vec3 p = position;
        p.x += sin(uT*0.22 + aSeed*40.0)*0.35;
        p.y += sin(uT*0.16 + aSeed*31.0)*0.30 + uT*0.012;
        p.z += cos(uT*0.19 + aSeed*23.0)*0.35;
        vec4 mv = modelViewMatrix * vec4(p,1.0);
        gl_Position = projectionMatrix * mv;
        gl_PointSize = aSize * uScale / max(1.0, -mv.z);
        vA = 0.35 + 0.65*abs(sin(uT*0.8 + aSeed*20.0));
      }`,
    fragmentShader: `
      uniform float uOpacity; varying float vA;
      void main(){
        vec2 d = gl_PointCoord - 0.5;
        float a = smoothstep(0.5, 0.0, length(d));
        gl_FragColor = vec4(0.85, 0.88, 1.0, a * vA * uOpacity);
      }`,
  });
  return new THREE.Points(g, m);
}
const dust = dustSystem(520, [26, 18, 30]);
scene.add(dust);

// ---------- ACT 0/1: shell -> knot ----------
const N_SHELL = 1600;
const shellGeo = new THREE.BufferGeometry();
{
  const rng = mulberry32(42);
  const start = new Float32Array(N_SHELL * 3), target = new Float32Array(N_SHELL * 3);
  const seed = new Float32Array(N_SHELL), size = new Float32Array(N_SHELL);
  // knot surface sample (cheap parametric)
  for (let i = 0; i < N_SHELL; i++) {
    const u = rng() * Math.PI * 2 * 3; // torus knot param
    const p = 2, q = 3, R = 1.5, r = 0.55;
    const cu = Math.cos(u), su = Math.sin(u), qu = (q / p) * u;
    const cs = Math.cos(qu);
    const x = (R + r * cs) * cu * 1.25, y = (R + r * cs) * su * 1.25, z = r * Math.sin(qu) * 1.25;
    // jitter
    target[i * 3] = x + (rng() - 0.5) * 0.12;
    target[i * 3 + 1] = y + (rng() - 0.5) * 0.12;
    target[i * 3 + 2] = z + (rng() - 0.5) * 0.12;
    // start: tight sphere cluster
    const th = rng() * Math.PI * 2, ph = Math.acos(rng() * 2 - 1), rr = 0.55 * Math.cbrt(rng());
    start[i * 3] = rr * Math.sin(ph) * Math.cos(th);
    start[i * 3 + 1] = rr * Math.sin(ph) * Math.sin(th);
    start[i * 3 + 2] = rr * Math.cos(ph);
    seed[i] = rng(); size[i] = 0.8 + rng() * 1.3;
  }
  shellGeo.setAttribute('position', new THREE.BufferAttribute(start, 3));
  shellGeo.setAttribute('aTarget', new THREE.BufferAttribute(target, 3));
  shellGeo.setAttribute('aSeed', new THREE.BufferAttribute(seed, 1));
  shellGeo.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
}
const shellMat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  uniforms: { uT: { value: 0 }, uScale: { value: H * 0.045 } },
  vertexShader: `
    attribute vec3 aTarget; attribute float aSeed; attribute float aSize;
    uniform float uT; uniform float uScale;
    varying float vA;
    void main(){
      float on = step(aSeed, smoothstep(0.05, 0.85, uT) * 1.2);
      vec3 c = position * 0.02;
      float kImp = pow(smoothstep(0.85, 1.12, uT), 3.0);
      float kExp = 1.0 - pow(2.0, -10.0 * smoothstep(1.12, 3.6, uT));
      float kMor = smoothstep(4.15, 5.45, uT);
      vec3 p = mix(position, c, kImp);
      p = mix(p, position * 3.4, kExp * (1.0 - kMor));
      p = mix(p, aTarget, kMor);
      vec4 mv = modelViewMatrix * vec4(p, 1.0);
      gl_Position = projectionMatrix * mv;
      gl_PointSize = aSize * uScale / max(1.0, -mv.z) * (1.0 + 0.8*kExp);
      vA = on * (1.0 - smoothstep(6.35, 6.95, uT));
    }`,
  fragmentShader: `
    varying float vA;
    void main(){
      vec2 d = gl_PointCoord - 0.5;
      float a = smoothstep(0.5, 0.0, length(d));
      gl_FragColor = vec4(1.0, 0.62, 0.42, a * vA * 0.75);
    }`,
});
const shell = new THREE.Points(shellGeo, shellMat);
scene.add(shell);

// shock ring
const ring = new THREE.Mesh(
  new THREE.TorusGeometry(1, 0.02, 8, 120),
  new THREE.MeshBasicMaterial({ color: COL.cream, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })
);
ring.rotation.x = Math.PI / 2 - 0.14;
scene.add(ring);

// hero knot mesh
const knot = new THREE.Mesh(
  new THREE.TorusKnotGeometry(1.2, 0.42, 240, 40),
  new THREE.MeshStandardMaterial({ color: 0x8f96ad, metalness: 1.0, roughness: 0.2, transparent: true, opacity: 0 })
);
scene.add(knot);

// act1 shards
const shardGroup = new THREE.Group(); scene.add(shardGroup);
const shards = [];
{
  const geo = new THREE.TetrahedronGeometry(0.09);
  const rng = mulberry32(9);
  for (let i = 0; i < 64; i++) {
    const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
      color: i % 3 === 0 ? COL.coral : (i % 3 === 1 ? COL.cyan : COL.cream),
      metalness: 0.9, roughness: 0.25, transparent: true, opacity: 0, emissive: (i % 3 === 0 ? COL.coral : (i % 3 === 1 ? COL.cyan : COL.cream)), emissiveIntensity: 0.3,
    }));
    const r = 2.2 + rng() * 1.8, a = rng() * Math.PI * 2, y = (rng() - 0.5) * 2.2, sp = 0.12 + rng() * 0.3;
    shards.push({ m, r, a, y, sp, rx: rng() * 2, rz: rng() * 2 });
    shardGroup.add(m);
  }
}

// ---------- ACT 2: type tunnel ----------
const typeGroup = new THREE.Group(); scene.add(typeGroup);
const letters = []; // vertical staggered columns, one per depth plane
const COL_Z = [2.2, -1.4, -5.0, -8.6, -12.2];
for (let col = 0; col < 5; col++) {
  const word = 'MOTION';
  for (let i = 0; i < word.length; i++) {
    const t = new Text();
    t.text = word[i];
    t.fontSize = 1.18;
    t.font = '/fonts/ArchivoBlack-Regular.ttf';
    t.color = (col % 2 === 1) ? COL.cyan : COL.cream;
    const x = (i % 2 ? 0.78 : -0.78) + (col - 1) * 0.12;
    const y = 2.42 - i * 0.94;
    t.position.set(x, y, COL_Z[col]);
    t.rotation.y = (i % 2 ? -0.16 : 0.16);
    typeGroup.add(t);
    letters.push({ mesh: t, col, i, x, y, z: COL_Z[col], ph: col * 6 + i });
    t.sync();
  }
}

// ---------- ACT 3: material triad ----------
const triad = new THREE.Group(); scene.add(triad);
const rb = new RoundedBoxGeometry(2.6, 2.6, 2.6, 6, 0.42);
const chrome = new THREE.Mesh(rb, new THREE.MeshStandardMaterial({
  color: 0xb9c0d6, metalness: 1.0, roughness: 0.16, transparent: true, opacity: 0,
}));
const glass = new THREE.Mesh(rb, new THREE.MeshStandardMaterial({
  color: 0x88b4ff, metalness: 1.0, roughness: 0.05, transparent: true, opacity: 0,
  emissive: 0x2b4fd8, emissiveIntensity: 0.12, envMapIntensity: 1.0,
}));
const wire = new THREE.Mesh(rb, new THREE.MeshBasicMaterial({
  color: COL.coral, wireframe: true, transparent: true, opacity: 0,
}));
const wireGlow = new THREE.Mesh(rb, new THREE.MeshBasicMaterial({
  color: COL.coral, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false,
}));
triad.add(chrome, glass, wire, wireGlow);

// act3 floor
const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(80, 80),
  new THREE.MeshStandardMaterial({ color: 0x0a0a11, metalness: 0.95, roughness: 0.38, transparent: true, opacity: 0 })
);
floor.rotation.x = -Math.PI / 2; floor.position.y = -2.35;
scene.add(floor);

// ---------- ACT 4: tube storm ----------
const storm = new THREE.Group(); scene.add(storm);
const tubes = [];
{
  const rng = mulberry32(2024);
  const cols = [COL.coral, COL.cyan, COL.blue, COL.cream];
  for (let k = 0; k < 6; k++) {
    const pts = [];
    for (let j = 0; j < 10; j++) {
      pts.push(new THREE.Vector3(
        Math.sin(j * 0.5 + k * 1.9) * (2.4 + (k % 3) * 1.1),
        Math.cos(j * 0.57 + k * 2.1) * (1.2 + (k % 2) * 0.9),
        46 - j * 12.5
      ));
    }
    const curve = new THREE.CatmullRomCurve3(pts);
    const tube = new THREE.Mesh(
      new THREE.TubeGeometry(curve, 160, 0.05 + (k % 3) * 0.028, 8),
      new THREE.MeshBasicMaterial({ color: cols[k % cols.length], transparent: true, opacity: 0 })
    );
    tubes.push(tube); storm.add(tube);
  }
}
// streaks
const streaks = [];
{
  const geo = new THREE.BoxGeometry(0.022, 0.022, 11);
  const rng = mulberry32(5);
  for (let i = 0; i < 36; i++) {
    const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({
      color: i % 2 ? COL.cyan : COL.cream, transparent: true, opacity: 0,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    streaks.push({
      m, x: (rng() - 0.5) * 10, y: (rng() - 0.5) * 5.5, z0: rng() * 120,
      sp: 26 + rng() * 42,
    });
    storm.add(m);
  }
}
// vortex points
const N_VOR = 2400;
const vorGeo = new THREE.BufferGeometry();
{
  const rng = mulberry32(88);
  const pos = new Float32Array(N_VOR * 3), seed = new Float32Array(N_VOR), size = new Float32Array(N_VOR);
  for (let i = 0; i < N_VOR; i++) {
    const a = rng() * Math.PI * 2, r = 1.2 + Math.pow(rng(), 1.5) * 6.5;
    pos[i * 3] = Math.cos(a) * r; pos[i * 3 + 1] = Math.sin(a) * r * 0.75;
    pos[i * 3 + 2] = -30 + rng() * 110;
    seed[i] = rng(); size[i] = 0.7 + rng() * 1.3;
  }
  vorGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  vorGeo.setAttribute('aSeed', new THREE.BufferAttribute(seed, 1));
  vorGeo.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
}
const vorMat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  uniforms: { uT: { value: 0 }, uOpacity: { value: 0 }, uScale: { value: H * 0.045 }, uSpin: { value: 0 } },
  vertexShader: `
    attribute float aSeed; attribute float aSize;
    uniform float uT; uniform float uScale; uniform float uSpin;
    varying float vA;
    void main(){
      vec3 p = position;
      float ang = uSpin * (0.55 + aSeed*0.7);
      float c = cos(ang), s = sin(ang);
      p.xy = mat2(c, -s, s, c) * p.xy;
      p.z += sin(uT*0.7 + aSeed*30.0)*1.6;
      vec4 mv = modelViewMatrix * vec4(p, 1.0);
      gl_Position = projectionMatrix * mv;
      gl_PointSize = aSize * uScale / max(1.0, -mv.z);
      vA = 0.4 + 0.6*abs(sin(uT*1.2 + aSeed*25.0));
    }`,
  fragmentShader: `
    uniform float uOpacity; varying float vA;
    void main(){
      vec2 d = gl_PointCoord - 0.5;
      float a = smoothstep(0.5, 0.0, length(d));
      gl_FragColor = vec4(0.75, 0.85, 1.0, a * vA * uOpacity);
    }`,
});
const vortex = new THREE.Points(vorGeo, vorMat);
scene.add(vortex);

// ---------- ACT 5: monoliths ----------
const monoGroup = new THREE.Group(); scene.add(monoGroup);
const N_MONO = 260;
const mono = new THREE.InstancedMesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshStandardMaterial({ color: 0x141824, metalness: 0.82, roughness: 0.42, transparent: true, opacity: 0 }),
  N_MONO
);
const monoData = [];
{
  const rng = mulberry32(1234);
  for (let i = 0; i < N_MONO; i++) {
    const gx = (i % 20) - 9.5, gz = Math.floor(i / 20) - 6.5;
    monoData.push({
      x: (() => { let x = gx * 2.35 + (rng() - 0.5) * 1.1; if (Math.abs(x) < 2.9) x += (x >= 0 ? 1 : -1) * 3.4; return x; })(),
      z: gz * 3.1 + (rng() - 0.5) * 1.4,
      h: 1.2 + Math.pow(rng(), 1.6) * 7.5,
      w: 0.75 + rng() * 1.15,
      d: 0.75 + rng() * 1.15,
      rise: rng(),
    });
  }
}
monoGroup.add(mono);
// sun
const sun = new THREE.Mesh(
  new THREE.SphereGeometry(1.7, 48, 32),
  new THREE.MeshBasicMaterial({ color: 0xffc9a8, transparent: true, opacity: 0 })
);
sun.position.set(0, 3.2, -19);
monoGroup.add(sun);
const sunHalo = (() => {
  const cv = document.createElement('canvas'); cv.width = 256; cv.height = 256;
  const ctx = cv.getContext('2d');
  const g = ctx.createRadialGradient(128, 128, 6, 128, 128, 128);
  g.addColorStop(0, 'rgba(255,240,225,1)');
  g.addColorStop(0.18, 'rgba(255,150,95,0.85)');
  g.addColorStop(0.45, 'rgba(255,107,53,0.32)');
  g.addColorStop(1, 'rgba(255,107,53,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, 256, 256);
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({
    map: new THREE.CanvasTexture(cv), transparent: true, opacity: 0,
    blending: THREE.AdditiveBlending, depthWrite: false,
  }));
  sp.position.copy(sun.position);
  sp.scale.setScalar(17);
  return sp;
})();
monoGroup.add(sunHalo);
// light shafts (additive gradient planes)
const shafts = new THREE.Group(); monoGroup.add(shafts);
{
  const cv = document.createElement('canvas'); cv.width = 64; cv.height = 256;
  const ctx = cv.getContext('2d');
  const gr = ctx.createLinearGradient(0, 0, 0, 256);
  gr.addColorStop(0, 'rgba(255,120,70,0.9)'); gr.addColorStop(1, 'rgba(255,120,70,0)');
  ctx.fillStyle = gr; ctx.fillRect(0, 0, 64, 256);
  const tex = new THREE.CanvasTexture(cv);
  for (let i = 0; i < 6; i++) {
    const p = new THREE.Mesh(new THREE.PlaneGeometry(2.2 + i * 0.7, 26),
      new THREE.MeshBasicMaterial({ map: tex, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
    p.position.set(-9 + i * 3.6, 8, -12 + (i % 3) * 3);
    p.rotation.z = (i - 2.5) * 0.12;
    shafts.add(p);
  }
}

// ---------- ACT 6: finale ----------
const finale = new THREE.Group(); scene.add(finale);
const lockup = new THREE.Group();
finale.add(lockup);
const fring = new THREE.Mesh(
  new THREE.TorusGeometry(2.1, 0.014, 8, 160),
  new THREE.MeshBasicMaterial({ color: COL.cream, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })
);
finale.add(fring);
const brand = new Text();
brand.text = 'kinetic';
brand.letterSpacing = -0.015;
brand.fontSize = 1.0;
brand.font = '/fonts/ArchivoBlack-Regular.ttf';
brand.color = COL.cream;
brand.position.set(-1.32, 0.72, 0);
brand.sync();
lockup.add(brand);
const brandDot = new Text();
brandDot.text = '.';
brandDot.fontSize = 1.0;
brandDot.font = '/fonts/ArchivoBlack-Regular.ttf';
brandDot.color = COL.coral;
brandDot.position.set(0.94, 0.72, 0);
brandDot.sync();
lockup.add(brandDot);
let brandReady = false;
setTimeout(() => { brandReady = true; }, 400);
let brandLaid = false;
const tag = new Text();
tag.text = 'motion, engineered.';
tag.fontSize = 0.29;
tag.font = '/fonts/Inter-SemiBold.ttf';
tag.color = 0xb9c2dc;
tag.position.set(-0.92, -0.52, 0);
tag.sync();
lockup.add(tag);
const underline = new THREE.Mesh(
  new THREE.BoxGeometry(1.85, 0.02, 0.02),
  new THREE.MeshBasicMaterial({ color: COL.blue, transparent: true, opacity: 0 })
);
underline.position.set(0, -0.92, 0);
lockup.add(underline);
const implosion = dustSystem(1100, [9, 6.5, 9]);
implosion.material.uniforms.uOpacity.value = 0;
finale.add(implosion);
const impCore = new THREE.Mesh(
  new THREE.SphereGeometry(0.16, 24, 16),
  new THREE.MeshBasicMaterial({ color: 0xffe8d8, transparent: true, opacity: 0 })
);
finale.add(impCore);

// ---------- composer ----------
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), 0.5, 0.42, 0.86);
composer.addPass(bloom);
const after = new AfterimagePass(0.0);
composer.addPass(after);
composer.addPass(new OutputPass());
const gradePass = new ShaderPass({
  uniforms: {
    tDiffuse: { value: null }, uT: { value: 0 }, uFlash: { value: 0 }, uFade: { value: 0 }, uCA: { value: 0.0016 },
  },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
  fragmentShader: `
    uniform sampler2D tDiffuse; uniform float uT, uFlash, uFade, uCA;
    varying vec2 vUv;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
    void main(){
      vec2 d = vUv - 0.5;
      float r2 = dot(d, d);
      vec2 off = d * uCA * (0.6 + r2 * 2.2);
      vec3 col;
      col.r = texture2D(tDiffuse, vUv + off).r;
      col.g = texture2D(tDiffuse, vUv).g;
      col.b = texture2D(tDiffuse, vUv - off).b;
      // vignette
      float vig = smoothstep(1.25, 0.35, r2 * 2.9);
      col *= mix(0.72, 1.0, vig);
      // gentle s-curve
      col = mix(col, col * col * (3.0 - 2.0 * col), 0.22);
      // grain
      float g = hash(vUv * vec2(1080.0, 1920.0) + fract(uT * 61.7) * 100.0) - 0.5;
      col += g * 0.032;
      col = mix(col, vec3(1.0), uFlash);
      col *= (1.0 - uFade);
      gl_FragColor = vec4(col, 1.0);
    }`,
});
composer.addPass(gradePass);

// ---------- camera & timeline ----------
function camAt(t) {
  // returns [pos, target, fov]
  let px, py, pz, tx, ty, tz, fov = 40;
  if (t < 4) {
    const k = easeInOutCubic(smooth(0, 4, t));
    px = 0; py = lerp(0.35, 0.1, k); pz = lerp(9.6, 7.6, k);
    tx = 0; ty = 0; tz = 0;
    // impact shake
    const sh = Math.exp(-Math.pow((t - 0.88) * 9, 2)) * 0.09;
    px += Math.sin(t * 61) * sh; py += Math.cos(t * 53) * sh;
    fov = 42;
  } else if (t < 8) {
    const k = smooth(4, 8, t), a = lerp(-0.55, 0.85, easeInOutCubic(k));
    px = Math.sin(a) * 7.3; pz = Math.cos(a) * 7.3; py = lerp(1.35, 0.55, k);
    tx = 0; ty = 0; tz = 0;
    fov = 38;
  } else if (t < 11.8) {
    const k = smooth(8, 11.8, t);
    px = lerp(0, 0.3, k); py = lerp(0.55, 0.26, k); pz = lerp(10.4, 10.0, k);
    tx = 0; ty = 0.28; tz = 2.2;
    fov = lerp(42, 39, k);
  } else if (t < 14) {
    const k = easeInOutCubic(smooth(11.8, 14, t));
    px = 0.3 + Math.sin(t * 2.1) * 0.1; py = 0.22 + Math.sin(t * 1.7) * 0.07;
    pz = lerp(10.0, -13.8, k);
    tx = px; ty = py; tz = pz - 4;
    fov = 50;
  } else if (t < 20) {
    const k = smooth(14, 20, t), a = lerp(0.25, -0.75, easeInOutCubic(k));
    px = Math.sin(a) * 8.6; pz = Math.cos(a) * 8.6; py = lerp(1.15, 0.45, k);
    tx = 0; ty = 0.25; tz = 0;
    fov = 38;
  } else if (t < 28) {
    const k = smooth(20, 28, t);
    if (t < 24) {
      const k2 = easeInOutCubic(smooth(20, 24, t));
      px = Math.sin(k2 * 5.0) * 0.85; py = Math.cos(k2 * 3.6) * 0.55;
      pz = lerp(34, -8, k2);
      tx = px * 0.85; ty = py * 0.85; tz = pz - 6;
    } else {
      const k2 = easeInOutCubic(smooth(24, 28, t));
      px = Math.sin(k2 * 5.4 + 1.2) * 0.8; py = Math.cos(k2 * 4.2) * 0.5;
      pz = lerp(-8, -34, k2);
      tx = px * 0.9; ty = py * 0.9; tz = pz - 6;
    }
    fov = 55;
  } else if (t < 34) {
    const k = easeInOutCubic(smooth(28, 34, t));
    px = Math.sin(k * 2.4) * 1.35; py = lerp(-1.3, -0.15, k); pz = lerp(12.5, 3.8, k);
    tx = Math.sin(k * 2.4 + 0.5) * 0.8; ty = lerp(1.3, 3.0, k); tz = -14;
    fov = 46;
  } else if (t < 36) {
    const k = easeInOutCubic(smooth(34, 36, t));
    px = lerp(0.9, 0, k); py = lerp(-0.2, 0.1, k); pz = lerp(5.4, 4.2, k);
    tx = 0; ty = 0.1; tz = -2;
    fov = lerp(50, 42, k);
  } else {
    const k = easeInOutCubic(smooth(36, 40, t));
    px = 0; py = lerp(0.12, 0.28, k); pz = lerp(8.3, 9.9, k);
    tx = 0; ty = 0.28; tz = 0;
    fov = lerp(38, 35, k);
  }
  return [px, py, pz, tx, ty, tz, fov];
}

const dummy = new THREE.Object3D();

function applyTime(t) {
  t = Math.min(Math.max(t, 0), DUR - 0.001);
  // ----- camera -----
  const [px, py, pz, tx, ty, tz, fov] = camAt(t);
  camera.position.set(px, py, pz);
  camera.lookAt(tx, ty, tz);
  camera.fov = fov;
  camera.updateProjectionMatrix();

  // ----- cut flashes & finale fade -----
  const CUTS = [4, 8, 14, 20, 28, 34];
  let flash = 0;
  for (const c of CUTS) flash = Math.max(flash, Math.exp(-Math.pow((t - c) * 22, 2)) * 0.28);
  flash += Math.exp(-Math.pow((t - 36) * 9, 2)) * 0.4;
  gradePass.uniforms.uFlash.value = flash;
  gradePass.uniforms.uFade.value = smooth(39.35, 39.96, t);
  gradePass.uniforms.uT.value = t;

  // ----- lights mood -----
  keyWarm.intensity = 170 * (0.7 + 0.5 * Math.sin(t * 0.7) ** 2) * (t > 28 && t < 34 ? 2.2 : 1);
  keyCool.intensity = 140 * (0.75 + 0.45 * Math.cos(t * 0.5) ** 2);
  bloom.strength = 0.48 + (t >= 20 && t < 28 ? 0.22 : 0) + (t >= 28 && t < 34 ? 0.12 : 0);
  {
    let nearCut = false;
    for (const c of [...CUTS, 36]) if (Math.abs(t - c) < 0.22) nearCut = true;
    after.uniforms['damp'].value = nearCut ? 0.0 : ((t >= 20 && t < 28) ? 0.68 : (t >= 11.8 && t < 14 ? 0.55 : 0.12));
  }
  scene.fog.density = (t >= 28 && t < 34) ? 0.026 : ((t >= 20 && t < 28) ? 0.018 : 0.011);

  // ----- dust -----
  dust.material.uniforms.uT.value = t;
  dust.material.uniforms.uOpacity.value = 0.22 + (t >= 34 ? 0.12 : 0);

  // ----- ACT 0/1: shell + ring + knot -----
  shellMat.uniforms.uT.value = t;
  ring.visible = t >= 0.86 && t < 3.4;
  if (ring.visible) {
    const k = smooth(0.88, 3.2, t);
    const s = 0.2 + easeOutExpo(k) * 7.2;
    ring.scale.setScalar(s);
    ring.material.opacity = (1 - k) * 0.55;
    ring.position.y = Math.sin(t * 2) * 0.05;
  }
  const knotOn = t >= 4.1 && t < 8;
  knot.visible = knotOn;
  if (knotOn) {
    knot.material.opacity = smooth(4.3, 5.3, t);
    knot.rotation.x = 0.5 + (t - 4) * 0.22;
    knot.rotation.y = (t - 4) * 0.42;
    knot.rotation.z = Math.sin(t * 0.4) * 0.15;
    const s = lerp(0.72, 1, easeOutBack(smooth(4.2, 5.6, t)));
    knot.scale.setScalar(s);
  }
  const shardOn = t >= 4.6 && t < 8;
  shardGroup.visible = shardOn;
  if (shardOn) {
    const op = smooth(4.6, 5.4, t) * (1 - smooth(7.5, 7.95, t));
    for (const s of shards) {
      const a = s.a + t * s.sp;
      s.m.position.set(Math.cos(a) * s.r, s.y + Math.sin(t * 0.7 + s.a) * 0.18, Math.sin(a) * s.r);
      s.m.rotation.x = t * s.rx; s.m.rotation.z = t * s.rz;
      s.m.material.opacity = op;
    }
  }

  // ----- ACT 2: type -----
  const typeOn = t >= 8.05 && t < 14;
  typeGroup.visible = typeOn;
  if (typeOn) {
    const tunnel = smooth(11.5, 12.15, t); // letters part to open the flight corridor
    for (const L of letters) {
      const stag = L.col * 0.2 + L.i * 0.11;
      const k = clamp01((t - 8.15 - stag) / 0.62);
      const e = k <= 0 ? 0 : easeOutBack(k);
      const appear = L.col === 0 ? 1 : smooth(11.35 + L.col * 0.09, 11.85 + L.col * 0.09, t);
      L.mesh.visible = (k > 0) && appear > 0.01;
      L.mesh.position.z = lerp(L.z - 26, L.z, e);
      L.mesh.position.y = L.y + Math.sin(t * 1.1 + L.ph) * 0.045;
      L.mesh.position.x = L.x * (1 + 0.62 * tunnel);
      L.mesh.rotation.y = (L.i % 2 ? -0.16 : 0.16) + (1 - e) * 0.5 + tunnel * (L.i % 2 ? -0.22 : 0.22);
      L.mesh.material.opacity = clamp01(k * 2) * appear * (1 - 0.15 * tunnel);
      L.mesh.material.transparent = true;
    }
  }

  // ----- ACT 3: triad -----
  const triOn = t >= 14 && t < 20;
  triad.visible = triOn;
  floor.visible = (t >= 14 && t < 20);
  if (triOn) {
    triad.rotation.y = (t - 14) * 0.32;
    triad.rotation.x = Math.sin((t - 14) * 0.5) * 0.12;
    const s = (1 + Math.sin((t - 14) * 1.1) * 0.035) * 0.85;
    triad.scale.setScalar(s);
    chrome.material.opacity = smooth(14, 14.4, t) * (1 - smooth(16.0, 16.45, t));
    glass.material.opacity = smooth(16.0, 16.45, t) * (1 - smooth(17.9, 18.35, t));
    wire.material.opacity = smooth(17.9, 18.35, t) * 0.55;
    wireGlow.material.opacity = smooth(17.9, 18.35, t) * 0.16;
    chrome.visible = chrome.material.opacity > 0.01;
    glass.visible = glass.material.opacity > 0.01;
    wire.visible = wireGlow.visible = wire.material.opacity > 0.01;
  }
  if (floor.visible) floor.material.opacity = 1;

  // ----- ACT 4: storm -----
  const stormOn = t >= 20 && t < 28;
  storm.visible = stormOn;
  if (stormOn) {
    const op = Math.min(smooth(20, 20.35, t), 1 - smooth(27.7, 28, t));
    for (const tb of tubes) tb.material.opacity = op * 0.85;
    for (const st of streaks) {
      const z = ((st.z0 + t * st.sp) % 120) - 60;
      st.m.position.set(st.x, st.y, z + camera.position.z - 10);
      st.m.material.opacity = op * 0.55;
    }
  }
  const vorOn = t >= 23.6 && t < 28.2;
  vortex.visible = vorOn;
  if (vorOn) {
    vorMat.uniforms.uT.value = t;
    vorMat.uniforms.uSpin.value = (t - 23.6) * 1.35;
    vorMat.uniforms.uOpacity.value = smooth(23.6, 24.3, t) * (1 - smooth(27.8, 28.15, t));
  }

  // ----- ACT 5: monoliths -----
  const monOn = t >= 28 && t < 34.1;
  monoGroup.visible = monOn;
  if (monOn) {
    mono.material.opacity = 1;
    const riseK = smooth(28, 29.8, t);
    for (let i = 0; i < N_MONO; i++) {
      const d = monoData[i];
      const k = easeOutCubic(clamp01((riseK - d.rise * 0.55) / 0.45));
      const h = Math.max(0.001, d.h * k);
      dummy.position.set(d.x, -2.2 + h / 2, d.z);
      dummy.scale.set(d.w, h, d.d);
      dummy.rotation.set(0, (i * 0.37) % (Math.PI / 2), 0);
      dummy.updateMatrix();
      mono.setMatrixAt(i, dummy.matrix);
    }
    mono.instanceMatrix.needsUpdate = true;
    sun.material.opacity = smooth(28.2, 29.2, t) * (1 - smooth(33.7, 34.05, t));
    sunHalo.material.opacity = smooth(28.1, 29.4, t) * (1 - smooth(33.6, 34.0, t)) * 0.9;
    const ss = 1 + Math.sin(t * 0.9) * 0.03;
    sun.scale.setScalar(ss);
    sunHalo.scale.setScalar(17 * ss);
    const shOp = smooth(28.6, 29.6, t) * (1 - smooth(33.6, 34, t)) * 0.16;
    shafts.children.forEach((p, i) => { p.material.opacity = shOp * (0.7 + 0.3 * Math.sin(t * 0.8 + i)); });
  }

  // ----- ACT 6: finale -----
  const finOn = t >= 34 && t < 40;
  finale.visible = finOn || t >= 34;
  if (t >= 34) {
    // implosion 34-36
    const imp = implosion.material.uniforms;
    imp.uT.value = t;
    imp.uOpacity.value = smooth(34, 34.4, t) * (1 - smooth(35.7, 36.0, t)) * 0.85;
    // converge: scale the cloud down
    const kk = 1 - easeInOutCubic(smooth(34, 36, t)) * 0.96;
    implosion.scale.setScalar(Math.max(0.02, kk));
    implosion.visible = imp.uOpacity.value > 0.01;
    const coreK = smooth(34.2, 35.85, t);
    impCore.visible = t >= 34.15 && t < 36.02;
    impCore.material.opacity = coreK;
    impCore.scale.setScalar(0.5 + coreK * 2.2);

    const calm = smooth(36.1, 36.8, t);
    fring.material.opacity = calm * 0.5;
    fring.rotation.x = 1.02 + Math.sin(t * 0.4) * 0.1;
    fring.rotation.z = -0.18 + t * 0.05;
    fring.scale.setScalar(lerp(1.35, 1, easeOutCubic(calm)));

    const bk = smooth(36.25, 37.15, t);
    brand.material.opacity = bk; brand.material.transparent = true;
    brandDot.material.opacity = bk; brandDot.material.transparent = true;
    tag.material.opacity = smooth(36.7, 37.6, t) * 0.95; tag.material.transparent = true;
    underline.material.opacity = smooth(36.9, 37.8, t) * 0.9;
    if (brandReady && !brandLaid) {
      // measure once, center the lockup, then scale it to fit the portrait frame
      const bb = new THREE.Box3().setFromObject(brand);
      const db = new THREE.Box3().setFromObject(brandDot);
      const bw = bb.max.x - bb.min.x, dw = db.max.x - db.min.x;
      const total = bw + 0.1 + dw;
      brand.position.x = -total / 2 - bb.min.x + brand.position.x;
      brandDot.position.x = -total / 2 + bw + 0.1 - db.min.x + brandDot.position.x;
      underline.scale.x = (total * 0.94) / 1.85;
      tag.position.x = 0; tag.anchorX = 'center';
      const fovV = 35 * Math.PI / 180;
      const frameW = 2 * 9.9 * Math.tan(fovV / 2) * (W / H); // horizontal world width at farthest pull-back
      const fit = Math.min(1, (frameW * 0.86) / total);
      lockup.scale.setScalar(fit);
      brandLaid = true;
    }
    const baseY = lerp(-0.25, 0, easeOutCubic(bk));
    brand.position.y = 0.72 + baseY; brandDot.position.y = 0.72 + baseY;
    tag.position.y = -0.52 + baseY; underline.position.y = -0.92 + baseY;
    brand.visible = brandDot.visible = bk > 0.01;
    tag.visible = tag.material.opacity > 0.01;
    underline.visible = underline.material.opacity > 0.01;
  }
}

// ---------- boot ----------
window.__objs = { ring, knot, shell, dust, typeGroup, triad, storm, vortex, monoGroup, finale, floor, shards: shardGroup, tubes };
window.__seek = (t) => { applyTime(t); composer.render(); };
applyTime(0);
composer.render();
window.__ready = true;
window.__shot = () => renderer.domElement.toDataURL('image/jpeg', 0.93);
