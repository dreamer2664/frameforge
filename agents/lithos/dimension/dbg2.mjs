import { chromium } from 'playwright';
import { writeFileSync } from 'fs';
const browser = await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-sandbox']});
const page = await browser.newPage({viewport:{width:1080,height:1920}});
await page.goto('http://127.0.0.1:8765/film.html');
await page.waitForFunction('window.__ready === true', {timeout:90000});
await page.waitForTimeout(1200);
await page.evaluate(() => window.__seek(9.5));
const state = await page.evaluate(() => {
  const o = window.__objs, out = {};
  for (const k in o) { const v = o[k]; out[k] = (v && v.visible !== undefined) ? v.visible : (v && v.length !== undefined ? 'grp' : '?'); }
  out['knot.scale'] = window.__objs.knot.scale.x;
  out['knot.opacity'] = window.__objs.knot.material.opacity;
  return out;
});
console.log(JSON.stringify(state));
await page.evaluate(() => { window.__objs.knot.visible = false; window.__seek(9.5); window.__objs.knot.visible = false; });
let data = await page.evaluate(() => window.__shot());
writeFileSync('/tmp/probe-noknot.jpg', Buffer.from(data.split(',')[1],'base64'));
await browser.close();
