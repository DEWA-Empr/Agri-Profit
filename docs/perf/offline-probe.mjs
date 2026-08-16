// Service-worker attribution probe.
//
// Settles a question the Lighthouse runs could not: when the second load is
// fast, is it served by the service worker, or merely by Chrome's HTTP disk
// cache? Lighthouse never marked the warm requests `fromServiceWorker`, so the
// flow artifacts alone cannot distinguish the two.
//
// Method: drive a real browser, inspect the CacheStorage from page context,
// then disconnect the network and perform a FULL navigation. A navigation that
// returns 200 with `response.fromServiceWorker() === true` while the network is
// unreachable is served by the service worker, by construction.
//
// Two traps this script is written to avoid:
//   1. `navigator.onLine` reports **true** in the document created by an
//      emulated-offline navigation. It is not evidence of connectivity and is
//      ignored here.
//   2. "The navigation succeeded" is only meaningful if the network was really
//      down. Every offline phase is therefore bracketed by CONTROL fetches to
//      deliberately non-precached URLs, which must reject.
//
// Prerequisite — the production frontend must be up (the dev server registers
// no service worker):
//     docker compose --profile prod up -d --build frontend-prod
// Run:
//     node docs/perf/offline-probe.mjs
//
// Paths below are absolute to the machine the measurements were taken on;
// adjust CHROME and PUPPETEER before re-running elsewhere.

import puppeteer from 'file:///C:/Users/DELL/AppData/Roaming/npm/node_modules/lighthouse/node_modules/puppeteer-core/lib/puppeteer/puppeteer-core.js';

const URL_ = 'http://localhost:4173';
const CHROME = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe';

const out = (label, v) =>
  console.log(`${label}: ${typeof v === 'string' ? v : JSON.stringify(v, null, 2)}`);

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: true,
  args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
});
const page = await browser.newPage();

const consoleMsgs = [];
const pageErrors = [];
const failedReqs = [];
page.on('console', (m) => consoleMsgs.push({ type: m.type(), text: m.text() }));
page.on('pageerror', (e) => pageErrors.push(String(e.message || e)));
page.on('requestfailed', (r) => failedReqs.push({ url: r.url(), err: r.failure()?.errorText }));

const verdict = {};

// ---------------------------------------------------------------- (a) cold
console.log('=== (a) COLD NAVIGATION + SERVICE-WORKER REGISTRATION ===');
const resp1 = await page.goto(URL_, { waitUntil: 'load', timeout: 60000 });
out('http status', resp1.status());

out('serviceWorker.ready', await page.evaluate(() => new Promise((res) => {
  if (!('serviceWorker' in navigator)) return res('no-serviceWorker-api');
  const t = setTimeout(() => res('TIMEOUT-8s'), 8000);
  navigator.serviceWorker.ready
    .then((reg) => { clearTimeout(t); res(`ready scope=${reg.scope} active=${reg.active?.state}`); })
    .catch((e) => { clearTimeout(t); res('error: ' + e.message); });
})));

// clientsClaim needs a moment to take control of the already-loaded document
await new Promise((r) => setTimeout(r, 2000));

// ------------------------------------------------------------ (b) evidence
console.log('\n=== (b) IN-PAGE EVIDENCE: CONTROL + CACHE CONTENTS ===');
const mainJs = await page.evaluate(() =>
  [...document.querySelectorAll('script[src]')]
    .map((s) => s.src)
    .find((u) => /\/assets\/index-.*\.js$/.test(u)) || null);
out('main bundle URL', mainJs);

const evidence = await page.evaluate(async (jsUrl) => {
  const keys = await caches.keys();
  const hit = await caches.match(jsUrl);
  const entries = [];
  for (const k of keys) {
    const c = await caches.open(k);
    for (const req of await c.keys()) {
      const r = await c.match(req);
      entries.push({ cache: k, url: req.url, status: r.status, bytes: (await r.clone().arrayBuffer()).byteLength });
    }
  }
  return {
    swControlled: !!navigator.serviceWorker.controller,
    controllerScript: navigator.serviceWorker.controller?.scriptURL ?? null,
    cacheKeys: keys,
    mainJsInCache: !!hit,
    mainJsCacheBytes: hit ? (await hit.clone().arrayBuffer()).byteLength : null,
    entries,
  };
}, mainJs);
out('evidence', evidence);

verdict.swControlled = evidence.swControlled;
verdict.bundlePrecached = evidence.mainJsInCache;

// ------------------------------------------------- (c) offline navigation
console.log('\n=== (c) FULL NAVIGATION WITH THE NETWORK DISCONNECTED ===');
await page.setOfflineMode(true);

const controlFetch = () => page.evaluate(async () => {
  const r = {};
  try {
    const x = await fetch('/definitely-not-precached-' + Date.now(), { cache: 'no-store' });
    r.sameOrigin = `RESOLVED status=${x.status} — NETWORK REACHABLE`;
  } catch (e) { r.sameOrigin = 'REJECTED: ' + e.message; }
  try {
    await fetch('http://localhost:8000/api/v1/health', { cache: 'no-store', mode: 'no-cors' });
    r.backendApi = 'RESOLVED — NETWORK REACHABLE';
  } catch (e) { r.backendApi = 'REJECTED: ' + e.message; }
  return r;
});

const controlBefore = await controlFetch();
out('CONTROL before navigation', controlBefore);

consoleMsgs.length = 0; pageErrors.length = 0; failedReqs.length = 0;

let navOk = false, navStatus = null, navFromSW = null, navErr = null;
try {
  const resp2 = await page.goto(URL_, { waitUntil: 'load', timeout: 45000 });
  navStatus = resp2?.status() ?? null;
  navFromSW = resp2?.fromServiceWorker() ?? null;
  navOk = true;
} catch (e) { navErr = e.message; }
out('navigation', navOk ? `SUCCESS status=${navStatus} fromServiceWorker=${navFromSW}` : `FAILED: ${navErr}`);

// Snapshot NOW, before the post-navigation control fetch — otherwise the
// control's deliberate failure pollutes the navigation's failure list.
const navFailures = [...failedReqs];
const navPageErrors = [...pageErrors];

const render = await page.evaluate(() => {
  const root = document.getElementById('root');
  return {
    title: document.title,
    rootChildCount: root ? root.children.length : -1,
    renderedText: root ? (root.innerText || '').trim().slice(0, 200) : null,
    // reported only to be explicitly disregarded — see header note (1)
    navigatorOnLine_IGNORE: navigator.onLine,
    stillControlled: !!navigator.serviceWorker.controller,
  };
}).catch((e) => ({ evaluateFailed: String(e.message) }));
out('render', render);

const controlAfter = await controlFetch();
out('CONTROL after navigation', controlAfter);
out('requests that failed during the offline navigation', navFailures);
out('uncaught JS errors during the offline navigation', navPageErrors);

// Requests known to fail offline because they are genuinely not precached.
// Documented as a real gap in README.md — tolerated here so it does not mask a
// regression, but reported rather than hidden.
const KNOWN_GAPS = [/\/pwa-192x192\.png$/];
const unexpected = navFailures.filter((r) => !KNOWN_GAPS.some((re) => re.test(r.url)));
out('known offline gaps hit', navFailures.filter((r) => KNOWN_GAPS.some((re) => re.test(r.url))).map((r) => r.url));
out('UNEXPECTED failures', unexpected);

// ------------------------------------------------------------- verdict
verdict.networkTrulyDown =
  controlBefore.sameOrigin.startsWith('REJECTED') && controlAfter.sameOrigin.startsWith('REJECTED');
verdict.offlineNavServedBySW = navOk && navStatus === 200 && navFromSW === true;
verdict.shellRendered = (render.rootChildCount ?? 0) > 0 && (render.renderedText ?? '').length > 0;
// Deliberately NOT a raw console-error count: the control fetches are designed
// to fail and log errors, so counting those would always fail the run.
verdict.noUncaughtJsErrors = navPageErrors.length === 0;
verdict.noUnexpectedRequestFailures = unexpected.length === 0;

console.log('\n=== VERDICT ===');
out('checks', verdict);
const pass = Object.values(verdict).every(Boolean);
console.log(pass
  ? 'PASS — the shell is provably service-worker-served, not HTTP-disk-cache-served.'
  : 'FAIL — at least one criterion did not hold; do not claim SW attribution.');

await browser.close();
process.exit(pass ? 0 : 1);
