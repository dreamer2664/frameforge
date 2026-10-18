import puppeteer from 'puppeteer';
import path from 'node:path';
const b = await puppeteer.launch({ headless: true, args: ['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-sandbox'] });
const p = await b.newPage();
await p.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
p.on('pageerror', e => console.log('[pageerror]', e.message));
await p.goto('file://' + path.resolve('film/page.html'), { waitUntil: 'load' });
await p.waitForFunction('window.__film && window.__film.ready === true', { timeout: 120000 });
const r = await p.evaluate(() => {
  const F = window.__film.dbg;
  const t1 = F.type.events.find(e => e.def.id === 'T1');
  const t2 = F.type.events.find(e => e.def.id === 'T2');
  const probe = (ev) => {
    const m = ev.chars[0];
    const img = m.material.map.image;
    const g = img.getContext('2d');
    const d = g.getImageData(0, 0, img.width, img.height).data;
    let ink = 0; for (let i = 3; i < d.length; i += 40) if (d[i] > 8) ink++;
    return { canvas: [img.width, img.height], inkSamples: ink, geo: m.geometry.parameters, pos: m.position.toArray().map(v=>+v.toFixed(1)), op: m.material.opacity, vis: m.visible, grpVis: ev.group.visible };
  };
  F.renderFrame(60);
  return { t1: probe(t1), t2: probe(t2), overlayChildren: F.type.scene.children.length,
           camType: [F.type.cam.left, F.type.cam.right, F.type.cam.top, F.type.cam.bottom, F.type.cam.near, F.type.cam.far, F.type.cam.position.z] };
});
console.log(JSON.stringify(r, null, 1));
await b.close();
