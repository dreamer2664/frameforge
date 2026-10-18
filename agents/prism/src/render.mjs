// PRISM deterministic frame renderer (headless Chrome + SwiftShader).
//   node render.mjs --from 0 --to 749 --out frames/
//   node render.mjs --measure --from 0 --to 749 --out evidence/text_measures.json
//   node render.mjs --dump-events --out evidence/events.json
import puppeteer from 'puppeteer';
import path from 'node:path';
import fs from 'node:fs';
import { normalizePNG } from './pngnorm.mjs';
import { fileURLToPath } from 'node:url';
import { EVENTS } from './film/events.js';
import { encodePNG } from './png.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(process.argv.slice(2).map((a, i, arr) =>
  a.startsWith('--') ? [a.slice(2), arr[i + 1] && !arr[i + 1].startsWith('--') ? arr[i + 1] : true] : null
).filter(Boolean));

const from = parseInt(args.from ?? '0', 10);
const to = parseInt(args.to ?? '749', 10);
const only = args.only ? String(args.only).split(',').map((x) => parseInt(x, 10)) : null;
const out = args.out || 'frames/';
const measure = !!args.measure;
const dumpEvents = !!args['dump-events'];

if (dumpEvents) {
  fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
  fs.writeFileSync(out, JSON.stringify(EVENTS, null, 2));
  console.log(`events written: ${out} (${EVENTS.texts.length} texts, ${EVENTS.flashes.length} flashes, ${EVENTS.hits.length} hits)`);
  process.exit(0);
}

if (measure) fs.mkdirSync(path.dirname(path.resolve(out)) || '.', { recursive: true });
else fs.mkdirSync(out, { recursive: true });

const t0 = Date.now();
let done = 0;
const ALL_MEASURES = [];

const CHUNK = parseInt(args.chunk ?? '25', 10);

async function runChunk(cFrom, cTo) {
  const want = only || Array.from({ length: cTo - cFrom + 1 }, (_, k) => cFrom + k);
  const missing = want.filter((f) => {
    const fp = path.join(out, `f_${String(f).padStart(5, '0')}.png`);
    return !(fs.existsSync(fp) && fs.statSync(fp).size > 0);
  });
  if (!measure && missing.length === 0) { console.log(`chunk ${cFrom}..${cTo} complete — skip (no browser)`); return; }
  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
      '--disable-gpu-sandbox', '--use-gl=angle', '--use-angle=swiftshader',
      '--enable-unsafe-swiftshader', '--hide-scrollbars', '--mute-audio',
      '--force-color-profile=srgb', '--font-render-hinting=none',
      '--window-size=1920,1080',
    ],
  });
  try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  page.on('console', (m) => { if (m.type() === 'error') console.log('[page]', m.text()); });
  await page.goto('file://' + path.join(__dirname, 'film', 'page.html'), { waitUntil: 'load' });
  await page.waitForFunction('window.__film && window.__film.ready === true', { timeout: 120000 });
  // in-page PNG encode lives in page.js (no compositor readback: see D-B01)
  const diag = await page.evaluate(() => window.__film.diag);
  console.log('renderer:', diag.renderer, '|', diag.glVersion);

  const frames = only || Array.from({ length: cTo - cFrom + 1 }, (_, k) => cFrom + k);
  const measures = ALL_MEASURES;
  for (const f of frames) {
    if (measure) {
      const boxes = await page.evaluate((i) => window.__film.measure(i), f);
      measures.push({ frame: f, texts: boxes });
    } else {
      const fp = path.join(out, `f_${String(f).padStart(5, '0')}.png`);
      if (fs.existsSync(fp) && fs.statSync(fp).size > 0) { done++; continue; }  // resume-aware
      const lost = await page.evaluate((i) => {
        window.__film.renderFrame(i);
        return window.__film.dbg.renderer.getContext().isContextLost();
      }, f);
      if (lost) throw new Error(`WebGL context lost at frame ${f}`);
      const b64 = await page.evaluate(() => window.__grabPNG());
      fs.writeFileSync(fp, normalizePNG(Buffer.from(b64, 'base64')));  // deterministic bytes
    }
    done++;
    if (done % 25 === 0) {
      const el = (Date.now() - t0) / 1000;
      const rate = done / el;
      console.log(`  ${f} (${done}/${to - from + 1}) ${rate.toFixed(2)} f/s ETA ${(((to - from + 1) - done) / rate).toFixed(0)}s`);
    }
  }
  } finally {
    try { await page.close(); } catch {}
    try { await browser.close(); } catch {}
    try { browser.process()?.kill('SIGKILL'); } catch {}
  }
}

if (only) {
  await runChunk(only[0], only[only.length - 1]);
} else {
  for (let c = from; c <= to; c += CHUNK) {
    const cTo = Math.min(to, c + CHUNK - 1);
    console.log(`chunk ${c}..${cTo}`);
    await runChunk(c, cTo);
  }
}
if (measure) fs.writeFileSync(out, JSON.stringify(ALL_MEASURES, null, 1));
console.log(`DONE ${done} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s -> ${out}`);
