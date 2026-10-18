// PRISM world — the 3D stage. Four acts, one scene graph, objects gated by act.
import * as THREE from 'three';
import { PAL, SEED, ACT, actOf } from './constants.js';
import { mulberry32, ease, inv, lerp, clamp, valueNoise1D } from './util.js';
import { CAMERA, FLASHES, HITS } from './events.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);

function radialTexture(inner, outer) {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const g = c.getContext('2d');
  const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  gr.addColorStop(0, inner);
  gr.addColorStop(0.4, outer);
  gr.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = gr;
  g.fillRect(0, 0, 256, 256);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/* ------------------------------- ACT I dust ------------------------------ */
function buildDust(count, seed, color, spread) {
  const rnd = mulberry32(seed);
  const pos = new Float32Array(count * 3);
  const ph = new Float32Array(count);
  const sz = new Float32Array(count);
  for (let i = 0; i < count; i++) {
    const r = Math.pow(rnd(), 0.62) * spread;
    const th = rnd() * Math.PI * 2;
    const y = (rnd() - 0.5) * spread * 0.55;
    pos[i * 3] = Math.cos(th) * r;
    pos[i * 3 + 1] = y;
    pos[i * 3 + 2] = Math.sin(th) * r;
    ph[i] = rnd() * 100;
    sz[i] = 0.6 + rnd() * 2.4;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('aPhase', new THREE.BufferAttribute(ph, 1));
  geo.setAttribute('aSize', new THREE.BufferAttribute(sz, 1));
  const mat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { uTime: { value: 0 }, uColor: { value: new THREE.Color(color) }, uOpacity: { value: 1 }, uPix: { value: 1080 } },
    vertexShader: /* glsl */`
      attribute float aPhase; attribute float aSize;
      uniform float uTime; uniform float uPix;
      varying float vA;
      void main(){
        vec3 p = position;
        float t = uTime*0.22 + aPhase;
        p.x += sin(t*1.7 + p.z*0.35)*0.9;
        p.y += sin(t*1.1 + p.x*0.28)*0.7;
        p.z += cos(t*1.3 + p.y*0.31)*0.9;
        vec4 mv = modelViewMatrix * vec4(p,1.0);
        gl_Position = projectionMatrix * mv;
        gl_PointSize = aSize * (uPix/1080.0) * (26.0 / -mv.z);
        vA = smoothstep(60.0, 8.0, -mv.z);
      }`,
    fragmentShader: /* glsl */`
      uniform vec3 uColor; uniform float uOpacity; varying float vA;
      void main(){
        vec2 q = gl_PointCoord - 0.5;
        float d = length(q);
        float a = smoothstep(0.5, 0.06, d);
        a *= a;
        gl_FragColor = vec4(uColor, a*vA*uOpacity);
      }`,
  });
  return new THREE.Points(geo, mat);
}

/* ------------------------------ ACT II grid ------------------------------ */
function buildGrid() {
  const g = new THREE.Group();
  const N = 34, S = 1.6, EXT = (N * S) / 2;
  const pts = [];
  for (let i = -N / 2; i <= N / 2; i++) {
    pts.push(-EXT, 0, i * S, EXT, 0, i * S);
    pts.push(i * S, 0, -EXT, i * S, 0, EXT);
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
  const mat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { uTime: { value: 0 }, uColor: { value: new THREE.Color(PAL.iceMid) }, uReveal: { value: 0 } },
    vertexShader: /* glsl */`
      varying vec3 vP;
      void main(){ vP = position; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
    fragmentShader: /* glsl */`
      uniform float uTime; uniform vec3 uColor; uniform float uReveal;
      varying vec3 vP;
      void main(){
        float r = length(vP.xz);
        float fade = smoothstep(30.0, 4.0, r);
        float ring = smoothstep(0.9, 1.0, sin(r*0.9 - uTime*2.4)*0.5+0.5);
        float a = fade * (0.20 + ring*0.55) * uReveal;
        gl_FragColor = vec4(uColor, a);
      }`,
  });
  const lines = new THREE.LineSegments(geo, mat);
  lines.position.y = -4.2;
  g.add(lines);

  // vertical measure posts
  const postPts = [];
  for (let i = 0; i < 26; i++) {
    const rnd = mulberry32(SEED + i * 7);
    const x = (rnd() - 0.5) * 44, z = (rnd() - 0.5) * 44;
    const h = 1.5 + rnd() * 6.5;
    postPts.push(x, -4.2, z, x, -4.2 + h, z);
  }
  const pgeo = new THREE.BufferGeometry();
  pgeo.setAttribute('position', new THREE.Float32BufferAttribute(postPts, 3));
  const pmat = new THREE.LineBasicMaterial({ color: PAL.iceDeep, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending, depthWrite: false });
  const posts = new THREE.LineSegments(pgeo, pmat);
  g.add(posts);
  g.userData.mat = mat;
  return g;
}

function buildSpecimen() {
  const g = new THREE.Group();
  const geo = new THREE.IcosahedronGeometry(3.1, 1);
  const fres = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.FrontSide,
    uniforms: { uColor: { value: new THREE.Color(PAL.ice) }, uHot: { value: new THREE.Color(PAL.amber) }, uMix: { value: 0 }, uTime: { value: 0 } },
    vertexShader: /* glsl */`
      varying vec3 vN; varying vec3 vV;
      void main(){
        vN = normalize(normalMatrix*normal);
        vec4 mv = modelViewMatrix*vec4(position,1.0);
        vV = normalize(-mv.xyz);
        gl_Position = projectionMatrix*mv;
      }`,
    fragmentShader: /* glsl */`
      uniform vec3 uColor; uniform vec3 uHot; uniform float uMix; uniform float uTime;
      varying vec3 vN; varying vec3 vV;
      void main(){
        float f = pow(1.0 - abs(dot(vN,vV)), 2.2);
        vec3 c = mix(uColor, uHot, uMix);
        gl_FragColor = vec4(c, f*0.38);
      }`,
  });
  const solid = new THREE.Mesh(geo, fres);
  const wire = new THREE.LineSegments(
    new THREE.EdgesGeometry(geo),
    new THREE.LineBasicMaterial({ color: PAL.ice, transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending, depthWrite: false })
  );
  wire.scale.setScalar(1.002);
  g.add(solid, wire);
  g.userData = { fres, wire };
  return g;
}

function buildRing() {
  const g = new THREE.Group();
  const pts = [];
  const R = 6.4, TICKS = 72;
  for (let i = 0; i < TICKS; i++) {
    const a = (i / TICKS) * Math.PI * 2;
    const long = i % 6 === 0;
    const r0 = R, r1 = R + (long ? 0.75 : 0.32);
    pts.push(Math.cos(a) * r0, 0, Math.sin(a) * r0, Math.cos(a) * r1, 0, Math.sin(a) * r1);
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
  const mat = new THREE.LineBasicMaterial({ color: PAL.iceMid, transparent: true, opacity: 0.75, blending: THREE.AdditiveBlending, depthWrite: false });
  g.add(new THREE.LineSegments(geo, mat));
  const cgeo = new THREE.BufferGeometry();
  const cpts = [];
  for (let i = 0; i <= 128; i++) {
    const a = (i / 128) * Math.PI * 2;
    cpts.push(Math.cos(a) * R, 0, Math.sin(a) * R);
  }
  cgeo.setAttribute('position', new THREE.Float32BufferAttribute(cpts, 3));
  g.add(new THREE.Line(cgeo, new THREE.LineBasicMaterial({ color: PAL.iceDeep, transparent: true, opacity: 0.9, depthWrite: false })));
  return g;
}

/* --------------------------- ACT III verdict ----------------------------- */
function buildDiagram() {
  const g = new THREE.Group();
  const geo = new THREE.IcosahedronGeometry(3.4, 1);
  const edges = new THREE.EdgesGeometry(geo);
  const src = edges.attributes.position.array;
  const geo2 = new THREE.BufferGeometry();
  geo2.setAttribute('position', new THREE.BufferAttribute(src.slice(), 3));
  const mat = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.95, blending: THREE.AdditiveBlending, depthWrite: false });
  const lines = new THREE.LineSegments(geo2, mat);
  g.add(lines);

  // corner brackets (world-space, framing the hero type)
  const bw = 8.6, bh = 4.2, L = 1.2, z = 0.02;
  const bp = [];
  const corner = (sx, sy) => {
    bp.push(sx * bw, sy * bh, z, sx * bw - sx * L, sy * bh, z);
    bp.push(sx * bw, sy * bh, z, sx * bw, sy * bh - sy * L, z);
  };
  corner(1, 1); corner(-1, 1); corner(1, -1); corner(-1, -1);
  const bgeo = new THREE.BufferGeometry();
  bgeo.setAttribute('position', new THREE.Float32BufferAttribute(bp, 3));
  const brackets = new THREE.LineSegments(bgeo, new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.9, depthWrite: false }));
  g.add(brackets);

  // crosshair with centre gap
  const cp = [];
  const gap = 1.1, ext = 15;
  cp.push(-ext, 0, z, -gap, 0, z, gap, 0, z, ext, 0, z);
  cp.push(0, -ext * 0.56, z, 0, -gap * 0.6, z, 0, gap * 0.6, z, 0, ext * 0.56, z);
  const cgeo = new THREE.BufferGeometry();
  cgeo.setAttribute('position', new THREE.Float32BufferAttribute(cp, 3));
  const cross = new THREE.LineSegments(cgeo, new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.4, depthWrite: false }));
  g.add(cross);

  g.userData = { lines, src, brackets, cross };
  return g;
}

/* --------------------------------- world --------------------------------- */
export function buildWorld() {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(PAL.voidWarm);

  const camera = new THREE.PerspectiveCamera(38, 1920 / 1080, 0.1, 300);

  const dustI = buildDust(3200, SEED + 1, PAL.amber, 26);
  const dustIV = buildDust(900, SEED + 9, PAL.amberDeep, 18);
  const glowI = new THREE.Sprite(new THREE.SpriteMaterial({ map: radialTexture('rgba(255,170,70,0.85)', 'rgba(255,120,0,0.28)'), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0.8 }));
  glowI.scale.setScalar(34);
  const scan = new THREE.Mesh(
    new THREE.PlaneGeometry(60, 0.06),
    new THREE.MeshBasicMaterial({ color: PAL.amber, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false })
  );

  const grid = buildGrid();
  const specimen = buildSpecimen();
  const ring = buildRing();
  ring.rotation.x = Math.PI / 2.15;

  const diagram = buildDiagram();
  const glowIII = new THREE.Sprite(new THREE.SpriteMaterial({ map: radialTexture('rgba(255,255,255,0.9)', 'rgba(190,220,255,0.25)'), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0 }));
  glowIII.scale.setScalar(30);

  scene.add(dustI, dustIV, glowI, scan, grid, specimen, ring, diagram, glowIII);

  const nz = valueNoise1D(SEED ^ 0xbeef);

  function shakeAt(f) {
    let amp = 0;
    for (const h of HITS) {
      if (h.kind === 'impact' || h.kind === 'drop' || h.kind === 'stamp') {
        const d = f - h.frame;
        if (d >= 0 && d < 16) amp = Math.max(amp, (h.kind === 'drop' ? 0.55 : 0.28) * Math.pow(1 - d / 16, 2));
      }
    }
    return amp;
  }

  function flashAt(f) {
    for (const fl of FLASHES) {
      const d = f - fl.frame;
      if (d >= 0 && d < fl.dur) return { i: fl.peak, c: fl.color };
      if (d === fl.dur) return { i: fl.peak * 0.32, c: fl.color };
      if (d === -1) return { i: fl.peak * 0.18, c: fl.color };
    }
    return { i: 0, c: '#ffffff' };
  }

  function update(f) {
    const act = actOf(f);
    const t = f / 30;

    dustI.visible = act === 1;
    glowI.visible = act === 1;
    scan.visible = f <= 120;
    grid.visible = act === 2;
    specimen.visible = act === 2 || act === 3;
    ring.visible = act === 2;
    diagram.visible = act === 3;
    glowIII.visible = act === 3;
    dustIV.visible = act === 4;

    // background per act (hard cuts are edit points)
    scene.background.setHex(act === 1 ? PAL.voidWarm : act === 2 ? PAL.voidCold : act === 3 ? PAL.voidInk : PAL.voidInk);

    if (act === 1) {
      dustI.material.uniforms.uTime.value = t;
      dustI.material.uniforms.uOpacity.value = 0.9;
      dustI.rotation.y = t * 0.05;
      glowI.material.opacity = 0.55 + 0.25 * Math.sin(t * 1.7);
      // scanline sweep top->bottom twice, eased
      const sp = ease.inOutCubic(inv(f, 6, 60));
      scan.position.set(0, lerp(9, -9, sp), 4);
      scan.material.opacity = 0.85 * (1 - inv(f, 108, 122));
    }

    if (act === 2) {
      const lp = ease.inOutCubic(inv(f, ACT.II[0], ACT.II[0] + 40));
      grid.userData.mat.uniforms.uTime.value = t;
      grid.userData.mat.uniforms.uReveal.value = lp;
      grid.position.y = lerp(-7.5, -4.2, lp);
      specimen.rotation.set(t * 0.24, t * 0.41, t * 0.11);
      specimen.userData.fres.uniforms.uTime.value = t;
      specimen.userData.fres.uniforms.uMix.value = 0.18 + 0.1 * Math.sin(t * 0.9);
      ring.rotation.z = ease.inOutCubic(inv(f, 200, 430)) * Math.PI * 1.5;
      const rs = ease.outBack(inv(f, ACT.II[0] + 6, ACT.II[0] + 30));
      ring.scale.setScalar(0.6 + rs * 0.4);
    }

    if (act === 3) {
      const ex = ease.outQuint(inv(f, 480, 540));
      const arr = diagram.userData.lines.geometry.attributes.position.array;
      const src = diagram.userData.src;
      for (let i = 0; i < arr.length; i += 3) {
        const mx = src[i], my = src[i + 1], mz = src[i + 2];
        const len = Math.hypot(mx, my, mz) || 1;
        const k = 1 + ex * 0.55;
        arr[i] = mx * k; arr[i + 1] = my * k; arr[i + 2] = mz * k;
        void len;
      }
      diagram.userData.lines.geometry.attributes.position.needsUpdate = true;
      diagram.scale.setScalar(0.82);
      diagram.rotation.y = t * 0.12;
      diagram.rotation.x = 0.12 * Math.sin(t * 0.5);
      const bp = ease.outQuint(inv(f, 486, 510));
      diagram.userData.brackets.scale.setScalar(lerp(1.35, 1.0, bp));
      diagram.userData.brackets.material.opacity = 0.9 * bp;
      diagram.userData.cross.material.opacity = 0.4 * ease.inOutCubic(inv(f, 490, 520));
      const gp = f >= 480 && f < 500 ? Math.pow(1 - (f - 480) / 20, 2) : 0;
      glowIII.material.opacity = gp * 0.9;
      specimen.visible = false;
    }

    if (act === 4) {
      dustIV.material.uniforms.uTime.value = t * 0.6;
      dustIV.material.uniforms.uOpacity.value = 0.5;
      dustIV.rotation.y = t * 0.02;
    }

    // camera choreography
    const C = CAMERA;
    let px, py, pz, lx = 0, ly = 0, lz = 0;
    if (act === 1) {
      const p = ease.inOutQuint(inv(f, C.I.f[0], C.I.f[1]));
      px = lerp(C.I.pos[0][0], C.I.pos[1][0], p);
      py = lerp(C.I.pos[0][1], C.I.pos[1][1], p);
      pz = lerp(C.I.pos[0][2], C.I.pos[1][2], p);
    } else if (act === 2) {
      const o = C.II.orbit;
      const p = ease.inOutCubic(inv(f, o.f[0], o.f[1]));
      const a = lerp(o.a0, o.a1, p);
      const r = o.r;
      px = Math.cos(a) * r; pz = Math.sin(a) * r; py = lerp(o.y0, o.y1, p);
      lx = 0; ly = -0.4; lz = 0;
    } else if (act === 3) {
      const p = ease.outQuint(inv(f, C.III.f[0], C.III.f[1]));
      px = lerp(C.III.pos[0][0], C.III.pos[1][0], p);
      py = lerp(C.III.pos[0][1], C.III.pos[1][1], p);
      pz = lerp(C.III.pos[0][2], C.III.pos[1][2], p);
    } else {
      px = 0; py = 0; pz = 12;
    }
    const amp = shakeAt(f);
    if (amp > 0) {
      px += nz(f * 0.9) * amp;
      py += nz(f * 1.3 + 31.7) * amp * 0.7;
      pz += nz(f * 0.7 + 71.1) * amp * 0.5;
    }
    camera.position.set(px, py, pz);
    camera.lookAt(lx, ly, lz);

    return flashAt(f);
  }

  return { scene, camera, update };
}
