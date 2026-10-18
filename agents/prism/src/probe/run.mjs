// PRISM feasibility probe: launch headless Chrome, verify WebGL is real,
// render N frames at 1920x1080 through the same code path the film will use,
// and measure per-frame wall clock. Prints no secrets, touches no network.
import puppeteer from 'puppeteer';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import fs from 'node:fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.join(__dirname, 'out');
fs.mkdirSync(outDir, { recursive: true });

const FRAMES = [0, 1, 123, 456, 749];

const browser = await puppeteer.launch({
  headless: true,
  args: [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu-sandbox',
    '--use-gl=angle',
    '--use-angle=swiftshader',
    '--enable-unsafe-swiftshader',
    '--hide-scrollbars',
    '--mute-audio',
    '--force-color-profile=srgb',
    '--font-render-hinting=none',
    '--window-size=1920,1080',
  ],
});

try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  page.on('console', (m) => console.log('[page]', m.text()));
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));

  const t0 = Date.now();
  await page.goto('file://' + path.join(__dirname, 'page.html'), { waitUntil: 'load' });
  await page.waitForFunction('window.__ready === true', { timeout: 60000 });
  console.log('boot+init ms:', Date.now() - t0);

  const diag = await page.evaluate(() => window.__probe.diag);
  const threeRev = await page.evaluate(() => window.__probe.three);
  console.log('three r' + threeRev, '| GL:', diag.glVersion, '| vendor:', diag.vendor, '| renderer:', diag.renderer, '| maxTex:', diag.maxTex);

  const canvas = await page.$('#c');
  for (const f of FRAMES) {
    const a = process.hrtime.bigint();
    await page.evaluate((i) => window.__probe.renderFrame(i), f);
    const b = process.hrtime.bigint();
    const p = path.join(outDir, `probe_${String(f).padStart(5, '0')}.png`);
    await canvas.screenshot({ path: p, captureBeyondViewport: false });
    const c = process.hrtime.bigint();
    const st = fs.statSync(p);
    console.log(
      `frame ${String(f).padStart(3)} render=${Number(b - a) / 1e6}ms shot=${Number(c - b) / 1e6}ms bytes=${st.size}`
    );
  }
  const info = await page.evaluate(() => window.__probe.info());
  console.log('render info:', JSON.stringify(info));
} finally {
  await browser.close();
}
