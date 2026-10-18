import puppeteer from 'puppeteer';
import path from 'node:path';
import fs from 'node:fs';
const b = await puppeteer.launch({ headless: true, args: ['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-sandbox'] });
const p = await b.newPage();
await p.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
p.on('console', m => console.log('[page]', m.type(), m.text().slice(0,200)));
p.on('pageerror', e => console.log('[pageerror]', e.message));
await p.goto('file://' + path.resolve('film/page.html'), { waitUntil: 'load' });
await p.waitForFunction('window.__film && window.__film.ready === true', { timeout: 120000 });
await p.evaluate(() => {
  const c = document.getElementById('c');
  c.addEventListener('webglcontextlost', () => console.log('CONTEXT LOST'));
  c.addEventListener('webglcontextrestored', () => console.log('CONTEXT RESTORED'));
});
const only = (process.argv[2] || '500').split(',').map(Number);
const canvas = await p.$('#c');
for (const f of only) {
  const st = await p.evaluate((i) => {
    const F = window.__film.dbg;
    F.renderFrame(i);
    const gl = F.renderer.getContext();
    return { lost: gl.isContextLost(), mem: { ...F.renderer.info.memory }, calls: F.renderer.info.render.calls };
  }, f);
  console.log('frame', f, JSON.stringify(st));
  await canvas.screenshot({ path: `styleframes/iso_${f}.png` });
  console.log('  bytes', fs.statSync(`styleframes/iso_${f}.png`).size);
}
await b.close();
