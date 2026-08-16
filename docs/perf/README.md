# Frontend performance measurements — raw Lighthouse artifacts

This folder holds the **raw, unedited** Lighthouse output behind the frontend
performance figures reported in the dissertation (LIMITATIONS §7). It is
committed so that every number in the write-up can be traced back to the report
that produced it, and so the measurement can be repeated.

## Provenance

| | |
|---|---|
| **Tool** | Lighthouse **13.4.1** (npm global), driven by headless Chrome **151.0.0.0** |
| **Date of runs** | **2026-08-15**, 16:38–17:28 UTC (all artifacts, per each report's `fetchTime`) |
| **Target** | `http://localhost:4173/` — the `frontend-prod` compose service (`vite preview` on the production build, so the PWA service worker is active) |
| **Backend** | `agrip-backend-1` + `agrip-db-1` from `docker-compose.yml`, running locally |
| **Form factor** | Mobile emulation — 412 × 823 @ DPR 1.75, Moto G Power UA |
| **Host benchmark index** | 744–812 across runs (Lighthouse's CPU-speed proxy for this machine) |
| **Bundle under test** | single JS chunk `assets/index-C1SNwsT_.js`, **243,534 bytes** transferred; 7 requests total on a cold load |

All runs are from a **single developer machine against localhost**. They
characterise the client-side cost of the bundle under emulated network and CPU
constraint; they are not a claim about production or real-network behaviour.

## Throttling parameters

Both keeper sets use Lighthouse's **`simulate`** throttling method (Lantern),
not applied packet-level throttling:

| Set | RTT | Throughput | CPU slowdown |
|---|---|---|---|
| **Cold slow-3G** (`lh-slow3g-run*`) | 400 ms | 400 Kbps | 4× |
| **Slow-4G** (`lh-4g-run*`) | 150 ms | 1638.4 Kbps | 4× |
| **Cache flow** (`flow-iter*`) | 400 ms | 400 Kbps | 4× |

> Note when reading the JSON: under `simulate`, only `rttMs`,
> `throughputKbps` and `cpuSlowdownMultiplier` are honoured. The
> `requestLatencyMs` / `downloadThroughputKbps` fields also present in
> `configSettings.throttling` are the DevTools-throttling equivalents and are
> **not** applied in this mode — in the flow artifacts they still carry
> Lighthouse's stock values (562.5 ms / 1474.56 Kbps) and should be ignored.

## What is here, and what was discarded

**Kept (13 runs, all committed):**

- `lh-slow3g-run1..5.report.{json,html}` — 5 cold slow-3G CLI runs
- `lh-4g-run1..5.report.{json,html}` — 5 slow-4G CLI runs
- `flow-iter1..3.json` — 3 Lighthouse user-flow results, each containing **both**
  a cold and a warm navigation
- `flow.mjs` — the user-flow script that produced them
- `offline-probe.mjs` — the driven-browser probe that settled service-worker
  attribution (see below); exits 0 on PASS

**Discarded as invalid, and deliberately not committed:** the
`lh-slow3g-warm-*` CLI runs (3) and the 1600 Kbps runs labelled "3G"
(`lh-3g-run*`, 3) — the former because a fresh CLI invocation gets a fresh
Chrome profile, so no service worker survived from a previous run and the
"warm" runs in fact measured a cold load (median FCP 7714 ms, statistically
identical to the 7732 ms cold set, with zero bytes served from cache); the
latter because 150 ms / 1600 Kbps is Lighthouse's *slow-4G* profile, so those
runs were throttled at 4G while being named 3G, duplicating the `lh-4g-run*`
set (median FCP 2372 ms vs 2419 ms).

The failure of the CLI to produce a genuine warm measurement is precisely why
`flow.mjs` exists: a Lighthouse **user flow** keeps one browser session across
two navigations (`disableStorageReset: true` on the second), so the service
worker installed during the cold navigation is still active for the warm one.

## Results

Medians across runs. Times in milliseconds; `perf` is the Lighthouse
performance score (0–100).

### Cold load, slow-3G — `lh-slow3g-run*` (n = 5, CLI)

| Run | FCP | LCP | SI | TBT | TTI | CLS | perf |
|---|---|---|---|---|---|---|---|
| 1 | 7823.4 | 8223.4 | 7823.4 | 48.0 | 8267.4 | 0 | 58 |
| 2 | 7711.3 | 7711.3 | 7711.3 | 140.0 | 7951.3 | 0 | 57 |
| 3 | 7734.1 | 7734.1 | 7734.1 | 334.0 | 8168.1 | 0 | 51 |
| 4 | 7732.4 | 7732.4 | 7732.4 | 215.0 | 8047.4 | 0 | 55 |
| 5 | 7697.5 | 7697.5 | 7697.5 | 202.0 | 7999.5 | 0 | 55 |
| **median** | **7732.4** | **7732.4** | **7732.4** | **202.0** | **8047.4** | **0** | **55** |

### Cold load, slow-4G — `lh-4g-run*` (n = 5, CLI)

| Run | FCP | LCP | SI | TBT | TTI | CLS | perf |
|---|---|---|---|---|---|---|---|
| 1 | 2421.2 | 2421.2 | 2421.2 | 136.0 | 2657.2 | 0 | 93 |
| 2 | 2346.1 | 2346.1 | 2346.1 | 165.0 | 2611.1 | 0 | 93 |
| 3 | 2353.9 | 2353.9 | 2353.9 | 368.0 | 2821.9 | 0 | 86 |
| 4 | 2537.9 | 2537.9 | 2943.5 | 14.5 | 2581.3 | 0 | 93 |
| 5 | 2418.5 | 2418.5 | 2418.5 | 256.0 | 2774.5 | 0 | 89 |
| **median** | **2418.5** | **2418.5** | **2418.5** | **165.0** | **2657.2** | **0** | **93** |

### Cache flow, slow-3G — `flow-iter*` (n = 3, user flow)

Cold navigation (step 1 of each flow):

| Iter | FCP | LCP | SI | TBT | TTI | CLS | perf |
|---|---|---|---|---|---|---|---|
| 1 | 7703.7 | 7703.7 | 7703.7 | 185.0 | 8265.9 | 0 | 55 |
| 2 | 7701.8 | 7701.8 | 7701.8 | 208.0 | 8009.8 | 0 | 55 |
| 3 | 7714.9 | 7714.9 | 7714.9 | 92.5 | 8032.5 | 0 | 58 |
| **median** | **7703.7** | **7703.7** | **7703.7** | **185.0** | **8032.5** | **0** | **55** |

Warm navigation (step 2 of each flow) — **the row this folder exists to record**:

| Iter | FCP | LCP | SI | TBT | TTI | CLS | perf |
|---|---|---|---|---|---|---|---|
| 1 | 120.4 | 1610.2 | 120.4 | 216.0 | 1610.2 | 0 | 96 |
| 2 | 99.4 | 1612.0 | 99.4 | 307.6 | 1612.0 | 0 | 93 |
| 3 | 105.4 | 1613.5 | 105.4 | 256.0 | 1613.5 | 0 | 95 |
| **median** | **105.4** | **1612.0** | **105.4** | **256.0** | **1612.0** | **0** | **95** |

The flow's cold median (7703.7 ms FCP) agrees with the independent CLI cold set
(7732.4 ms), which is the cross-check that the two harnesses measured the same
thing under the same throttling.

**Warm vs cold on identical slow-3G throttling:** FCP falls from 7703.7 ms to
105.4 ms (**≈ 73×**) and the performance score rises from 55 to 95, because on
the second navigation the main bundle is served from cache — `transferSize` 0,
against 243,534 bytes on the cold load — and the request count drops from 7
to 6.

## Service-worker attribution

Cache attribution IS established. A driven-browser probe (see
`offline-probe.mjs`) confirmed the page is controlled by `/sw.js`, that the sole
cache is `workbox-precache-v2` containing five entries including the application
bundle, and that a full navigation performed with the network disconnected
returned HTTP 200 with `response.fromServiceWorker() === true` and rendered the
login screen. Control requests to non-precached URLs were rejected with
`ERR_INTERNET_DISCONNECTED` both before and after that navigation, confirming
the network was genuinely unreachable.

Note: `navigator.onLine` reports `true` after an emulated-offline navigation and
must be disregarded; the control fetches are the evidence.

Known gap: `pwa-192x192.png` is not precached and is unavailable offline.

The five precached entries:

| Entry | Bytes (uncompressed) |
|---|---|
| `index.html` | 581 |
| `assets/index-C1SNwsT_.js` | 807,372 |
| `assets/index-CMvIr7Qx.css` | 1,669 |
| `manifest.webmanifest` | 380 |
| `registerSW.js` | 134 |

Neither `pwa-192x192.png` nor `favicon.svg` appears in that list — the icon gap
is a deterministic fact about the precache manifest, corroborated by an observed
`ERR_INTERNET_DISCONNECTED` when Chrome fetched the manifest icon offline.
(Whether that fetch is attempted at all varies between runs, so the precache
listing, not the failed request, is the evidence of record.)

The bundle is 807,372 bytes in cache against 243,534 bytes transferred on the
cold load — the former is uncompressed, the latter gzip over the wire. Both
figures describe the same asset.

## Reading caveats

- **SI equals FCP in most runs.** The app shell has no images above the fold and
  renders in a single paint, so Speed Index collapses onto FCP. Not a
  transcription error. `lh-4g-run4` is the one run where they differ.
- **TTI is reported here but is no longer a scored metric.** In Lighthouse
  13.4.1 `interactive` carries weight 0 and sits in the `hidden` group; the
  score is composed of FCP (10), SI (10), LCP (25), TBT (30) and CLS (25). TTI
  is included in the tables for completeness because it was asked for, and
  because it is still the clearest single number for "when did the main thread
  settle" — but it should not be presented as a Lighthouse-scored metric.
- **Cache attribution is established** — but not by these Lighthouse artifacts
  alone, which never mark the warm requests `fromServiceWorker`. It is settled
  by `offline-probe.mjs`; see "Service-worker attribution" below.
- **CLS is 0.000 everywhere**, which is expected for a fixed-layout shell but is
  also a weak signal at this page count — it is not evidence of layout stability
  across the whole application.
- **`simulate` is a model, not a measurement of a real network.** Lantern
  estimates metrics from an unthrottled trace plus a network model. These
  figures are comparable to each other and to other Lighthouse results at the
  same settings; they are not field data.

## Reproducing

Start the production frontend (the dev server runs no service worker, so it
cannot show the warm case):

```bash
docker compose --profile prod up -d --build frontend-prod
```

Cold CLI runs:

```bash
# slow-3G
lighthouse http://localhost:4173 --preset=desktop=false --form-factor=mobile \
  --throttling-method=simulate --throttling.rttMs=400 \
  --throttling.throughputKbps=400 --throttling.cpuSlowdownMultiplier=4 \
  --output=json --output=html --output-path=./lh-slow3g-run1

# slow-4G: --throttling.rttMs=150 --throttling.throughputKbps=1638.4
```

Warm (cache) measurement — the CLI cannot do this; use the flow script:

```bash
node docs/perf/flow.mjs
```

Service-worker attribution:

```bash
node docs/perf/offline-probe.mjs   # exits 0 on PASS, 1 on FAIL
```

`flow.mjs` and `offline-probe.mjs` hard-code absolute paths to the globally
installed Lighthouse, to Chrome, and (for `flow.mjs`) to an output directory;
adjust those constants before re-running on another machine.
