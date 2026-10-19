import { chromium } from 'playwright';
import { writeFileSync } from 'fs';
const browser = await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-sandbox']});
const page = await browser.newPage({viewport:{width:1080,height:1920}});
await page.goto('http://127.0.0.1:8765/film.html');
await page.waitForFunction('window.__ready === true', {timeout:90000});
await page.waitForTimeout(1200);
for (const t of [24, 27]) {
  await page.evaluate((tt) => window.__seek(tt), t);
  const data = await page.evaluate(() => window.__shot());
  writeFileSync(`/tmp/probe-t${t}.jpg`, Buffer.from(data.split(',')[1],'base64'));
  const vis = await page.evaluate(() => ({
    fin: window.__objs.finale.visible, tag: window.__objs.finale.children.map(c=>c.visible||c.type)
  }));
  console.log(t, JSON.stringify(vis));
}
await browser.close();
