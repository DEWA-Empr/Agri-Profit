# Frontend performance measurements — raw Lighthouse artifacts

This folder holds the **raw, unedited** Lighthouse output behind the frontend
performance figures reported in the dissertation (LIMITATIONS §7). It is
committed so that every number in the write-up can be traced back to the report
that produced it, and so the measurement can be repeated.

> **These figures supersede the 15 August 2026 set.** The application was
> rebuilt on 17 August after the dashboard mock-data removal, the reversal UI,
> the Bioprocess dropdown guard and the yield-unit changes (commit `c16924e`),
> which changed the bundle. **The superseded artifacts are kept, not deleted** —
> they are in [`2026-08-15/`](./2026-08-15/), unmodified, under their original
> filenames. Any figure quoted in the write-up should come from the top-level
> files described below; the archive exists only so the earlier claims remain
> auditable.

## Provenance

| | |
|---|---|
| **Tool** | Lighthouse **13.4.1** (npm global), driven by headless Chrome |
| **Date of runs** | **2026-08-17**, 17:41–17:47 UTC (all artifacts, per each report's `fetchTime`) |
| **Target** | `http://localhost:4173/` — the `frontend-prod` compose service (`vite preview` on the production build, so the PWA service worker is active) |
| **Backend** | `agrip-backend-1` + `agrip-db-1` from `docker-compose.yml`, running locally |
| **Form factor** | Mobile emulation — 412 × 823 @ DPR 1.75, Moto G Power UA |
| **Host benchmark index** | 425–1654 across runs — **see the warning below** |
| **Bundle under test** | single JS chunk `assets/index-AjooZYSG.js`, **243,724 bytes** transferred; 7 requests total on a cold load |
| **Commit** | `c16924e` |

All runs are from a **single developer machine against localhost**. They
characterise the client-side cost of the bundle under emulated network and CPU
constraint; they are not a claim about production or real-network behaviour.

> **Host-speed warning — read before comparing against the August set.**
> `benchmarkIndex` is Lighthouse's CPU-speed proxy for the machine at the moment
> of the run. On 15 August the CLI runs sat at **609.5–935**. On 17 August the
> same machine measured **425–1561.5** on the CLI runs and **1497–1654.5** on the
> flow's cold navigations — i.e. it was generally running about **1.5–2× faster**,
> with one cold-start outlier at the bottom (`lh-slow3g-run1`, 425).
> Network-bound metrics under `simulate` (FCP, LCP, SI) are modelled by Lantern
> and are largely insulated from this. **CPU-bound metrics are not**: TBT and the
> composite performance score move with host speed. Any improvement in TBT or
> score between the two sets must therefore **not** be attributed to the code
> changes. Within a single set the comparison is sound; across the two sets, only
> the network-bound metrics and the byte counts are.

## Throttling parameters

Both keeper sets use Lighthouse's **`simulate`** throttling method (Lantern),
not applied packet-level throttling:

| Set | RTT | Throughput | CPU slowdown |
|---|---|---|---|
| **Cold slow-3G** (`lh-slow3g-run*`) | 400 ms | 400 Kbps | 4× |
| **Cold default mobile / slow-4G** (`lh-4g-run*`) | 150 ms | 1638.4 Kbps | 4× |
| **Cache flow** (`flow-iter*`) | 400 ms | 400 Kbps | 4× |

The `lh-4g-run*` settings are Lighthouse's **default mobile preset**, passed
explicitly so the invocation is self-documenting and byte-comparable with the
August set.

> Note when reading the JSON: under `simulate`, only `rttMs`,
> `throughputKbps` and `cpuSlowdownMultiplier` are honoured. The
> `requestLatencyMs` / `downloadThroughputKbps` fields also present in
> `configSettings.throttling` are the DevTools-throttling equivalents and are
> **not** applied in this mode — in the flow artifacts they still carry
> Lighthouse's stock values (562.5 ms / 1474.56 Kbps) and should be ignored.

## What is here

**Current set (2026-08-17, 13 runs, all committed):**

- `lh-slow3g-run1..5.report.{json,html}` — 5 cold slow-3G CLI runs
- `lh-4g-run1..5.report.{json,html}` — 5 cold default-mobile-preset CLI runs
- `flow-iter1..3.json` — 3 Lighthouse user-flow results, each containing **both**
  a cold and a warm navigation
- `flow.mjs` — the user-flow script that produced them
- `offline-probe.mjs` — the driven-browser probe that settles service-worker
  attribution; exits 0 on PASS

**Superseded set (2026-08-15):** kept in `2026-08-15/`, same filenames, not
modified. Nothing from the August measurement has been deleted.

**Discarded as invalid at the original August measurement, and never
committed:** the `lh-slow3g-warm-*` CLI runs (3) and the 1600 Kbps runs labelled
"3G" (`lh-3g-run*`, 3) — the former because a fresh CLI invocation gets a fresh
Chrome profile, so no service worker survived from a previous run and the "warm"
runs in fact measured a cold load; the latter because 150 ms / 1600 Kbps is
Lighthouse's *slow-4G* profile, so those runs were throttled at 4G while being
named 3G, duplicating the `lh-4g-run*` set.

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
| 1 | 7668.8 | 7668.8 | 7668.8 | 121.0 | 7868.5 | 0 | 57 |
| 2 | 7692.2 | 7692.2 | 7692.2 | 120.5 | 7891.5 | 0 | 57 |
| 3 | 7683.0 | 7683.0 | 7683.0 | 165.5 | 7927.2 | 0 | 56 |
| 4 | 7661.5 | 7661.5 | 7661.5 | 113.0 | 7853.2 | 0 | 57 |
| 5 | 7674.4 | 7674.4 | 7674.4 | 152.0 | 7926.4 | 0 | 56 |
| **median** | **7674.4** | **7674.4** | **7674.4** | **121.0** | **7891.5** | **0** | **57** |

### Cold load, default mobile preset (slow-4G) — `lh-4g-run*` (n = 5, CLI)

| Run | FCP | LCP | SI | TBT | TTI | CLS | perf |
|---|---|---|---|---|---|---|---|
| 1 | 2324.9 | 2324.9 | 2324.9 | 161.5 | 2565.3 | 0 | 93 |
| 2 | 2311.7 | 2311.7 | 2311.7 | 100.5 | 2491.1 | 0 | 95 |
| 3 | 2311.5 | 2311.5 | 2311.5 | 101.0 | 2491.2 | 0 | 95 |
| 4 | 2317.7 | 2317.7 | 2317.7 | 107.0 | 2524.7 | 0 | 95 |
| 5 | 2345.4 | 2345.4 | 2345.4 | 125.5 | 2549.6 | 0 | 94 |
| **median** | **2317.7** | **2317.7** | **2317.7** | **107.0** | **2524.7** | **0** | **95** |

### Cache flow, slow-3G — `flow-iter*` (n = 3, user flow)

Cold navigation (step 1 of each flow):

| Iter | FCP | LCP | SI | TBT | TTI | CLS | perf |
|---|---|---|---|---|---|---|---|
| 1 | 7682.2 | 7682.2 | 7682.2 | 174.0 | 7956.2 | 0 | 56 |
| 2 | 7679.9 | 7679.9 | 7679.9 | 39.5 | 8070.1 | 0 | 58 |
| 3 | 7676.9 | 7676.9 | 7676.9 | 32.0 | 8040.5 | 0 | 58 |
| **median** | **7679.9** | **7679.9** | **7679.9** | **39.5** | **8040.5** | **0** | **58** |

Warm navigation (step 2 of each flow) — **the row this folder exists to record**:

| Iter | FCP | LCP | SI | TBT | TTI | CLS | perf |
|---|---|---|---|---|---|---|---|
| 1 | 105.4 | 1612.1 | 105.4 | 266.6 | 1612.1 | 0 | 94 |
| 2 | 122.4 | 1613.8 | 122.4 | 265.6 | 1613.8 | 0 | 94 |
| 3 | 116.4 | 1614.8 | 116.4 | 285.0 | 1614.8 | 0 | 94 |
| **median** | **116.4** | **1613.8** | **116.4** | **266.6** | **1613.8** | **0** | **94** |

The flow's cold median (7679.9 ms FCP) agrees with the independent CLI cold set
(7674.4 ms), which is the cross-check that the two harnesses measured the same
thing under the same throttling.

**Warm vs cold on identical slow-3G throttling:** FCP falls from 7679.9 ms to
116.4 ms (**≈ 66×**) and the performance score rises from 58 to 94, because on
the second navigation the main bundle is served from cache — `transferSize` 0,
against 243,724 bytes on the cold load — and the request count drops from 7
to 6.

### Change against the superseded 15 August set

Only the network-bound metrics and byte counts are comparable across sets (see
the host-speed warning above). TBT and the performance score are **not** listed
here for that reason.

| Metric | 2026-08-15 | 2026-08-17 | Δ |
|---|---|---|---|
| Cold slow-3G FCP (median) | 7732.4 | 7674.4 | −58.0 ms (−0.8%) |
| Cold slow-4G FCP (median) | 2418.5 | 2317.7 | −100.8 ms (−4.2%) |
| Warm FCP (median) | 105.4 | 116.4 | +11.0 ms (+10.4%) |
| Bundle transferred (gzip) | 243,534 B | 243,724 B | +190 B |
| Bundle in cache (uncompressed) | 807,372 B | 808,386 B | +1,014 B |
| Cold requests | 7 | 7 | — |
| Warm requests | 6 | 6 | — |

All of these differences are small enough to be run-to-run noise rather than
demonstrated effects; the honest reading is that the 17 August changes left
load performance **unchanged**. The bundle grew by 190 transferred bytes — the
reversal dialog and the unit-grouping display code, less the deleted mock
components — which is not a meaningful change at this size.

## Service-worker attribution

Cache attribution IS established, and was **re-confirmed against this build** on
2026-08-17: `offline-probe.mjs` exits PASS. The probe confirmed the page is
controlled by `/sw.js`, that the sole cache is `workbox-precache-v2` containing
five entries including the application bundle, and that a full navigation
performed with the network disconnected returned HTTP 200 with
`response.fromServiceWorker() === true` and rendered the login screen. Control
requests to non-precached URLs were rejected with `ERR_INTERNET_DISCONNECTED`
both before and after that navigation, confirming the network was genuinely
unreachable. No uncaught JS errors and no unexpected request failures occurred
during the offline navigation.

Note: `navigator.onLine` reports `true` after an emulated-offline navigation and
must be disregarded; the control fetches are the evidence.

Known gap, unchanged: `pwa-192x192.png` is not precached and is unavailable
offline.

The five precached entries:

| Entry | Bytes (uncompressed) |
|---|---|
| `index.html` | 581 |
| `assets/index-AjooZYSG.js` | 808,386 |
| `assets/index-CMvIr7Qx.css` | 1,669 |
| `manifest.webmanifest` | 380 |
| `registerSW.js` | 134 |

Neither `pwa-192x192.png` nor `favicon.svg` appears in that list — the icon gap
is a deterministic fact about the precache manifest.

The bundle is 808,386 bytes in cache against 243,724 bytes transferred on the
cold load — the former is uncompressed, the latter gzip over the wire. Both
figures describe the same asset. The CSS chunk `index-CMvIr7Qx.css` is
byte-identical to the August build.

## Reading caveats

- **SI equals FCP in every run of this set.** The app shell has no images above
  the fold and renders in a single paint, so Speed Index collapses onto FCP. Not
  a transcription error. (In the August set `lh-4g-run4` was the one run where
  they differed; in this set they never do.)
- **TTI is reported here but is no longer a scored metric.** In Lighthouse
  13.4.1 `interactive` carries weight 0 and sits in the `hidden` group; the
  score is composed of FCP (10), SI (10), LCP (25), TBT (30) and CLS (25). TTI
  is included in the tables for completeness because it was asked for, and
  because it is still the clearest single number for "when did the main thread
  settle" — but it should not be presented as a Lighthouse-scored metric.
- **Cache attribution is established** — but not by these Lighthouse artifacts
  alone, which never mark the warm requests `fromServiceWorker` (the field is
  absent in 13.4.1). It is settled by `offline-probe.mjs`; see above.
- **CLS is 0.000 everywhere**, which is expected for a fixed-layout shell but is
  also a weak signal at this page count — it is not evidence of layout stability
  across the whole application.
- **`simulate` is a model, not a measurement of a real network.** Lantern
  estimates metrics from an unthrottled trace plus a network model. These
  figures are comparable to each other and to other Lighthouse results at the
  same settings; they are not field data.
- **The host was not quiesced.** `benchmarkIndex` varied by more than 3× across
  the CLI runs (425 to 1561.5), with the lowest value on the very first run of
  the session. A stricter protocol would discard a warm-up run and pin the
  machine to a fixed power profile; neither was done, and the raw runs are
  reported as they came out.

## Reproducing

Start the production frontend (the dev server runs no service worker, so it
cannot show the warm case):

```bash
docker compose --profile prod up -d --build frontend-prod
```

Cold CLI runs:

```bash
# slow-3G
lighthouse http://localhost:4173 --form-factor=mobile --screenEmulation.mobile \
  --throttling-method=simulate --throttling.rttMs=400 \
  --throttling.throughputKbps=400 --throttling.cpuSlowdownMultiplier=4 \
  --output=json --output=html --output-path=./lh-slow3g-run1 \
  --chrome-flags="--headless --no-sandbox --disable-gpu"

# default mobile preset (slow-4G):
#   --throttling.rttMs=150 --throttling.throughputKbps=1638.4
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
adjust those constants before re-running on another machine. `flow.mjs` does not
create its output directory — create it first, or the run fails at the write.

On Windows, the Lighthouse CLI may exit with
`EPERM, Permission denied: ...\Temp\lighthouse.NNNNNNNN` **after** the audit
completes. That is the Chrome launcher failing to delete its own temporary
profile directory; the report files are written correctly and the measurement is
unaffected. Check that the `.report.json` exists rather than trusting the exit
code.
