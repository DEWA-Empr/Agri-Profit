# Thesis evidence freeze — 2026-09-07

**This document supersedes `docs/EVIDENCE_FREEZE_2026-08-29.md` as the
reporting baseline for the test-suite figures and for the screenshot set in
`Screenshots/`.**

It does **not** supersede the 29 August document wholesale. The performance
figures remain measured at `78a68c2` and are **not re-measured here** — see §4.
The 29 August freeze remains the source for everything this document does not
name.

Everything below was **executed on 7 September 2026** against the commit named
in §1. No figure is copied from an earlier document; every figure quoted here
was produced by running the command shown beside it.

---

## 0. Why this document exists

The thirteen thesis figures in `Screenshots/` were captured from a running
application whose frontend state had never been committed. Four frontend source
files were modified in the working tree — the farm-wide enterprise economics
view, the drying metrics panel and the records browse mode — and the
screenshots show that behaviour, not the behaviour of any commit in the
repository's history.

That meant the figures had no provenance: nobody, including the author, could
have reproduced them from a named commit. This document exists to close that
gap. The working tree is now committed, and §3 states explicitly that the
screenshots belong to it.

---

## 1. Repository identity

| | |
| --- | --- |
| Branch | `main` |
| Reporting baseline commit | `598eab0a02533e9692332d92382d42f16fc9e346` |
| Short SHA | `598eab0` |
| Commit subject | `Freeze thesis evidence state: farm-wide economics view, drying metrics panel, records browse mode` |
| Commit date | Mon 7 Sep 2026 15:35:38 +0900 |
| Parent | `c9c4e13` (`fix(A-01): filter farm records by activity and crop`) |
| Performance baseline commit | `78a68c2` — unchanged, not re-measured (§4) |
| Verification date | 7 Sep 2026, +0900 |

The commit contains five files:

```
frontend/src/features/dss/components/CostStructurePanel.tsx    | 24 +++--
frontend/src/features/dss/components/EnterpriseEconomics.tsx   | 61 +++++++-----
frontend/src/features/farm-records/DryingRunResult.tsx         | 19 ++--
frontend/src/features/farm-records/FarmRecordsPage.tsx         | 28 +++++-
frontend/src/lib/cacheInvalidation.test.tsx                    | 20 +++-
5 files changed, 113 insertions(+), 39 deletions(-)
```

### 1.1 The fifth file, and why it is in this commit

Four files were the working-tree state being frozen. The fifth,
`cacheInvalidation.test.tsx`, is a test correction that the freeze forced, and
it is recorded here rather than left silent.

`EnterpriseEconomics` now opens **farm-wide** instead of opening on a chosen
crop. Break-even prices are deliberately not shown in the farm-wide view — both
prices are per kilogram of marketable output, and marketable mass belongs to a
single crop, so the farm has no divisor. One seed assertion in the
cache-invalidation suite rendered the panel with no crop chosen and asserted a
sentence that lives in the per-crop break-even panel
(`BreakEvenPricePanel.tsx:129`). Under the new default that panel is not on
screen, and the assertion failed.

The correction selects the crop before asserting, and changes nothing about
what the test guards: the subject is still that creating equipment purges the
cached depreciation qualification, and the closing
`expect(bodyText()).not.toContain('1 of your 2 assets')` is untouched. The
failure was a stale assumption about the default view, not a cache-invalidation
defect.

---

## 2. Test suites at this commit

Both suites were run at `598eab0` with a clean tracked working tree.

### 2.1 Backend

```
python -m pytest backend/tests --collect-only -q
python -m pytest backend/tests -q --cov=backend/app --cov-report=term
```

| | |
| --- | --- |
| Tests collected | **426** |
| Passed | **422** |
| Skipped | **4** |
| Failed | **0** |
| Statement coverage | **96%** |
| Statements measured | **1,601** (67 uncovered) |
| Duration | 136.87 s |

These are **identical to the figures recorded at `78a68c2`** in the 29 August
freeze. That is expected and is the point of quoting them: the commit frozen
here touches only frontend files, so the backend evidence carries across
unchanged, and it has now been re-executed to prove it rather than assumed.

### 2.2 Frontend

```
cd frontend && npm run test:coverage      # vitest run --coverage
```

| | |
| --- | --- |
| Test files | **13 passed** (13) |
| Tests | **148 passed** (148) |
| Failed | **0** |
| Statement coverage | **42.14 %** |
| Branch coverage | 32.19 % |
| Function coverage | 34.66 % |
| Line coverage | 42.15 % |

Statement coverage is **42.14 %** — a single measured figure, not a range.

The denominator is deliberate. `vitest.config.ts` sets
`coverage.include: ['src/**/*.{ts,tsx}']`, so the figure is taken over every
source file under `src`, tested or not. Without that setting the v8 provider
measures only the files a test happened to import and reports roughly 91 %,
which describes the tested modules rather than the frontend. 42.14 % is the
honest denominator.

### 2.3 A note on suite stability

`src/features/dashboard/dashboardAccess.test.tsx` failed once, on a 5-second
`waitFor` timeout, during one of four runs on this machine on 7 September. It
passes in isolation and passed in every subsequent run, including the run whose
figures are recorded in §2.2. It is a load-related timing flake in the test
harness, not a defect in the application, and it is recorded here so that a
future re-run which reproduces it is not mistaken for a regression.

---

## 3. Provenance of the screenshots

**The thirteen thesis figures in `Screenshots/` were captured against the
application state now frozen at `598eab0`.** This is the statement those
figures have never previously had.

The thirteen are:

```
fig_4_1.png   fig_4_2.png   fig_4_3.png   fig_4_4.png
fig_4_5.png   fig_4_6.png   fig_4_7.png   fig_4_8.png
fig_4_9.png   fig_4_10.png  fig_4_11.png
fig_x_filter.png            fig_x_pnl.png
```

`Screenshots/` also holds six raw `Screenshot 2026-09-02 *.png` capture files.
Those are working captures, not thesis figures, and are not covered by this
statement.

Two consequences follow, and both matter for how the figures may be cited:

1. **They cannot be reproduced from `78a68c2`.** The farm-wide economics view,
   the drying metrics panel and the records browse mode do not exist at that
   commit. Any attempt to regenerate these figures from the previous baseline
   will produce different screens. `598eab0` is the only commit from which they
   reproduce.
2. **Farm 26 and the sign-in are unchanged; the wider database is not.**
   Signed in as **farm 26**, whose last write was **24 August 2026** — so every
   figure read from that farm is the same at this commit as at the 29 August
   freeze. The database as a whole has moved since freeze §4, and this document
   previously stated otherwise in error. `docs/EVIDENCE_CAPTURE_2026-09-07.md`
   §2 records the census on 7 September 2026: five of nine rows changed —
   `farms` 14 → 15, `users` 13 → 14, `operational_logs` 109 → 110,
   `financial_transactions` 109 → 110, `share_tokens` 10 → 12. `equipment` (3),
   `maintenance_logs` (1), `alembic_version` (`b9e5f30c74a1`) and unpaired
   operational logs (0) are unchanged. The entire delta is one new farm,
   **30, `Miller Farms`**, created 2026-09-01 17:50:20 UTC and holding a single
   `BIOPROCESS` / `DRYING` maize log — see capture §2.1, which also shows every
   farm present on 25 August carrying an identical count, farm 26 included at
   28 logs. **Cite the census at its own date, 29 August 2026 (freeze §4); cite
   farm 26's figures at either.** The frozen commit itself changes presentation,
   not data.

---

## 4. What this document does NOT re-measure

The performance figures — response-time measurements, load characteristics and
everything else recorded under `docs/perf/` and in the 29 August freeze's
performance section — **remain at `78a68c2` and were not re-measured on
7 September.**

This is a deliberate scoping decision, not an omission. The commit frozen here
changes four frontend components and one test file; it does not touch the
backend, the database, the query paths or the deployment composition, which are
what those measurements characterise. Re-running them would produce numbers
that differ only by machine noise, and quoting fresh noise as though it were a
new measurement would be worse evidence than citing the measured original.

**When citing performance, cite `78a68c2`. When citing test figures, the
screenshots, or any frontend behaviour, cite `598eab0`.**

---

## 5. Superseding summary

| Evidence class | Commit to cite | Source document |
| --- | --- | --- |
| Backend test suite | `598eab0` | this document, §2.1 |
| Frontend test suite | `598eab0` | this document, §2.2 |
| Screenshots / figures | `598eab0` | this document, §3 |
| Performance measurements | `78a68c2` | 29 Aug freeze (unchanged) |

Superseding lines naming this document have been added to
`docs/THESIS_REPORTING_STATE.md` and to `docs/EVIDENCE_FREEZE_2026-08-29.md` §1.

No tag was created for this commit. Cite the SHA.
