// PRISM film assembly — renderer + composer + type overlay + renderFrame(i).
// renderFrame is the single source of temporal truth: pure function of i.
import * as THREE from 'three';
import { W, H, actOf } from './constants.js';
import { buildWorld } from './world.js';
import { TypeLayer, loadFonts } from './text.js';
import { buildComposer } from './grade.js';

export async function createFilm(canvas) {
  await loadFonts();

  const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    preserveDrawingBuffer: true,
    alpha: false,
    powerPreference: 'high-performance',
  });
  renderer.setSize(W, H, false);
  renderer.setPixelRatio(1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.06;

  const world = buildWorld();
  const type = new TypeLayer();
  const { composer, bloom, grade } = buildComposer(renderer, world.scene, world.camera);

  const fc = new THREE.Color();
  let lastBoxes = [];

  function renderFrame(i) {
    const f = i | 0;
    const act = actOf(f);
    const flash = world.update(f);

    lastBoxes = type.update(f);

    const u = grade.uniforms;
    u.uFrame.value = f;
    u.uFlash.value = flash.i;
    fc.set(flash.c);
    u.uFlashColor.value.copy(fc);
    u.uCA.value = (act === 3 ? 2.2 : 0.7) + flash.i * 9.0;
    u.uVig.value = act === 1 ? 0.34 : act === 2 ? 0.30 : act === 3 ? 0.26 : 0.22;
    u.uGrain.value = act === 4 ? 0.022 : 0.030;
    u.uSat.value = act === 3 ? 0.42 : act === 2 ? 1.06 : 1.0;
    if (act === 1) u.uLift.value.setRGB(0.014, 0.007, 0.001);
    else if (act === 2) u.uLift.value.setRGB(0.001, 0.005, 0.011);
    else if (act === 3) u.uLift.value.setRGB(0.004, 0.004, 0.005);
    else u.uLift.value.setRGB(0.012, 0.010, 0.007);
    bloom.strength = act === 3 ? 0.85 : act === 1 ? 0.66 : 0.62;

    composer.render();
    renderer.autoClear = false;
    renderer.clearDepth();
    renderer.render(type.scene, type.cam);
    renderer.autoClear = true;
    return lastBoxes;
  }

  const gl = renderer.getContext();
  const diag = {
    glVersion: gl.getParameter(gl.VERSION),
    renderer: gl.getParameter(gl.RENDERER),
    vendor: gl.getParameter(gl.VENDOR),
    maxTextureSize: gl.getParameter(gl.MAX_TEXTURE_SIZE),
  };

  return { renderer, world, type, composer, renderFrame, measure: () => lastBoxes, diag };
}
