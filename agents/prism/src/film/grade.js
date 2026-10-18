// PRISM grade chain — bloom + custom final pass (chromatic aberration,
// vignette, film grain, ordered dither, flash overlay, per-act lift).
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';

export const GradeShader = {
  uniforms: {
    tDiffuse: { value: null },
    uFlash: { value: 0 },
    uFlashColor: { value: new THREE.Color(1, 1, 1) },
    uCA: { value: 0.0 },
    uVig: { value: 0.32 },
    uGrain: { value: 0.030 },
    uFrame: { value: 0 },
    uLift: { value: new THREE.Color(0, 0, 0) },
    uSat: { value: 1.0 },
  },
  vertexShader: /* glsl */`
    varying vec2 vUv;
    void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }
  `,
  fragmentShader: /* glsl */`
    precision highp float;
    uniform sampler2D tDiffuse;
    uniform float uFlash; uniform vec3 uFlashColor;
    uniform float uCA; uniform float uVig; uniform float uGrain; uniform float uFrame;
    uniform vec3 uLift; uniform float uSat;
    varying vec2 vUv;

    float hash(vec2 p){ p = fract(p*vec2(123.34,456.21)); p += dot(p,p+45.32); return fract(p.x*p.y); }

    void main(){
      vec2 uv = vUv;
      vec2 d = uv - 0.5;
      float r2 = dot(d,d);
      // radial chromatic aberration, animated by uCA (px -> uv)
      float ca = uCA / 1920.0;
      vec3 col;
      col.r = texture2D(tDiffuse, uv + d*ca).r;
      col.g = texture2D(tDiffuse, uv).g;
      col.b = texture2D(tDiffuse, uv - d*ca).b;

      // per-act lift + saturation
      float l = dot(col, vec3(0.2126,0.7152,0.0722));
      col = mix(vec3(l), col, uSat);
      col += uLift;

      // vignette (smooth, never crushes the safe box)
      float vig = smoothstep(0.95, 0.25, r2*1.9);
      col *= mix(1.0 - uVig, 1.0, vig);

      // flash overlay (screen blend)
      col = mix(col, vec3(1.0), clamp(uFlash,0.0,1.0) * 0.88);
      col += uFlashColor * clamp(uFlash,0.0,1.0) * 0.12;

      // grain, deterministic per frame
      float g = hash(uv*vec2(1920.0,1080.0) + vec2(uFrame*37.7, uFrame*17.3)) - 0.5;
      col += g * uGrain;

      // ordered 4x4 Bayer dither to kill gradient banding in the voids
      float bx = mod(gl_FragCoord.x,4.0); float by = mod(gl_FragCoord.y,4.0);
      float bayer = mod(bx*4.0+by, 16.0)/16.0 - 0.5;
      col += bayer/255.0;

      gl_FragColor = vec4(col, 1.0);
    }
  `,
};

export function buildComposer(renderer, scene, camera) {
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(1920, 1080), 0.62, 0.72, 0.80);
  composer.addPass(bloom);
  composer.addPass(new OutputPass());
  const grade = new ShaderPass(GradeShader);
  grade.renderToScreen = true;
  composer.addPass(grade);
  return { composer, bloom, grade };
}
