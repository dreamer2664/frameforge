import { chromium } from 'playwright';
import { writeFileSync, mkdirSync } from 'fs';

const outdir = '/tmp/r05-frames';
mkdirSync(outdir, { recursive: true });
const start = parseInt(process.argv[2] ?? '0', 10);
const end = parseInt(process.argv[3] ?? '1200', 10);

const browser = await chromium.launch({
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox']
});
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
page.on('pageerror', e => { console.log('PAGEERROR', String(e).slice(0, 300)); process.exit(1); });
await page.goto('http://127.0.0.1:8765/film.html');
await page.waitForFunction('window.__ready === true', { timeout: 90000 });
await page.waitForTimeout(1500);
const t0 = Date.now();
for (let f = start; f < end; f++) {
  await page.evaluate((t) => window.__seek(t), f / 30);
  const data = await page.evaluate(() => window.__shot());
  writeFileSync(`${outdir}/${String(f).padStart(4, '0')}.jpg`, Buffer.from(data.split(',')[1], 'base64'));
  if ((f - start) % 100 === 99) {
    const el = (Date.now() - t0) / 1000;
    console.log('frames', f + 1, 'elapsed_s', Math.round(el), 'per_frame_s', (el / (f + 1 - start)).toFixed(2));
  }
}
console.log('RENDER_DONE', end - start, 'frames');
await browser.close();
