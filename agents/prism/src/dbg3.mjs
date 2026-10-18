import puppeteer from 'puppeteer';
import path from 'node:path';
const b = await puppeteer.launch({ headless: true, args: ['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-sandbox'] });
const p = await b.newPage();
await p.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
p.on('console', m => { const t = m.text(); if (/lost|OOM|memory|ERROR|fatal/i.test(t)) console.log('[page]', t.slice(0,160)); });
await p.goto('file://' + path.resolve('film/page.html'), { waitUntil: 'load' });
await p.waitForFunction('window.__film && window.__film.ready === true', { timeout: 120000 });
const seq = [450,455,460,465,470,475,478,479,480,481,482,483,485,490,495,500,660,670,700,749];
for (const f of seq) {
  const st = await p.evaluate((i) => {
    const F = window.__film.dbg;
    try { F.renderFrame(i); } catch (e) { return { err: String(e).slice(0,140) }; }
    return { lost: F.renderer.getContext().isContextLost() };
  }, f);
  console.log(f, JSON.stringify(st));
  if (st.lost || st.err) break;
}
await b.close();
