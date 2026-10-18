import { createFilm } from './film.js';
import { EVENTS } from './events.js';

(async () => {
  const canvas = document.getElementById('c');
  const film = await createFilm(canvas);
  window.__film = {
    ready: true,
    events: EVENTS,
    diag: film.diag,
    renderFrame: (i) => { film.renderFrame(i); return true; },
    measure: (i) => { film.renderFrame(i); return film.measure(); },
    dbg: film,
  };

  // ---- in-page deterministic PNG encode (readPixels + own CRC/deflate) ----
  const CRCT = (() => { const t = new Int32Array(256);
    for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c; }
    return t; })();
  const crc32 = (b) => { let c = -1; for (let i = 0; i < b.length; i++) c = CRCT[(c ^ b[i]) & 0xff] ^ (c >>> 8); return (c ^ -1) >>> 0; };
  const chunk = (type, data) => {
    const len = new Uint8Array(4); new DataView(len.buffer).setUint32(0, data.length);
    const td = new Uint8Array(type.length + data.length);
    for (let i = 0; i < type.length; i++) td[i] = type.charCodeAt(i);
    td.set(data, type.length);
    const cr = new Uint8Array(4); new DataView(cr.buffer).setUint32(0, crc32(td));
    const o = new Uint8Array(4 + td.length + 4); o.set(len); o.set(td, 4); o.set(cr, 4 + td.length);
    return o;
  };
  const cat = (arrs) => { let n = 0; for (const a of arrs) n += a.length; const o = new Uint8Array(n); let p = 0; for (const a of arrs) { o.set(a, p); p += a.length; } return o; };

  window.__grabPNG = async () => {
    const F = window.__film.dbg;
    const gl = F.renderer.getContext();
    const w = gl.drawingBufferWidth, h = gl.drawingBufferHeight;
    if (!window.__px || window.__px.length !== w * h * 4) window.__px = new Uint8Array(w * h * 4);
    gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, window.__px);
    const row = w * 4;
    if (!window.__raw || window.__raw.length !== (row + 1) * h) window.__raw = new Uint8Array((row + 1) * h);
    const raw = window.__raw;
    for (let y = 0; y < h; y++) {
      raw[y * (row + 1)] = 0;
      raw.set(window.__px.subarray((h - 1 - y) * row, (h - 1 - y) * row + row), y * (row + 1) + 1);
    }
    const ds = new CompressionStream('deflate');
    const wr = ds.writable.getWriter();
    wr.write(raw); wr.close();
    const def = new Uint8Array(await new Response(ds.readable).arrayBuffer());
    const ihdr = new Uint8Array(13);
    const dv = new DataView(ihdr.buffer);
    dv.setUint32(0, w); dv.setUint32(4, h); ihdr[8] = 8; ihdr[9] = 6;
    const png = cat([
      new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
      chunk('IHDR', ihdr), chunk('IDAT', def), chunk('IEND', new Uint8Array(0)),
    ]);
    let s = ''; const CH = 0x8000;
    for (let i = 0; i < png.length; i += CH) s += String.fromCharCode.apply(null, png.subarray(i, i + CH));
    return btoa(s);
  };
})();
