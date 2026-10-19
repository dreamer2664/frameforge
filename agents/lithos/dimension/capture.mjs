import { chromium } from 'playwright';
import { writeFileSync, mkdirSync } from 'fs';

const base = process.env.R05_BASE ?? 'http://127.0.0.1:8765';
const page_path = process.argv[2] ?? '/spike.html';
const outdir = process.argv[3] ?? '/tmp/r05-spike';
const n = parseInt(process.argv[4] ?? '10', 10);
mkdirSync(outdir, { recursive: true });

const browser = await chromium.launch({
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox']
});
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
const t0 = Date.now();
await page.goto(base + page_path);
await page.waitForFunction('window.__ready === true', { timeout: 60000 });
console.log('loaded_ms', Date.now() - t0);
await page.waitForTimeout(600); // font + first compile

for (let i = 0; i < n; i++) {
  const s = Date.now();
  await page.evaluate((t) => window.__seek(t), i * 0.5);
  const data = await page.evaluate(() => window.__shot());
  writeFileSync(`${outdir}/${String(i).padStart(4, '0')}.jpg`, Buffer.from(data.split(',')[1], 'base64'));
  console.log('frame', i, 'ms', Date.now() - s);
}
await browser.close();
