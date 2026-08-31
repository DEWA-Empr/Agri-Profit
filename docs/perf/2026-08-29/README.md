# Frontend performance — baseline set, 29 August 2026

**This is the current set. It supersedes the 17 August 2026 set in the parent
directory for every reported figure.** The parent set is kept, unmodified, as the
dated record of the pre-code-splitting build; nothing there has been deleted or
edited.

## Provenance

| | |
|---|---|
| **Tool** | Lighthouse **13.4.1** (npm global), driven by headless Chrome |
| **Date of runs** | **2026-08-29**, 04:59–05:02 UTC (per each report's `fetchTime`) |
| **Commit** | **`78a68c292205acdcac1a52f977fbea31b6e8495e`** — the thesis baseline |
| **Target** | `http://localhost:4173/` — the `frontend-prod` compose service (`vite preview` on the production build, so the PWA service worker is active) |
| **Backend** | `agrip-backend-1` + `agrip-db-1` from `docker-compose.yml`, running locally |
| **Form factor** | Mobile emulation — 412 × 823 @ DPR 1.75 |
| **Host benchmark index** | **1406–1996** across runs (17 Aug set: 425–1654) |
| **Bundle under test** | code-split: `assets/index-K2tsIDPN.js` 129,054 B + `assets/jsx-runtime-CDoWQAPm.js` 4,205 B transferred; **139,245 B over 8 requests** on a cold load |

Same method and same machine as the 17 August set. All runs are from a **single
developer machine against localhost** under simulated (Lantern) throttling. They
characterise the client-side cost of the bundle under emulated network and CPU
constraint; they are **not** a claim about production or real-network behaviour.

> **Host-speed warning.** `benchmarkIndex` is Lighthouse's CPU-speed proxy. The
> machine ran faster and more consistently on 29 August (1406–1996) than on
> 17 August (425–1654). FCP, LCP and Speed Index are modelled by Lantern under
> `simulate` and are largely insulated from this. **TBT and the composite
> performance score are not.** No score or blocking-time difference between the
> two dates may be attributed to code — which specifically rules out reading the
> cold slow-3G TBT movement (121.0 → 10.5 ms) as a code effect. Across dates,
> only the network-bound metrics and the byte counts compare.

## Throttling parameters

| Set | RTT | Throughput | CPU slowdown |
|---|---|---|---|
| **Cold slow-3G** (`lh-slow3g-run*`) | 400 ms | 400 Kbps | 4× |
| **Cold default mobile / slow-4G** (`lh-4g-run*`) | 150 ms | 1638.4 Kbps | 4× |
| **Cache flow** (`flow-iter*`) | 400 ms | 400 Kbps | 4× |

## What is here

- `lh-slow3g-run1..5.report.{json,html}` — 5 cold slow-3G CLI runs
- `lh-4g-run1..5.report.{json,html}` — 5 cold default-mobile-preset CLI runs
- `flow-iter1..3.json` — 3 user-flow results, each containing **both** a cold and
  a warm navigation, produced by the unmodified `../flow.mjs`

## Results

Medians. Times in milliseconds; `perf` is the performance score (0–100).

### Cold load, slow-3G (n = 5, CLI)

| Run | FCP | LCP | SI | TBT | TTI | CLS | perf | BI |
|---|---|---|---|---|---|---|---|---|
| 1 | 6095.6 | 6095.6 | 6095.6 | 18.0 | 6170.4 | 0 | 63 | 1406 |
| 2 | 5661.5 | 5661.5 | 5661.5 | 2.0 | 5718.7 | 0 | 65 | 1863 |
| 3 | 5661.2 | 5661.2 | 5661.2 | 4.0 | 5720.6 | 0 | 65 | 1762 |
| 4 | 5619.7 | 5619.7 | 5619.7 | 24.0 | 5921.1 | 0 | 65 | 1797 |
| 5 | 5661.0 | 5661.0 | 5661.0 | 10.5 | 5727.6 | 0 | 65 | 1566 |
| **median** | **5661.2** | **5661.2** | **5661.2** | **10.5** | **5727.6** | **0** | **65** | 1761.5 |

Transfer: 139,245 B over 8 requests, every run.

### Cold load, default mobile preset / slow-4G (n = 5, CLI)

| Run | FCP | LCP | SI | TBT | TTI | CLS | perf | BI |
|---|---|---|---|---|---|---|---|---|
| 1 | 1673.7 | 1823.7 | 1673.7 | 7.5 | 1969.4 | 0 | 99 | 1668 |
| 2 | 1709.9 | 1859.9 | 1709.9 | 9.0 | 1924.8 | 0 | 99 | 1800 |
| 3 | 1682.2 | 1832.2 | 1682.2 | 5.0 | 1947.7 | 0 | 99 | 1923 |
| 4 | 1717.3 | 1867.3 | 1717.3 | 19.5 | 1943.8 | 0 | 99 | 1637 |
| 5 | 1716.2 | 1866.2 | 1716.2 | 9.0 | 1903.6 | 0 | 99 | 1493 |
| **median** | **1709.9** | **1859.9** | **1709.9** | **9.0** | **1943.8** | **0** | **99** | 1668.5 |

Transfer: 139,245 B over 8 requests, every run.

### Cache flow, slow-3G (n = 3, one browser session per iteration)

| Iteration | cold FCP | warm FCP | warm LCP | warm TBT | warm perf | cold transfer | warm transfer |
|---|---|---|---|---|---|---|---|
| 1 | 5663.3 | 66.6 | 1612.7 | 0 | 100 | 139,245 B / 8 req | 127 B / 7 req |
| 2 | 5668.6 | 70.6 | 1612.0 | 0 | 100 | 139,245 B / 8 req | 127 B / 7 req |
| 3 | 5664.4 | 78.6 | 1611.3 | 0 | 100 | 139,245 B / 8 req | 127 B / 7 req |
| **median** | **5664.4** | **70.6** | **1612.0** | **0** | **100** | | |

The flow's cold navigation reproduces the CLI cold median to within ~3 ms, which
is the internal control that makes the warm-against-cold comparison legitimate.

### The 127 warm bytes

On the warm navigation the document, both JavaScript chunks, the stylesheet,
`registerSW.js` and `manifest.webmanifest` each transfer **0 bytes**. The only
request that transfers anything is `pwa-192x192.png` at 127 B — the manifest
icon, which is absent from the Workbox precache. That is the defect reported in
Chapter Four §4.10.4, and this run confirms it by measurement rather than by
reading the precache listing.

## Movement against the 17 August set — comparable metrics only

| Metric | 17 Aug, `c16924e` | 29 Aug, `78a68c2` |
|---|---|---|
| Cold transfer | 243,724 B / 7 req | **139,245 B / 8 req** (−43%) |
| Cold FCP, slow 3G | 7674.4 ms | **5661.2 ms** (−26%) |
| Cold FCP, slow 4G | 2317.7 ms | **1709.9 ms** (−26%) |
| Warm FCP | 116.4 ms | **70.6 ms** |
| Warm LCP | 1613.8 ms | **1612.0 ms** (unchanged) |
| Score, TBT | — | **not comparable** (host speed) |

Route-level code-splitting removed 104,479 bytes from the first load. The warm
largest-contentful-paint is unchanged because it was never network-bound.

## Reproduce

```
docker compose --profile prod up -d --build db backend frontend-prod
lighthouse http://localhost:4173/ --only-categories=performance --form-factor=mobile \
  --screenEmulation.mobile --screenEmulation.width=412 --screenEmulation.height=823 \
  --screenEmulation.deviceScaleFactor=1.75 --throttling-method=simulate \
  --throttling.rttMs=400 --throttling.throughputKbps=400 --throttling.cpuSlowdownMultiplier=4 \
  --output=json --output=html --output-path=lh-slow3g-run1.report \
  --chrome-flags="--headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage"
node docs/perf/flow.mjs
```
