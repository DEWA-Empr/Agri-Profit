// Warm-cache measurement via Lighthouse 13.4.1 user-flow (verified against the
// installed API). One browser session, two navigations:
//   nav1 = cold  (disableStorageReset:false -> storage reset, guaranteed cold)
//   nav2 = warm  (disableStorageReset:true  -> SW from nav1 survives, serves shell)
// Identical slow-3G simulate throttling on both. 3 iterations, fresh browser each.
import { startFlow } from 'file:///C:/Users/DELL/AppData/Roaming/npm/node_modules/lighthouse/core/index.js';
import puppeteer from 'file:///C:/Users/DELL/AppData/Roaming/npm/node_modules/lighthouse/node_modules/puppeteer-core/lib/puppeteer/puppeteer-core.js';
import fs from 'node:fs';

const URL = 'http://localhost:4173';
const CHROME = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe';
const OUT = 'C:/Users/DELL/AppData/Local/Temp/claude/C--Users-DELL-Desktop-Agri-P/39ceadfd-b14c-4e03-83fa-373773ad45c8/scratchpad/lighthouse';

const flags = {
  logLevel: 'error',
  throttlingMethod: 'simulate',
  throttling: { rttMs: 400, throughputKbps: 400, cpuSlowdownMultiplier: 4 },
};

const fcp = (lhr) => lhr.audits['first-contentful-paint'].numericValue / 1000;
const perf = (lhr) => Math.round(lhr.categories.performance.score * 100);
function mainJs(lhr) {
  const items = lhr.audits['network-requests'].details.items;
  return items.find((i) => /index-.*\.js(\?|$)/.test(i.url)) || null;
}

const results = [];
for (let iter = 1; iter <= 3; iter++) {
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: true,
    args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  const flow = await startFlow(page, { flags });

  await flow.navigate(URL, { name: `cold-${iter}`, disableStorageReset: false });

  // Let the service worker install + finish precaching before the warm nav.
  await page.evaluate(() => new Promise((res) => {
    if (!('serviceWorker' in navigator)) return res('no-sw');
    const t = setTimeout(() => res('timeout'), 8000);
    navigator.serviceWorker.ready.then(() => { clearTimeout(t); res('ready'); });
  })).catch(() => {});
  await new Promise((r) => setTimeout(r, 3000));

  await flow.navigate(URL, { name: `warm-${iter}`, disableStorageReset: true });

  const fr = await flow.createFlowResult();
  const cold = fr.steps[0].lhr;
  const warm = fr.steps[1].lhr;
  const wjs = mainJs(warm);
  results.push({
    iter,
    cold_fcp_s: +fcp(cold).toFixed(2),
    warm_fcp_s: +fcp(warm).toFixed(2),
    warm_perf: perf(warm),
    warm_mainjs_transfer: wjs ? wjs.transferSize : null,
    warm_mainjs_fromSW: wjs ? wjs.fromServiceWorker : null,
  });
  fs.writeFileSync(`${OUT}/flow-iter${iter}.json`, JSON.stringify(fr));
  await browser.close();
}
console.log(JSON.stringify(results, null, 2));
