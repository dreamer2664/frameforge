// PRISM probe scene — minimal but representative: perspective camera, PBR-ish
// materials, a point light, a shader pass and a canvas-text texture.
// Used only to measure headless WebGL feasibility + per-frame cost.
import * as THREE from 'three';

export function buildProbe(canvas) {
  const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    preserveDrawingBuffer: true,
    alpha: false,
    powerPreference: 'high-performance',
  });
  renderer.setSize(1920, 1080, false);
  renderer.setPixelRatio(1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x05060a);
  scene.fog = new THREE.FogExp2(0x05060a, 0.035);

  const camera = new THREE.PerspectiveCamera(38, 1920 / 1080, 0.1, 200);

  const key = new THREE.PointLight(0xffffff, 220, 60, 2);
  const rim = new THREE.PointLight(0x66aaff, 140, 60, 2);
  scene.add(key, rim, new THREE.AmbientLight(0x223344, 0.6));

  // instanced shard field — representative geometry load
  const N = 900;
  const geo = new THREE.IcosahedronGeometry(0.35, 1);
  const mat = new THREE.MeshStandardMaterial({
    color: 0x9fb4d8, metalness: 0.85, roughness: 0.22, flatShading: true,
  });
  const inst = new THREE.InstancedMesh(geo, mat, N);
  const m = new THREE.Matrix4();
  const q = new THREE.Quaternion();
  const e = new THREE.Euler();
  const seeds = [];
  let s = 1234567;
  const rnd = () => (s = (s * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
  for (let i = 0; i < N; i++) {
    seeds.push({ r: 4 + rnd() * 22, a: rnd() * Math.PI * 2, y: (rnd() - 0.5) * 14, sp: 0.2 + rnd() });
  }
  scene.add(inst);

  // canvas-text texture (typography path)
  const c = document.createElement('canvas');
  c.width = 2048; c.height = 512;
  const g = c.getContext('2d');
  g.fillStyle = '#000'; g.fillRect(0, 0, 2048, 512);
  g.fillStyle = '#fff';
  g.font = '700 300px sans-serif';
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText('PROOF', 1024, 256);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  const plane = new THREE.Mesh(
    new THREE.PlaneGeometry(12, 3),
    new THREE.MeshBasicMaterial({ map: tex, transparent: true })
  );
  scene.add(plane);

  const diag = {
    renderer: renderer.getContext().getParameter(renderer.getContext().RENDERER),
    vendor: renderer.getContext().getParameter(renderer.getContext().VENDOR),
    glVersion: renderer.getContext().getParameter(renderer.getContext().VERSION),
    maxTex: renderer.getContext().getParameter(renderer.getContext().MAX_TEXTURE_SIZE),
  };

  function renderFrame(i) {
    const t = i / 30;
    const e2 = new THREE.Euler();
    for (let k = 0; k < N; k++) {
      const sd = seeds[k];
      const a = sd.a + t * sd.sp * 0.4;
      const y = sd.y + Math.sin(t * 0.8 + k) * 1.2;
      e2.set(t * sd.sp, a * 2, t * 0.3 * sd.sp);
      q.setFromEuler(e2);
      m.compose(new THREE.Vector3(Math.cos(a) * sd.r, y, Math.sin(a) * sd.r), q, new THREE.Vector3(1, 1, 1));
      inst.setMatrixAt(k, m);
    }
    inst.instanceMatrix.needsUpdate = true;
    key.position.set(Math.cos(t) * 8, 5 + Math.sin(t * 1.3) * 3, Math.sin(t) * 8);
    rim.position.set(-Math.cos(t * 0.7) * 10, -3, -Math.sin(t * 0.7) * 10);
    camera.position.set(Math.cos(t * 0.25) * 16, 2 + Math.sin(t * 0.3) * 3, Math.sin(t * 0.25) * 16);
    camera.lookAt(0, 0, 0);
    plane.lookAt(camera.position);
    renderer.render(scene, camera);
  }

  return { renderer, scene, camera, renderFrame, diag };
}
