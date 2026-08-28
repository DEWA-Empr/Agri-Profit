# Chapter Four — screenshot run-sheet

Prepared state and capture order for the Chapter Four figures. Everything below
was verified against the running stack (`agrip-db-1`, `agrip-backend-1`,
`agrip-frontend-1`, `agrip-frontend-prod-1` all up) and the live API on
2026-08-19, not from the documentation.

## Prepared state

The seed was re-run: all 13 POSTs returned **200 (already seeded)**,
`13 operational logs, 13 financial transactions`. Live
`GET /dss/decision-support` matches `dss_per_crop.json` exactly (cassava
84200.0, maize 41500.0 / 35.0 / 41.666…, tomato −112900.0, overall 12800.0).
Nothing needs re-seeding.

If the ledger has been reset since, restore it with:

```
python backend/scripts/seed_bioprocess_demo.py
```

**Origin: `http://localhost:5173`** (dev) for the whole pass — it runs no
service worker, so a stale cached response cannot be photographed by mistake.
`http://localhost:4173` is the production PWA build, needed only for the
offline-with-cached-reads variant in 4.10.

**Before shot 1.** If the browser holds a token for another farm, sign out
(header, top right) and log in as `demo-bioprocess-v2@test.example` /
`demo-bioprocess-pw`. Window at 1440×900 for shots 1–10; 360 px only at step 11.

---

## Capture order — one pass

### 1 · 4.1 Dashboard, post-cleanup

**URL** `http://localhost:5173/` · no command.

Expect Net Profit **₦12.8K**, Gross Revenue **₦223.6K**, Operating Cost
**₦210.8K**, Profit Margin **5.7%** (from `GET /ledger/summary`). The
post-cleanup evidence in frame: six nav items only (no USSD/WhatsApp section),
no field-performance table, no YoY deltas or sparklines on the KPI tiles.

### 2 · 4.3 Per-crop gross margin and ranking

Same page, scroll to the **Decision support** card. Three rows in rank order:
**Cassava +₦84.2K**, **Maize +₦41.5K**, **Tomato −₦112.9K** (tomato carries the
alert accent; its line reads "Unit cost — no yield recorded yet").

There is **no numeric rank badge**. The API returns `crops` sorted by gross
margin descending and has no `rank` field, so the artefact is ordering plus the
profit/alert colouring. The chapter should be worded accordingly.

### 3 · 4.5 Break-even in the past tense

Same card, same frame or a crop of it. Cassava: "**Break-even was 993.7 kg at
the price you got**". Maize: "**Break-even was 7.8 kg at the price you got**" —
matching the chapter's 7.8 kg. Tomato has no break-even line at all (null, the
no-realised-price case), which is itself the shot for the null path.

### 4 · 4.4 Unit cost on both bases, maize — NOT REACHABLE IN THE UI

This state cannot be screenshotted from the application.
`DecisionSupport.tsx` renders only `unit_cost_of_production` → "Unit cost of
production ₦35/kg". The second basis, `unit_cost_per_kg_marketable` =
**41.666666666666664**, is computed in `dss_service.py` and returned by the
endpoint, but **no frontend component reads it — the field is not present in
`frontend/src/types/domain.ts` at all**. The investor report shows the single
basis too, and `/bioprocess/summary` (which carries `total_marketable_mass_kg`)
has a typed client method, `bioprocessService.getSummary`, that nothing calls.

Capture options, while the dashboard is still open: DevTools → Network →
`decision-support` → Response pane (both fields side by side), or the raw file
`docs/ch4-data/dss_per_crop.json`. Both bases exist as data, never as
interface. That absence is the finding.

### 5 · 4.6 Model metrics with the disclosure visible

**URL** `http://localhost:5173/dss` — scroll to **Model quality**. It renders
without running a prediction. Expect R² **0.9762**, MAE **0.2414 t/ha**, and the
amber box "**What these figures measure** … representative synthetic data …
Trained on **6,000** generated samples."

### 6 · 4.7 Model info, untrained state

```
docker exec agrip-backend-1 mv /code/app/ml/models/model_meta.json /tmp/
```

Reload `/dss` → "**The model has not been trained yet.**" plus "No accuracy
figures exist until it has been fitted." `GET /dss/model` keys purely off the
existence of the meta sidecar; there is no service-worker cache on that route
and no restart is needed.

**Do not press Run Prediction during this shot** — `latest_model.joblib` is
still present, so a forecast would succeed and the two panels would contradict
each other.

Restore immediately after, then reload and confirm the metrics are back:

```
docker exec agrip-backend-1 mv /tmp/model_meta.json /code/app/ml/models/
```

### 7 · 4.2 Log-entry form with Bioprocess selected

**URL** `http://localhost:5173/records` → **Log activity** → Activity =
**"Post-harvest drying"**.

**On row 4 of Section 4.8.4:** that record is now historical. The option *was*
removed, and it was **re-added together with its parameter fields** in commit
`856200a` (ticket 08 phase 6, branch `feat/bioprocess-drying`). Selecting it
today reveals: drying method (Sun / Solar dryer / Mechanical / Ambient), mass
in, mass out, moisture in, moisture out (both % wet basis), drying time, and an
optional air temperature; the Amount label gains "— 0 is fine for sun drying".
`buildDryingParams` mirrors the backend validator client-side, so the
unsatisfiable queued record the chapter describes cannot recur: an invalid
payload is rejected before it can reach IndexedDB. There is **no readings
input** (see shot 8).

### 8 · 4.13 Drying result panel — it exists

Fill that same form and save. Use **Crop = Rice, Amount = 0** — *not maize*: a
maize run would add to marketable mass and break the 100 kg / 84 kg / ₦3,500
figures Section 4.3.2 depends on. Suggested values: mass in 60, mass out 50,
moisture 22 → 13, time 8 h.

On save the form is replaced by the result panel: water removed, drying rate,
process loss (against the dry-matter-balance prediction), dry matter, moisture
ratio, Newton k, and a green safe-storage chip (rice threshold 14% wb).

Finding: the Newton k hint reads "**Page fit needs 3+ intermediate readings**" —
the form has no readings input, so the Page model is unreachable from the
interface even though the backend computes it (the seed posts readings
directly).

This temporarily adds a fourth "rice" row (₦0 margin) to the decision-support
panel, which is why shots 1–3 come first. Step 10 removes it again.

### 9 · 4.8 Reversal confirmation dialogue

Still on `/records`. Click **Reverse** on the **rice drying** row just created —
never on a seeded row. Dialog: "**Correct this record?**", the explanatory
paragraph ("nothing is deleted"), the record identified by
activity/description/amount/date, "A correcting entry cannot itself be
corrected", buttons "Keep as it is" / "Post correcting entry".

### 10 · 4.9 Original and contra together

Confirm **Post correcting entry**. The list refetches: the original row is
struck through with a "**Reversed**" pill; the contra row is tinted and pilled
"**Correction of #\<id\>**", described "Reversal of log #\<id\>". Both fit in one
frame.

Caveat for the chapter: `GET /ledger/logs` has no `ORDER BY`, so adjacency is
observed, not guaranteed. In practice the pair is the last two rows.

Afterwards the rice bucket disappears from decision support entirely (reversed
drying runs are excluded from marketable mass, and both money sides net to
zero), so the ledger is back to the three seeded crops. Reload `/` to confirm
the KPIs read ₦12.8K / ₦223.6K / ₦210.8K again.

### 11 · 4.12 360 px, no horizontal overflow

DevTools device toolbar → **360×800**, on `/records` (the widest content, now 15
rows). Expect the sidebar gone with a hamburger in the header, every grid
collapsed to one column, and the table scrolling **inside** its own container
(`.table-scroll > table { min-width: 640px }`) while `main` keeps
`overflow-x: hidden` — the page itself does not scroll sideways. Worth a second
and third frame on `/` and `/dss` at the same width.

---

## Group B — backend unreachable. Capture last, together.

### 12 · 4.10 Offline pending-sync indicator

Return to **desktop width first**: the indicator lives in the sidebar footer,
which at 360 px is inside the drawer.

Two variants, which do **not** show the same thing:

- **DevTools → Network → Offline** (flips `navigator.onLine`): the sidebar shows
  **both** "Offline · showing saved data" **and** "⏳ 1 pending sync". This is the
  shot the chapter wants.
- **`docker compose stop backend` alone**: `isOnline` derives from
  `navigator.onLine`, which stays true, so **no offline chip appears**. The POST
  fails, the record queues, the form says "Network error — saved offline. Will
  retry when connected." and only "⏳ 1 pending sync" shows. **The application
  cannot distinguish a stopped backend from being online** — a genuine finding,
  worth its own frame beside the DevTools one.

Procedure: go offline → `/records` → Log activity → Other, description "Offline
queue demo", amount 500 → Save → screenshot the sidebar footer.

**Clean up before reconnecting:** DevTools → Application → IndexedDB → delete the
queued record. Otherwise it flushes on reconnect and lands as a real ₦500
expense under "Unspecified", adding a fourth DSS row and moving the dashboard
totals. If it does flush, reverse it from `/records`. If the container was
stopped: `docker compose start backend`.

Also worth photographing here: **reload the page while offline on 5173**. The
summary fetch fails, the summary stays zero, and the dashboard renders the
first-run **onboarding screen** rather than the KPI row — a fetch failure
presented as an empty farm. On `4173` the service worker serves the cached
summary and the real figures survive the reload. A clean two-frame finding.

---

## States that cannot be reached, stated plainly

| Shot | Status |
|---|---|
| 4.4 both unit-cost bases | **Absent from the UI.** Computed, returned by the API, rendered nowhere. |
| Page drying-model fit | **Unreachable from the form** — no readings input; backend only. |
| `/bioprocess/summary` | **No screen calls it.** Endpoint and typed client method exist, zero consumers. |
| 4.7 untrained model | Reachable only by removing the meta sidecar — not a state the app can enter on its own once the container has booted (`ensure_model` trains on startup). |
| 4.10 offline chip via stopped backend | **Not reachable** — requires `navigator.onLine` false. |
