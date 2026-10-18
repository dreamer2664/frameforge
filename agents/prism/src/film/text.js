// PRISM typography — screen-space orthographic overlay.
// 1 overlay unit = 1 screen pixel, so cap-heights and title-safe margins are
// exact by construction and measurable analytically (see TEXT_LOG.md).
import * as THREE from 'three';
import { W, H, SAFE } from './constants.js';
import { ease, inv, clamp, lerp, pad } from './util.js';
import { TEXTS } from './events.js';

import fDisplay from './fonts/archivo-black-latin-400-normal.woff2';
import fMono400 from './fonts/ibm-plex-mono-latin-400-normal.woff2';
import fMono500 from './fonts/ibm-plex-mono-latin-500-normal.woff2';
import fMono600 from './fonts/ibm-plex-mono-latin-600-normal.woff2';
import fMono700 from './fonts/ibm-plex-mono-latin-700-normal.woff2';

export const FONT_FAMILIES = { display: '"PRISM Display"', mono: '"PRISM Mono"' };
// measured cap/em ratios for the two locked faces (see RIGHTS.md measurement note)
const CAP_RATIO = { display: 0.72, mono: 0.70 };
const SS = 4; // supersample factor for glyph textures

export async function loadFonts() {
  const specs = [
    ['PRISM Display', fDisplay, 400],
    ['PRISM Mono', fMono400, 400],
    ['PRISM Mono', fMono500, 500],
    ['PRISM Mono', fMono600, 600],
    ['PRISM Mono', fMono700, 700],
  ];
  const faces = specs.map(([fam, url, w]) => new FontFace(fam, `url(${url})`, { weight: String(w) }));
  const loaded = await Promise.all(faces.map((f) => f.load()));
  loaded.forEach((f) => document.fonts.add(f));
  await document.fonts.ready;
  return true;
}

function glyphTexture(ch, family, weight, fontPx) {
  // adaptive supersample: huge glyphs need less headroom (memory cap, D-B02)
  const ss = fontPx > 150 ? 2 : SS;
  const cv = document.createElement('canvas');
  const meas = document.createElement('canvas').getContext('2d');
  meas.font = `${weight} ${fontPx * ss}px ${FONT_FAMILIES[family]}`;
  const adv4 = meas.measureText(ch).width;
  const adv = adv4 / ss;                       // css-px advance (screen px)
  const boxW = Math.ceil(adv) + fontPx * 0.9;  // css px
  const boxH = Math.ceil(fontPx * 1.7);        // css px
  cv.width = Math.max(2, Math.ceil(boxW * ss));
  cv.height = Math.ceil(boxH * ss);
  const g = cv.getContext('2d');
  g.font = `${weight} ${fontPx * ss}px ${FONT_FAMILIES[family]}`;
  g.textAlign = 'center';
  g.textBaseline = 'middle';
  g.fillStyle = '#ffffff';
  g.fillText(ch, cv.width / 2, cv.height / 2);
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.minFilter = THREE.LinearMipmapLinearFilter;
  tex.magFilter = THREE.LinearFilter;
  tex.anisotropy = 2;
  tex.generateMipmaps = true;
  return { tex, boxW, boxH, adv };
}

class TextEvent {
  constructor(def) {
    this.def = def;
    this.group = new THREE.Group();
    this.chars = [];
    const family = def.family;
    const fontPx = def.cap / CAP_RATIO[family];
    this.fontPx = fontPx;
    const track = def.tracking || 0;

    if (def.mode === 'counter') {
      const { tex, boxW, boxH } = glyphTexture('FRAME 000/750', family, def.weight, fontPx, true);
      this.counterTex = tex;
      this.counterCv = tex.image;
      this.counterCtx = this.counterCv.getContext('2d');
      this.counterW = boxW; this.counterH = boxH;
      const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthTest: false, toneMapped: false, side: THREE.DoubleSide });
      this.plane = new THREE.Mesh(new THREE.PlaneGeometry(boxW, boxH), mat);
      this.group.add(this.plane);
      this.lastCount = -1;
    } else {
      const chars = [...def.str];
      // layout with base tracking (animated tracking is added at update time)
      const widths = chars.map((c) => {
        const g = glyphTexture(c, family, def.weight, fontPx);
        return g;
      });
      // space handling: invisible but advances
      let total = 0;
      chars.forEach((c, i) => { total += widths[i].adv; });
      total += track * (chars.length - 1);
      this.baseTotal = total;
      let cursor = 0;
      chars.forEach((c, i) => {
        const g = widths[i];
        const mat = new THREE.MeshBasicMaterial({ map: g.tex, transparent: true, depthTest: false, toneMapped: false, side: THREE.DoubleSide });
        const m = new THREE.Mesh(new THREE.PlaneGeometry(g.boxW, g.boxH), mat);
        m.userData = { adv: g.adv, space: c === ' ', idx: i, boxW: g.boxW, boxH: g.boxH };
        this.chars.push(m);
        this.group.add(m);
        cursor += m.userData.adv;
      });
      this.widths = widths;
    }
    this.group.renderOrder = 10;
    this.color = new THREE.Color(def.color);
    this.applyColor();
  }

  applyColor() {
    const targets = this.plane ? [this.plane] : this.chars;
    targets.forEach((m) => m.material.color.copy(this.color));
  }

  redrawCounter(n) {
    const g = this.counterCtx;
    const cv = this.counterCv;
    g.clearRect(0, 0, cv.width, cv.height);
    g.font = `${this.def.weight} ${this.fontPx * SS}px ${FONT_FAMILIES[this.def.family]}`;
    g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillStyle = '#ffffff';
    g.fillText(`FRAME ${pad(n, 3)}/750`, cv.width / 2, cv.height / 2);
    this.counterTex.needsUpdate = true;
  }

  // per-char visibility/opacity for the designed motion modes
  update(f) {
    const d = this.def;
    const vis = f >= d.in && f <= d.out;
    this.group.visible = vis;
    if (!vis) return null;

    const inP = inv(f, d.in, d.in + 10);
    const outP = inv(f, d.out - 6, d.out);
    const aOut = 1 - ease.inCubic(outP);
    let alpha = ease.outCubic(inP) * aOut;

    if (d.mode === 'type') {
      const per = 2.2;
      this.chars.forEach((m, i) => {
        const on = f >= d.in + i * per;
        m.material.opacity = on ? aOut : 0;
        m.visible = on;
      });
      alpha = aOut; // per-char handled, group exit fade kept
    } else if (d.mode === 'stab') {
      alpha = f <= d.out ? 1 : 0;
      alpha *= inv(f, d.in, d.in + 1);
      this.chars.forEach((m) => { m.material.opacity = alpha; });
    } else if (d.mode === 'slam') {
      this.chars.forEach((m) => { m.material.opacity = inv(f, d.in, d.in + 2); });
    } else {
      this.chars.forEach((m) => { m.material.opacity = alpha; });
    }
    if (this.plane) this.plane.material.opacity = d.mode === 'counter' ? inv(f, d.in, d.in + 6) * (1 - ease.inCubic(outP)) : alpha;

    // horizontal layout with animated tracking + per-mode offsets
    let track = d.tracking || 0;
    let scale = 1, dy = 0, dx = 0;
    if (d.mode === 'track') {
      track = lerp(d.tracking || 0, 0, ease.inOutQuint(inv(f, d.in, d.in + 20)));
      dy = lerp(14, 0, ease.outQuint(inv(f, d.in, d.in + 16)));
      const o = inv(f, d.out - 8, d.out);
      track = lerp(track, (d.tracking || 0) * 0.6, ease.inCubic(o));
    } else if (d.mode === 'slam') {
      scale = lerp(1.2, 1, ease.outExpo(inv(f, d.in, d.in + 9)));
      track = lerp(8, 0, ease.outQuint(inv(f, d.in, d.in + 12)));
    } else if (d.mode === 'stab') {
      dy = lerp(8, 0, ease.outQuint(inv(f, d.in, d.in + 5)));
    }

    if (d.mode === 'counter') {
      const n = clamp(Math.round((f - 196) / (442 - 196) * 750), 0, 750);
      if (n !== this.lastCount) { this.redrawCounter(n); this.lastCount = n; }
      this.plane.scale.set(scale, scale, 1);
      this.placeSingle(d, dx, dy);
      return this.bboxSingle(d, dx, dy);
    }

    const chars = this.chars;
    let total = 0;
    chars.forEach((m) => { total += m.userData.adv; });
    total += track * (chars.length - 1);
    let cursor = d.anchor === 'center' ? -total / 2 : d.anchor === 'right' ? -total : 0;
    chars.forEach((m, i) => {
      const u = m.userData;
      const cx = cursor + u.adv / 2;
      // scale is applied about the line's anchor so bbox(total*scale) stays true
      m.position.set(d.x + cx * scale + dx, H - (d.y + dy), 0);
      m.scale.set(scale, scale, 1);
      cursor += u.adv + track;
    });
    return this.bbox(d, total, dx, dy, scale);
  }

  placeSingle(d, dx, dy) {
    const w = this.counterW;
    const cx = d.anchor === 'right' ? d.x - w / 2 : d.anchor === 'center' ? d.x : d.x + w / 2;
    this.plane.position.set(cx + dx, H - (d.y + dy), 0);
  }
  bboxSingle(d, dx, dy) {
    const w = this.counterW, h = d.cap;
    const cx = d.anchor === 'right' ? d.x - w / 2 : d.anchor === 'center' ? d.x : d.x + w / 2;
    return { id: d.id, x0: cx - w / 2 + dx, x1: cx + w / 2 + dx, y0: d.y - h / 2 + dy, y1: d.y + h / 2 + dy };
  }

  // analytic screen-space bbox of the inked line at this frame (px, y-down)
  bbox(d, total, dx, dy, scale) {
    const h = d.cap * scale;
    const left = d.anchor === 'center' ? d.x - (total * scale) / 2 : d.anchor === 'right' ? d.x - total * scale : d.x;
    return { id: d.id, x0: left + dx, x1: left + total * scale + dx, y0: d.y - h / 2 + dy, y1: d.y + h / 2 + dy };
  }
}

export class TypeLayer {
  constructor() {
    this.scene = new THREE.Scene();
    this.cam = new THREE.OrthographicCamera(0, W, H, 0, -10, 10); // y-up; pixel y converted at placement
    this.cam.position.z = 5;
    this.events = TEXTS.map((t) => new TextEvent(t));
    this.events.forEach((e) => this.scene.add(e.group));
    this.receipt = this.buildReceipt();
    this.scene.add(this.receipt.group);
  }

  // Act IV receipt body — sub-rows of the T10 moment, revealed row by row.
  buildReceipt() {
    const group = new THREE.Group();
    // paper panel (screen-space), fades/slides in ahead of the rows
    const panel = new THREE.Mesh(
      new THREE.PlaneGeometry(960, 640),
      new THREE.MeshBasicMaterial({ color: 0xf2efe9, transparent: true, depthTest: false, toneMapped: false, side: THREE.DoubleSide })
    );
    panel.position.set(960, H - 550, -1);
    panel.renderOrder = 4;
    panel.visible = false;
    group.add(panel);
    const rule = new THREE.Mesh(
      new THREE.PlaneGeometry(960, 5),
      new THREE.MeshBasicMaterial({ color: 0xff8a00, transparent: true, depthTest: false, toneMapped: false, side: THREE.DoubleSide })
    );
    rule.position.set(960, H - 244, -0.5);
    rule.renderOrder = 5;
    rule.visible = false;
    group.add(rule);
    this.panel = panel; this.rule = rule;
    const lines = [
      'PRISM / PROOF',
      '25.00 S · 750 FRAMES · 30 FPS',
      '1920×1080 · H.264 · AAC 48K',
      'COMMISSION SHA F29F865C…',
      'SEED 0x50524F4F · ENV-B',
      '2026-10-18 · EUROPE/ROME',
    ];
    const cap = 36, fontPx = cap / CAP_RATIO.mono, lh = 56;
    const planes = [];
    lines.forEach((ln, i) => {
      const g = glyphTexture(ln, 'mono', i === 0 ? 700 : 500, fontPx, true);
      const mat = new THREE.MeshBasicMaterial({ map: g.tex, transparent: true, depthTest: false, toneMapped: false, side: THREE.DoubleSide });
      mat.color.set(i === 0 ? '#141210' : '#3a352e');
      const m = new THREE.Mesh(new THREE.PlaneGeometry(g.boxW, g.boxH), mat);
      m.position.set(510 + g.boxW / 2, H - (376 + i * lh), 0);
      m.renderOrder = 6 + i;
      m.visible = false;
      group.add(m);
      planes.push({ m, w: g.boxW, i });
    });
    return { group, planes, in: 672, per: 7, panel, rule };
  }

  update(f) {
    const boxes = [];
    for (const e of this.events) {
      const b = e.update(f);
      if (b && e.group.visible) boxes.push(b);
    }
    // receipt rows
    const R = this.receipt;
    const pIn = inv(f, 660, 672);   // revealed under F6 burst cover (FLASH_LOG)
    R.panel.visible = f >= 660 && f <= 749;
    R.rule.visible = R.panel.visible;
    if (R.panel.visible) {
      const e1 = ease.outQuint(pIn);
      R.panel.material.opacity = e1;
      R.rule.material.opacity = e1;
      R.panel.scale.setScalar(lerp(1.03, 1, e1));
      R.panel.position.y = H - (550 + lerp(10, 0, e1));
      R.rule.position.y = H - (244 + lerp(10, 0, e1));
    }
    R.planes.forEach((p) => {
      const on = f >= R.in + p.i * R.per;
      const off = f > 749;
      p.m.visible = on && !off;
      if (p.m.visible) {
        const t = inv(f, R.in + p.i * R.per, R.in + p.i * R.per + 5);
        p.m.material.opacity = ease.outCubic(t);
        p.m.position.x = 510 + p.w / 2 + lerp(-6, 0, ease.outQuint(t));
      }
    });
    if (f >= R.in) {
      const last = Math.min(R.planes.length - 1, Math.floor((f - R.in) / R.per));
      const w = R.planes[last].w;
      boxes.push({ id: 'T10.body', x0: 510, x1: 510 + w, y0: 376 - 26, y1: 376 + last * 56 + 26 });
    }
    return boxes;
  }
}
