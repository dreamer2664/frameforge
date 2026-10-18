import * as THREE from 'three';
import { buildProbe } from './scene.js';
const canvas = document.getElementById('c');
const P = buildProbe(canvas);
window.__probe = {
  diag: P.diag,
  three: THREE.REVISION,
  renderFrame: (i) => { P.renderFrame(i); return true; },
  info: () => P.renderer.info.render,
};
window.__ready = true;
