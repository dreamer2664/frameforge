import puppeteer from 'puppeteer';
import path from 'node:path';
import fs from 'node:fs';
const b = await puppeteer.launch({ headless: true, args: ['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-sandbox'] });
const p = await b.newPage();
await p.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
p.on('pageerror', e => console.log('[pageerror]', e.message));
await p.goto('file://' + path.resolve('film/page.html'), { waitUntil: 'load' });
await p.waitForFunction('window.__film && window.__film.ready === true', { timeout: 120000 });
const r = await p.evaluate(async () => {
  const F = window.__film.dbg;
  const gl = F.renderer.getContext();
  const inkAt = (x, yTop) => { const px = new Uint8Array(4); gl.readPixels(x, 1080 - yTop, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); return Array.from(px); };
  F.renderFrame(60);
  const after = inkAt(220, 540);
  // manual overlay render on top, then sample again
  F.renderer.autoClear = false; F.renderer.clearDepth();
  F.renderer.render(F.type.scene, F.type.cam);
  F.renderer.autoClear = true;
  const manual = inkAt(220, 540);
  const err = gl.getError();
  // what does the overlay alone look like? render to a fresh RT
  const rt = new (Object.getPrototypeOf(F.composer.renderTarget1).constructor)(1920, 1080);
  F.renderer.setRenderTarget(rt);
  F.renderer.setClearColor(0x000000, 1);
  F.renderer.clear();
  F.renderer.render(F.type.scene, F.type.cam);
  const px = new Uint8Array(4);
  F.renderer.readRenderTargetPixels(rt, 220, 540, 1, 1, px);
  const rtSample = Array.from(px);
  F.renderer.setRenderTarget(null);
  return { after, manual, err, rtSample };
});
console.log(JSON.stringify(r));
await b.close();
