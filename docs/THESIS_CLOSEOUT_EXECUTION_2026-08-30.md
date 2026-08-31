# Thesis closeout — execution report, 30 August 2026

**This is not another audit.** The three preceding documents diagnosed; this one
records what was **applied to `Thesis_Ch1-5.docx`**. The .docx is now the source
of record, and the audit files below are historical accounts of what was wrong,
not of what the thesis says.

| | |
|---|---|
| Implementation baseline | `78a68c292205acdcac1a52f977fbea31b6e8495e` on `main`, 29 Aug 2026 |
| Implementation changed? | **No.** No file under `backend/` or `frontend/` was modified |
| Document before | 724 paragraphs · 27 tables · **0 figures** · 9 reference entries |
| Document after | 747 paragraphs · **30 tables** · **3 figures** · **29 reference entries** |
| Output | `Thesis_Ch1-5.docx` (38,012 words) and `Thesis_Ch1-5.pdf` (164 pages: xix + 145) |
| Backup | `backups/Thesis_Ch1-5.BEFORE_CLOSEOUT_20260830_0228.docx` |

---

## 1. Input inventory

**Used:**

| Input | Standing |
|---|---|
| `Thesis_Ch1-5.docx` | The document. Edited. |
| `docs/THESIS_CLOSEOUT_2026-08-30.md` | Evidence baseline (§2), limitations register (§9), capture plan (§7), claims-that-must-not-appear (§11) |
| `docs/THESIS_CH5_AND_CONSISTENCY_AUDIT_2026-08-30.md` | The 60-row Chapter 5 correction plan, the remap table, the draft §5.1.2, the numerical register (N-01…N-40), the cross-chapter register (X-01…X-12) |
| `docs/EVIDENCE_FREEZE_2026-08-29.md` | Primary evidence: per-file test counts, coverage, security probes, census |
| `claude/Thesis_Ch4-5_DRAFT.md` | **A fully corrected Ch4+Ch5 draft that had never been applied.** Its prose was used where correct |
| `.scratch/chapter-corrections.md` | Ch1–3 redline. Partly stale (predates break-even and ranking being built) — used selectively |
| `MERGE_AUDIT.md` §10 | The twelve missing references, all marked *requires external source verification* |
| `Updated B.Tech Final Project Guideline…pdf` | Chapter 5 structure, reference minimums, table/figure rules |

**Re-verified independently during this session, not taken on trust:**

- Backend suite at the baseline: **418 passed, 4 skipped, 0 failed, 96%, 1,594 / 66** — and the eleven modules below 100%, whose missed counts sum to exactly 66.
- Frontend suite: **13 files, 148 tests, 148 passed** (vitest JSON reporter). Per-file counts taken from that run, so Table 4.5 is measured rather than transcribed.
- The Page-model fixture parameters (`k = 0.30`, `n = 0.75`, `M₀ = 30.0 %wb`) read from `test_bioprocess_service.py`.
- The drying-readings input exists (`DryingFields.tsx`), closing a `[CONFIRM]`.
- The production stack was built and started; the demonstration farm authenticates and holds its data.
- **Twenty-one bibliographic records verified against the publishers** (see §7).

---

## 2. Submission blockers

| Blocker | Status |
|---|---|
| **A — post-harvest drying orphaned** from aim, objectives, scope, literature and design | **RESOLVED.** Objective (v) added; aim widened; §1.5 scope rewritten; **new §2.7** (2.7.1 thin-layer models, 2.7.2 the African context and the costing gap) with six verified sources; **new §3.6.9** post-harvest drying module; §2.8 gap statement extended; Objective (v) row added to Tables 4.28 and 5.1; §5.1.3 and §5.2.2 carry it through |
| **B — livestock claimed, not implemented** | **RESOLVED.** §1.5 now scopes crop enterprises and states livestock as explicitly out of scope with the reason; §1.4's "crop or livestock level" corrected |
| **C — Chapter 5 structure** | **RESOLVED.** Retitled `5.0 SUMMARY, CONCLUSION AND RECOMMENDATIONS`; remapped to the mandated 5.1 / 5.2 / 5.3 with no analysis lost |
| **D — references incomplete** | **RESOLVED for completeness, OPEN on recency.** 9 → 29 entries; every cited work now has one. Recency is 44.8%, not 70% — see §7 |
| **E (found, not in the brief) — Chapter 3 described a subsystem that does not exist** | **RESOLVED.** §3.6.8 rewritten as *Designed, Not Implemented* |

---

## 3. Objective traceability matrix

Now Table 5.1 in the thesis, and Table 4.28 in Chapter 4.

| Objective | Ch1 | Ch3 design | Ch4 evidence | Ch5 conclusion | Status |
|---|---|---|---|---|---|
| **(i)** Socio-technical barriers | §1.3 (i) | §3.3.2 (a)–(e); §3.6.1; §3.6.8 *designed, not implemented* | §4.2; census 109/109/0; §4.10; §4.11.4 | §5.1.3, §5.2.2 | **PARTIALLY ACHIEVED** |
| **(ii)** Records → decision-support metrics | §1.3 (ii), **narrowed** | §3.5; §3.6.2; §3.6.5 (nine quantities); **§3.6.10** | §4.6, §4.7; both services 100% | §5.1.3, §5.2.1 | **ACHIEVED** as arithmetic, on one seeded farm |
| **(iii)** Secure data sharing | §1.3 (iii) | §3.6.6; §3.6.7; **§3.7 expanded** | §4.3.3; **new §4.12** | §5.1.3, §5.2.3 | **ACHIEVED** as implementation + internal verification; **not validated in practice** |
| **(iv)** Usability, cost, viability | §1.3 (iv) | §3.8, **reconciled**; §3.8.4 *specified, not executed* | §4.3–§4.5, §4.10–§4.12; §4.13 reports no figure | §5.1.3, §5.2.3 | **PARTIALLY ACHIEVED** |
| **(v)** Post-harvest drying → financial record | **§1.3 (v), NEW** | **§2.7 literature; §3.6.9 module** | §4.8; coupling to §4.6.2 | §5.1.3, §5.2.1, §5.2.2 | **DEMONSTRATED AS PROTOTYPE** |

All five chains are now complete. Objective (ii) was narrowed because "optimising farm mechanisation and input allocation" is not implemented — `equipment_id` and `hours_used` are captured and costed nowhere.

---

## 4. Chapter 5 — what was done

Rebuilt against the baseline and remapped. **No analysis was deleted to fit the structure.**

| Mandated section | Content | Source |
|---|---|---|
| **5.1 Summary** | 5.1.1 The problem, the approach, and the procedures used | old §5.1 + §5.8 ¶1, expanded to the guideline's requirement |
| | **5.1.2 Summary of Findings** | **NEW** — seven areas, every figure baseline-verified |
| | 5.1.3 Achievement against the research objectives + **Table 5.1** | old §5.2.1–§5.2.4, corrected, **plus Objective (v)** |
| **5.2 Conclusion** | 5.2.1 Interpretation of the major findings | old §5.3.1–§5.3.6 **+ "A recorded defect that was not one"** |
| | 5.2.2 Comparison with the literature | old §5.4 **+ a post-harvest paragraph** |
| | 5.2.3 Limitations | old §5.5, corrected and classified IL / EL / FW / OOS |
| | 5.2.4 Conclusion | old §5.8 |
| **5.3 Recommendations** | 5.3.1 Implications | old §5.6 **+ an evaluation-practice implication** |
| | 5.3.2 Recommendations and suggestions for further studies | old §5.7, Tiers A/B/C **rebuilt** |

**Deletions from the recommendations, because each proposed fixing something already true or already fixed:** old Tier A(a) contra-entry attribution, A(b) monetary bounds, A(c) equipment edit path, A(e) first half, B(e) performance re-run, C(b) RMSE half, C(c) both halves, C(d). **Tier A is now four genuine prerequisites** — observability, TLS for a real hostname, externalising the model artefact, and moving the rate-limit counters out of process.

**Also removed:** the "Note for submission" about missing references (the references are complete).

---

## 5. Cross-chapter consistency register

| # | Was | Now |
|---|---|---|
| X-01 | §3.6.4 "future refinement" vs Ch4 "captured, not consumed" vs Ch5 "already stores it" | **"captured but not costed"** in all three; the no-figure rule stated in §3.6.4, Table 4.2 row 13 and §5.2.3 |
| X-02 | §3.6.1 read caching "a planned enhancement" | Restated **as built**, with the exclusions and the purge-on-write design |
| X-03 | §3.3.2(b) claimed offline capture generally | Scoped to **writes**; offline reads named as the weaker service-worker guarantee |
| X-04 | "standardised, exportable reports" | **CSV only**, stated as the only format |
| X-05 | §3.6.5 RMSE "may additionally be reported" | **"is additionally reported"**; §2.6.4 likewise; the Ch5 gap sentence deleted |
| X-06 | §3.6.7 token revocable only | **+ 90-day expiry, hashed at rest, bearer refusal, single 404** — carried into §5.1.3 |
| X-08 | Abstract carried 190 / 93% / 89 and the 17 Aug performance set | **Abstract fully re-sourced** |
| X-09 | Ch4 §4.14 listed five defects; Ch5 restated all five | **Ch4 corrected first**, then Ch5: two stand, one withdrawn, two closed, two added |
| X-10 | §1.5 "lightweight statistical regression" vs a Random Forest | §1.5 says **tree-based ensemble**; §5.2.2 argues the step up the ladder as a design decision |
| X-11 | No architecture diagram, no ERD | **Figures 3.1, 3.2, 3.3 added** |
| X-12 | Ch4 says five crops; per-crop tables captioned farm 26 | Captions re-anchored to the baseline; **no farm-wide total is quoted from `dss_per_crop.json`** |
| **New** | §3.6.8 described a USSD/SMS webhook in the present tense | **Rewritten as designed-not-implemented**; NFR (d) restated as a requirement the release does not meet |
| **New** | §3.8 "The evaluation actually undertaken" included usability | **"specified"**; three executed, one not, stated in Ch3 |
| **New** | §3.7 had no authorisation model | **Expanded**: RBAC, throttling, credential hygiene, and the named residuals |
| **New** | Ch3 had no module for drying or enterprise economics | **§3.6.9 and §3.6.10 added** |
| **New** | Table 3.1 omitted `ShareToken`, `reverses_id`, `crop`, `client_id` | **Six rows added** |
| **New** | §3.4.2 called the backend asynchronous | Corrected: handlers are synchronous, run in a threadpool |
| **New** | §2.6.1 named seven predictor features and three prediction targets; four features and one target exist | Corrected to the implemented four (crop, rainfall, fertiliser, soil pH) and the single target (yield); the rest restated as intended direction |
| **New** | §2.6.3(a) said Tier 1 "runs fully offline" and computes "input thresholds" | Corrected: computation is server-side with cached availability; input thresholds removed as never implemented |
| **New** | §2.6.5 claimed ranked option sets and break-even early warnings | Ranking and break-even *yield* claimed (both built); the input-mix optimiser and threshold warning moved to intended direction |

---

## 6. Numerical consistency register

Every row applied document-wide, **including the abstract**.

| Metric | Was | Now |
|---|---|---|
| Backend tests | 190 | **422 collected · 418 passed · 4 skipped · 0 failed** |
| Backend coverage | 93% | **96%** |
| Statements / missed | 1,286 / 91 | **1,594 / 66** |
| Frontend tests / files | 89 / 9 | **148 / 13** |
| Frontend coverage | 33.48% (378/1,129) | **43.18% (558/1,292)**, quoted *with* the backend figure |
| Timing robustness | absent | **stated**: one test is not timing-robust in a full-suite run under load |
| RMSE | `[PLACEHOLDER]` | **0.4883 t/ha** |
| ML reproducibility | "not reproducible from the repository" | **reproducible to six decimals**, dataset SHA-256, 18 tests, two Python versions |
| Cold transfer | 243,724 B | **139,245 B over 8 requests** |
| Cold slow-3G FCP | 7,679.9 ms | **5,661.2 ms** |
| Warm FCP / LCP | 116.4 / 1,613.8 ms | **70.6 / 1,612.0 ms** |
| Warm transfer | "nothing at all" | **127 B over 7 requests** (the manifest icon) |
| **FCP ratio** | "sixty-six" | **about eighty** (5,661.2 ÷ 70.6 = 80.2) |
| **LCP ratio** | "about five" | **about three and a half** (5,661.2 ÷ 1,612.0 = 3.5) |
| Transfer time @ 400 Kbps | 4.87 s | **2.79 s** |
| Lighthouse scores | 95 / 57 | **99 slow-4G / 65 slow-3G**, with the benchmark-index non-comparability stated |
| Baseline identity | `59a6286`, "development stopped at that tag" | **`78a68c2`, 29 Aug 2026**; the false sentence deleted |
| Census | "109 / 109" | **+ `alembic_version b9e5f30c74a1`, 0 unpaired** |
| Break-even price | ₦41.666… only | **CASH ₦41.67 and TOTAL ₦42.37**, distinguished from break-even *yield* |
| Pricing placeholder | `[CONFIRM — re-check provider pricing pages]` | **resolved** by restating the retrieval date and the estimate's standing |

**Unchanged and re-verified as load-bearing:** ₦450/kg · 100 kg · 84 kg · 86.21 kg · ₦35.00 → ₦41.67 · 19% · ₦6.67 · 7.78 kg · R² 0.9762 · MAE 0.2414 · 88.25%/11.75% · 178.9–202.8 MiB · $15.40 ≈ ₦20,950 · ₦419/₦210/₦105/₦42 · 8.57 s.

**Standing rules now honoured throughout:** "CI is green" appears nowhere; no machine-hour, utilisation or cost-per-hour figure appears anywhere; no score or TBT is compared across the two measurement dates.

Occurrences of the superseded figures that **remain deliberately**: Table 4.7 and §4.3.4 (the reconciliation, which must show both states), §4.10.3 (the measured movement against the 17 August build), and the retraction sentences in §4.6.4, §4.7.5, §4.9 and §5.2.1. Each is explicitly framed as superseded or withdrawn.

---

## 7. Reference correction plan — done, with one open item

**9 → 29 entries. Every cited work now has one; no entry is uncited.**

| Correction | Status |
|---|---|
| 12 missing works entered | **Done** — 11 verified against publishers; Jaiyeola open (below) |
| **Huang (2020) → Xiong, Dalhaus, Wang, & Huang (2020)** | **Done**, all occurrences (verified: *Frontiers in Blockchain*, 3, Art. 7) |
| **Mhlanga (2023) → Mhlanga & Ndhlovu (2023)** | **Done**, all occurrences (verified: *Human Behavior and Emerging Technologies*, 2023, Art. 6951879) |
| **Nirosha (2024) removed** | **Done** — no publication record exists. Its four claims are carried by Abbasi et al. (2022), Mhlanga & Ndhlovu (2023) and the new Abioye et al. (2026) |
| **Olisah et al. §2.6.3(c) misuse** | **Done** — verified from arXiv that their **DNN performed best**. The recommendation of tree ensembles is now sourced to van Klompenburg et al. alone; Olisah is cited for its pre-processing finding, with its preprint status disclosed, and §5.2.2 states the counter-case |
| **Edge-computing misattribution (§2.1.3)** | **Done** — removed from Mhlanga & Ndhlovu, re-sourced to Abiri et al. (2023) and Dayıoğlu & Türker (2021), with a sentence saying what Mhlanga & Ndhlovu *do* support |
| **Giua et al. re-dated 2020 → 2021** | **Done** (*British Food Journal*, 123(3), 884–909) |
| **APA 7** | **Done** — Fountas et al. ellipsis replaced with the full ten-author list; publisher cities dropped (Taylor & Francis, Wiley, ACM); diacritics restored (Dayıoğlu, Türker, Novković, Sørensen) in list *and* in text |
| **Sources for the new §2.7** | Lewis (1921), Page (1949), Henderson & Pabis (1961), Erbay & Icier (2010), Onwude et al. (2016), Baidhe et al. (2024), FAO (n.d.), Kay, Edwards & Duffy (2016) — the last two also close the two open implementation citations of ADR 0002 |

### Two items needing your decision

**(a) Jaiyeola (2023) — the one entry I could not complete.** The author (Temitayo Jaiyeola, BusinessDay Nigeria) and the underlying GSMA statistic are confirmed, but I could not identify the specific 2023 article. Rather than invent a title, the entry reads:

> Jaiyeola, T. (2023). **[AUTHOR TO SUPPLY:** exact article title, publication date and URL of the BusinessDay Nigeria article reporting the GSMA figures that 32% of rural Nigerians owned a smartphone in 2022 against 58% of urban Nigerians**]**. BusinessDay Nigeria.

**This bracket must be filled or the citation replaced before submission.** It supports the 68% figure in §1.1, §1.5, §2.4.2, §5.1.3 and §5.2.2 — the headline socio-technical constraint of the thesis, so it should not simply be dropped. The cleanest alternative is to cite the GSMA report directly.

**(b) The 70%-recency requirement cannot be met honestly.** 29 entries; **13 dated 2021 or later = 44.8%**. The 16 pre-2021 works are the usability instruments (Brooke 1996; Nielsen 1994; Nielsen & Molich 1990), the drying models the thesis actually fits (Lewis 1921; Page 1949; Henderson & Pabis 1961), the drying reviews (Erbay & Icier 2010; Onwude et al. 2016), the enterprise-budget text (Kay et al. 2016) and the FMIS/ML reviews the argument rests on (Fountas 2015; Carrer 2017; Tummers 2019; van Klompenburg 2020; Xiong 2020; Husemann & Novković 2012). Holding all sixteen, 70% would require **38 post-2021 entries — a 54-item list**, which is padding. **Put this to your supervisor**: either the requirement is read as a target rather than a threshold, or a small number of recent reviews are added *and cited* in Chapters 1 and 2. I did not pad.

---

## 8. Table and figure plan

**Tables: 30 (was 27). Numbering sequential, no gaps, no duplicates. All 30 are now referenced in body text (was 5 of 27).**

- Table 4.2: rows 11 and 12 were **false** and are corrected; row 13 restated; **7 rows added** (authorisation, throttling, token lifecycle, input bounds, equipment correction, drying readings, the unconsumed summary endpoint).
- Tables 4.3, 4.4, 4.5, 4.7, 4.20 **re-sourced from measurements taken this session**.
- Table 4.19: RMSE filled; fingerprint, seeds, zero-real-records disclosure and reproducibility added.
- **New Table 4.24** (security and authorisation, 13 rows) and **Table 4.25** (deployment, migration and recovery, 12 rows).
- Tables 4.26 and 4.27 (usability) stay **deliberately empty** — the editorial `[INSERT VERIFIED RESULT HERE]` markers were replaced with em dashes so nothing reads as a placeholder.
- Table 4.28 re-sourced, **Objective 5 row added**.
- **New Table 5.1** — Chapter 5 previously had no table at all.

**Figures: 3 (was 0). The bracketed "[NO FIGURES ARE PRESENT…]" note is gone.**

- **Figure 3.1** System architecture · **Figure 3.2** Entity-relationship diagram · **Figure 3.3** Paired-write sequence.
- Each is referenced in the body, captioned below and centred, and generated at 2× for print (`docs/figures/*.png`, reproducible from `figures.py`).
- These are **author-drawn design diagrams**, and §4.5.1 says so explicitly so that no reader mistakes them for evidence captures.

**Interface screenshots — not captured, and §4.5.1 now explains why rather than leaving a placeholder.** I brought the stack up and confirmed the demonstration data is live, but signing in means entering a password into a form, which I don't do. If you sign in yourself I can drive the capture from there. The §4.5.1 text as it stands is defensible without them — it argues that the live API responses already reported *are* the stronger form of the same evidence — and Tier B(g) records the capture as outstanding presentation work. **If your department expects interface screenshots in a B.Tech report, this is the one content item still open.**

---

## 9. Limitations and recommendations alignment

§4.15 and §5.2.3 now classify every limitation as **IL** (implementation), **EL** (evaluation), **FW** or **OOS**, with an explicit paragraph saying that no usability study does not mean an unusable interface, no load testing does not mean it cannot scale, a synthetic evaluation does not make the model worthless, and no security assessment does not mean authentication and authorisation are absent.

The defect list moved from **five known defects** to: **two standing** (a reversal cannot itself be rolled back; the stale-revalidation window, reported as a hypothesis), **one withdrawn** (per-crop reversal netting), **two closed** (monetary bounds, equipment edit path), **two added** (equipment attribution captured-not-costed; the unconsumed `/bioprocess/summary`). §5.2.3 states plainly that the defects were found by the project's own audit and closed before submission.

The deployment limitation is refined from "the system has never been deployed" to the **demonstrated-path versus performed-deployment** distinction, which is both more accurate and more creditable. Of the four things §5.5 previously said were absent — TLS, backup and recovery, secret management, observability — **only observability survives**; the other three were false.

---

## 10. Final submission checklist

### Content
- [x] Chapter 1 matches final system scope
- [x] No livestock overclaim
- [x] Post-harvest drying has objective, scope, literature and design alignment
- [x] Chapter 2 citations verified; three misattributions corrected; one unverifiable source removed
- [x] Chapter 3 matches implementation (USSD, usability, RBAC, drying, enterprise economics, async, Table 3.1)
- [x] Chapter 4 uses final evidence
- [x] Chapter 5 uses final evidence

### Objectives
- [x] All five objectives trace across Chapters 1–5
- [x] Partial achievements honestly described (two partial, one prototype)
- [x] No objective claims unsupported functionality (Objective (ii) narrowed)

### Evidence
- [x] Backend figures use the final baseline — independently re-run this session
- [x] Frontend timeout honestly reported
- [x] ML reproducibility correctly stated
- [x] RMSE correct (0.4883 t/ha)
- [x] Performance arithmetic correct (80×, 3.5×, 2.79 s)
- [x] Retracted defects removed and converted into a methodological finding

### References
- [x] Every cited work appears in the references
- [x] Nirosha removed · Huang corrected · Mhlanga & Ndhlovu corrected · edge-computing attribution removed · Olisah misuse corrected
- [x] APA 7 applied
- [x] Minimum of 15 met (29)
- [ ] **Jaiyeola (2023) bracket to be filled — MUST FIX**
- [ ] **70% recency not met (44.8%) — supervisor decision**

### Tables and figures
- [x] Every table discussed in text (30 of 30)
- [x] Table numbering correct and sequential
- [x] Real figures added (3 design diagrams)
- [x] Every figure supports a thesis claim and is referenced
- [x] List of Figures contains no editorial placeholder
- [ ] **Interface screenshots — open, needs you to sign in**

### Final document
- [x] TOC regenerated (120 entries) with real page numbers
- [x] List of Tables regenerated (30) with real page numbers
- [x] List of Figures regenerated (3) with real page numbers
- [x] Page numbering checked — Roman preliminaries, Arabic body restarting at 1, section break intact
- [x] PDF generated (163 pages)
- [ ] **PDF visually inspected — you should page through it**

---

## 11. The three lists

### MUST FIX BEFORE SUBMISSION
1. **Fill the Jaiyeola (2023) bracket** in the reference list, or replace the citation with the GSMA report, in the list and at its five in-text sites.
2. **Page through the PDF.** Check that Figures 3.1–3.3 sit on their pages without awkward breaks, that no table splits badly across a page, and that the front-matter page numbers still match after any edit you make.
3. **Take the recency arithmetic to your supervisor** (§7b) and record the decision.

### FIX IF TIME ALLOWS
4. Capture the interface screenshots, following the plan in `docs/THESIS_CLOSEOUT_2026-08-30.md` §7. Every capture must show a populated state the system actually produced; nothing may be staged.
5. Re-run the negative controls (§4.4) and the driven-browser probe (§4.5.3) at `78a68c2` so they need not be attributed to earlier commits.
6. Add the drying-curve and cold-versus-warm performance figures.
7. Apply the remaining terminology decisions (Part 4 of the consistency audit) — "the platform" / "the application" / "the system" are used consistently where a correction touched the text, not yet everywhere.

### POST-SUBMISSION
8. Run the usability panel. It is still the highest-value remaining evidence in the project and it is what closes Objective (iv).
9. Tier A of §5.3.2: observability, TLS for a real hostname, externalised model artefact, out-of-process rate-limit counters.
10. Component tests for the page and form layer; an end-to-end browser test; PostgreSQL concurrency; independent security review and load testing.

---

## 12. Two things I found that you should know

**1. A 500 where a 422 belongs.** Posting form-encoded credentials to `/api/v1/auth/login` (which expects JSON) returns **HTTP 500**, not 422: the validation-error handler at `backend/app/main.py:120` tries to serialise a `bytes` value into JSON and raises `TypeError`. The correct JSON request works normally. I did **not** fix this — the implementation is frozen for the thesis — and I did **not** put it in the thesis, because a single unreproduced observation is exactly the kind of finding §4.6.4 now warns against. Reproduce it before you decide whether it belongs in the limitations.

**2. The corrected Chapter 4–5 draft had been written and never applied.** `claude/Thesis_Ch4-5_DRAFT.md` contained most of what Chapters 4 and 5 needed. It is now superseded by the .docx. Treat `claude/Thesis_Ch4-5_DRAFT.md` and `.scratch/chapter-corrections.md` as historical — re-applying either would reintroduce retracted findings.

---

## 13. Notes for whoever edits the document next

1. **The .docx is the source of record.** The audit files record what was wrong, not what the thesis says.
2. **Front-matter lists are plain styled paragraphs with typed page numbers, not Word TOC fields.** Regenerate them from the body with python-docx, then read page numbers from Word **read-only**. Writing to `Paragraph.Range.Text` through Word COM merges paragraphs and destroys the front matter — it did, once, during this session, and the lists were rebuilt from the body afterwards.
3. **The preliminary/body section break lives on an empty `Normal` paragraph immediately before `CHAPTER ONE`.** It carries the Roman numbering and the preliminary footer. Deleting it collapses the document to one section and renumbers the whole thesis in Arabic. It was lost once and restored from the backup.
4. **Correct Chapter 3 before 4, and 4 before 5.** Each interprets the one before it.
5. **Quote backend and frontend coverage together, or neither.**
6. **Never write "CI is green"**; never quote a machine-hour, utilisation or cost-per-hour figure; never compare a Lighthouse score or TBT across the 17 and 29 August sets; never quote a farm-wide total from `docs/ch4-data/dss_per_crop.json`.
7. **The maize chain — ₦450/kg, 100 kg, 84 kg, 86.21 kg, 7.78 kg, ₦35.00, ₦41.67 — is load-bearing across two chapters.** Do not change a division in it without re-stating the whole chain. Note that ₦41.67 is now explicitly the **cash** basis; the total basis is ₦42.37.
8. **A state that cannot be captured is stated as absent, never staged.**
