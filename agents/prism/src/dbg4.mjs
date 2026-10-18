import puppeteer from 'puppeteer';
import path from 'node:path';
import fs from 'node:fs';
const b = await puppeteer.launch({ headless: true, args: ['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-sandbox'] });
const p = await b.newPage();
await p.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
p.on('console', m => { const t = m.text(); if (/lost|ERROR/i.test(t)) console.log('[page]', t.slice(0,120)); });
await p.goto('file://' + path.resolve('film/page.html'), { waitUntil: 'load' });
await p.waitForFunction('window.__film && window.__film.ready === true', { timeout: 120000 });
for (const f of [500, 700]) {
  const r = await p.evaluate((i) => {
    const F = window.__film.dbg;
    F.renderFrame(i);
    const gl = F.renderer.getContext();
    // method B: in-page toDataURL
    let url = null, err = null;
    try { url = F.renderer.domElement.toDataURL('image/png'); } catch (e) { err = String(e); }
    // method C: readPixels stats
    const px = new Uint8Array(4 * 64);
    gl.readPixels(960 - 4, 540, 8, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
    let max = 0; for (let k = 0; k < px.length; k++) max = Math.max(max, px[k]);
    return { lost: gl.isContextLost(), urlLen: url ? url.length : 0, err, maxRow: max };
  }, f);
  console.log('frame', f, JSON.stringify({ lost: r.lost, urlLen: r.urlLen, err: r.err, maxRow: r.maxRow }));
  if (r.urlLen) {
    const buf = Buffer.from(r.urlLen ? await p.evaluate((i) => window.__film.dbg.renderer.domElement.toDataURL('image/png').split(',')[1], f) : '', 'base64');
    fs.writeFileSync(`styleframes/durl_${f}.png`, buf);
    console.log('  durl bytes', buf.length);
  }
}
await b.close();
