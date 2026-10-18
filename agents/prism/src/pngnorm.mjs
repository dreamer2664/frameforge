// pngnorm.mjs — deterministic PNG byte normalization.
//
// WHY: the in-page encoder uses Chrome's CompressionStream('deflate'), whose
// output bytes depend on worker scheduling (same pixels, different IDAT bytes
// per session — caught by RENDER_DETERMINISM). Pixel data is fully
// deterministic; only the deflate byte stream was not. This module re-wraps
// the decompressed scanlines with Node's zlib (single-threaded, version-pinned
// in TECHNICAL_RECEIPT), making PNG bytes a pure function of pixels.
//
// Usage: node pngnorm.mjs <dir>   — normalize every f_*.png in place.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

export function crc32(buf) { return zlib.crc32(buf) >>> 0; }

function chunksOf(buf) {
  const out = [];
  let i = 8;
  while (i < buf.length) {
    const len = buf.readUInt32BE(i);
    const type = buf.toString('latin1', i + 4, i + 8);
    out.push({ type, data: buf.subarray(i + 8, i + 8 + len) });
    i += 12 + len;
  }
  return out;
}

function mkChunk(type, data) {
  const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
  const td = Buffer.concat([Buffer.from(type, 'latin1'), data]);
  const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(td));
  return Buffer.concat([len, td, crc]);
}

/** Decode raw scanlines (filter bytes included) from a PNG buffer. */
export function rawScanlines(buf) {
  const idat = Buffer.concat(chunksOf(buf).filter(c => c.type === 'IDAT').map(c => c.data));
  return zlib.inflateSync(idat);
}

/** Build a deterministic PNG from raw scanlines + IHDR of the source. */
export function normalizePNG(buf) {
  const cs = chunksOf(buf);
  const ihdr = cs.find(c => c.type === 'IHDR').data;
  const raw = rawScanlines(buf);
  const def = zlib.deflateSync(raw, { level: 6 });
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    mkChunk('IHDR', ihdr), mkChunk('IDAT', def), mkChunk('IEND', Buffer.alloc(0)),
  ]);
}

import { fileURLToPath } from 'node:url';
if (process.argv[1] && process.argv[1].endsWith('pngnorm.mjs')) {
  const dir = process.argv[2];
  const files = fs.readdirSync(dir).filter(f => /^f_\d{5}\.png$/.test(f)).sort();
  let changed = 0;
  for (const f of files) {
    const p = path.join(dir, f);
    const src = fs.readFileSync(p);
    const out = normalizePNG(src);
    if (!out.equals(src)) { fs.writeFileSync(p, out); changed++; }
  }
  console.log(`[pngnorm] ${files.length} frames, ${changed} re-wrapped deterministically`);
}
