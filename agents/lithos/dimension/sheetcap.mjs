import { chromium } from 'playwright';
import { writeFileSync, mkdirSync } from 'fs';

const times = (process.env.TIMES ?? '1.2,3,5,7,9.5,11,13,15,17,19,21,24,27,29.5,32,34.5,36.5,38.5').split(',').map(Number);
const outdir = process.env.OUTDIR ?? '/tmp/r05-sheet';
mkdirSync(outdir, { recursive: true });

const browser = await chromium.launch({
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox']
});
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
page.on('pageerror', e => console.log('PAGEERROR', String(e).slice(0, 400)));
await page.goto('http://127.0.0.1:8765/film.html');
await page.waitForFunction('window.__ready === true', { timeout: 90000 });
await page.waitForTimeout(1500);
for (const t of times) {
  for (let w = -0.45; w < 0; w += 0.05) await page.evaluate((tt) => window.__seek(tt), Math.max(0, t + w));
  await page.evaluate((tt) => window.__seek(tt), t);
  const data = await page.evaluate(() => window.__shot());
  writeFileSync(`${outdir}/t${String(t).replace('.', '_')}.jpg`, Buffer.from(data.split(',')[1], 'base64'));
  console.log('t', t);
}
await browser.close();
