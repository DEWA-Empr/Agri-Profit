# Chapter Five and whole-thesis consistency audit — 30 August 2026

**Scope.** Chapter Five correction plan, objective-to-conclusion matrix,
cross-chapter inconsistency register, numerical consistency register,
table/figure register, submission checklist, prioritised action list.

**Authorities used, in priority order.**

1. `Updated B.Tech Final Project Guideline for 2025_2026_v1.pdf` — departmental
   structure and formatting requirements.
2. `docs/THESIS_CLOSEOUT_2026-08-30.md` — the Chapter 4 evidence baseline,
   contradiction register (C-01…C-27), Chapter 3 audit, verified limitations
   register (items 1–25) and the must-not-claim list.
3. `docs/EVIDENCE_FREEZE_2026-08-29.md` — the underlying measurement document.
4. `Thesis_Ch1-5.docx` — the document under audit (1,424 paragraphs, extracted
   and read in full).

**Baseline.** `78a68c292205acdcac1a52f977fbea31b6e8495e` on `main`, 29 Aug 2026.

**Method note.** No figure in this document was chosen by inference. Every
number is either quoted from the closeout baseline or computed from it, and
where computed the arithmetic is shown.

---

## PART 0 — Phase 1 input inventory

| Required input | Available? | Where |
|---|---|---|
| Chapter 1 objectives | **Yes** | `Thesis_Ch1-5.docx` §1.3, four objectives, roman-numbered |
| Chapter 3 implementation verification | **Yes** | Closeout §5 (§5.1–§5.7), audited at `78a68c2` |
| Chapter 4 evidence baseline | **Yes** | Closeout §2 (§2.1–§2.8) |
| Verified results | **Yes** | Closeout §2, §3, §8 (T1–T19) |
| Verified limitations | **Yes** | Closeout §9, items 1–25 |
| Known partial implementations | **Yes** | Closeout §5.2(b) offline writes; §5.6 usability; limitation 18 |
| Known non-implemented features | **Yes** | Closeout §5.4 (USSD/SMS §3.6.8); §5.2(d) NFR feature-phone; limitation 20 |
| **Institutional Chapter 5 structure** | **Yes** | Guideline: `5.0 SUMMARY, CONCLUSION, AND RECOMMENDATIONS` → `5.1 Summary`, `5.2 Conclusion`, `5.3 Recommendations` |

**Missing inputs — nothing is invented in their place.** No usability data, no
field-trial data, no load-test data, no independent security assessment, no CI
run record for `78a68c2`, no production deployment record, no real farm data.
Chapter Five must state each absence, not bridge it.

**Nothing in this audit required new measurement.** Chapter Five as written is
complete prose; the work is correction and restructuring, not authoring.

---

## PART 1 — Chapter Five correction plan

Chapter Five **already exists** (`Thesis_Ch1-5.docx`, §5.0–§5.8, ~5,900 words).
It is well-argued and its analytical structure is sound. It is, however,
**written entirely against the superseded `59a6286` freeze** and carries every
figure and every defect claim that the 29–30 August verification overturned. Not
one 29 August figure appears anywhere in it.

This section therefore gives an **exact correction plan**, not a redraft.

### 1.1 Structural decision required — the chapter does not match the guideline

The departmental guideline mandates:

```
CHAPTER FIVE
5.0   SUMMARY, CONCLUSION, AND RECOMMENDATIONS
5.1 Summary          — Restatement of the problem, and description of procedures used.
5.2 Conclusion       — Conclude your objectives achieved.
5.3 Recommendations  — Give recommendations arising from the study.
                       Give suggestions for further studies.
```

The thesis has **`5.0 DISCUSSION, CONCLUSION AND RECOMMENDATIONS` with eight
second-level sections (5.1–5.8)**. Title and structure both deviate.

**Recommended resolution — remap, do not rewrite.** Retitle the chapter to the
mandated title and demote the existing sections one level, so the three mandated
headings become the top level and no prose is lost:

| Mandated section | Absorbs | Existing content |
|---|---|---|
| **5.1 Summary** | 5.1.1 The problem and the approach | old §5.1 Introduction + §5.8 ¶1 |
| | 5.1.2 Summary of findings | **NEW — must be written** (see §1.3) |
| | 5.1.3 Achievement against the research objectives | old §5.2.1–§5.2.4, as four subheaded blocks |
| **5.2 Conclusion** | 5.2.1 Interpretation of the major findings | old §5.3.1–§5.3.6 |
| | 5.2.2 Comparison with the literature | old §5.4 |
| | 5.2.3 Limitations | old §5.5 |
| | 5.2.4 Conclusion | old §5.8 ¶¶2–5 |
| **5.3 Recommendations** | 5.3.1 Implications | old §5.6 |
| | 5.3.2 Recommendations and further work | old §5.7 (Tiers A/B/C, corrected) |

**Alternative, lower-effort:** keep the eight-section structure and change only
the chapter title to the mandated one. This is a supervisor's call. The remap is
recommended because the guideline's section list is explicit and an examiner can
check it against the table of contents in ten seconds.

*Note:* the guideline says "Avoid third level of list, use subheadings" — it
constrains **lists**, not headings. Chapters 2, 3 and 4 already use third-level
headings (2.6.4, 3.6.8, 4.10.3), so 5.1.3 is consistent with the document.

### 1.2 Corrections required section by section

Severity: **F** = false at baseline (evidence contradicts) · **S** = stale figure ·
**U** = understated (costs the thesis credit) · **G** = guideline compliance.

| # | Location (current §) | Text as written | Severity | Required correction | Authority |
|---|---|---|---|---|---|
| **5-01** | 5.2.1 | "a service worker that was shown by driven browser to serve the whole application shell with the network disconnected" | **S** | Attribute it: "…shown by a driven-browser probe at commit `c16924e` on 17 August 2026, against service-worker configuration the subsequent merge did not change." | Closeout §9 item 8; must-not-claim 19 |
| **5-02** | 5.2.1 | "a reasoned ₦105 per farm per month at a two-hundred-farm tenancy" | **OK** | Keep. Already carries "reasoned". Confirm the word survives editing. | Closeout §2.5 |
| **5-03** | 5.2.1 | "the feature-phone entry channel of Section 3.6.8 — is not present in the frozen build" | **U/S** | Strengthen and re-anchor: the channel is **not implemented in any form** — no route, no webhook, no parser, no sender-to-farm mapping, no test, no simulated harness. Replace "the frozen build" with "the submitted build". Chapter 3 §3.6.8 must be rewritten in the conditional first, or Chapter 5 contradicts it. | Closeout §5.4, §9 item 20 |
| **5-04** | 5.2.2 | "The per-crop breakdown does not net reversals, so the very view a farmer would use to choose between enterprises is misleading after any correction — a defect in the feature that carries the objective." | **F — highest severity in the chapter** | **Delete the claim.** Per-crop decision support **does** net reversals, and did so at the freeze commit too. Reversing ₦25,000 moved that crop 35,000 → 10,000 and unit cost ₦2,916.67 → ₦833.33, with no `Unspecified` bucket at any point. Five named tests pin it. Replace with the methodological finding (see 5-25). | C-08 |
| **5-05** | 5.2.2 | "one computed metric, the Olympic-average baseline, has no interface surface at all: it is computed, tested, served and invisible." | **F** | **Delete.** `EnterpriseEconomics.tsx:49` calls `dssService.getYieldBaseline()` and renders `YieldBaselinePanel` at line 152. All six enterprise endpoints are reachable. | C-15 |
| **5-06** | 5.2.2 | Tier-1 metric list (nine metrics) | **OK** | Keep — accurate and, unusually, matches the code. Note that Chapter 3 §3.6.5 names only two of the nine and must be brought up to Chapter 5's own account. | Closeout §5.1 |
| **5-07** | 5.2.3 | The whole objective-3 discussion: auth, farm scoping, share tokens, ledger immutability | **U — materially** | **Expand.** The section omits every security capability the hardening merge added and the freeze verified live: RBAC over **3 roles / 12 permissions** with permission checked *before* scope so a refusal is never an existence oracle; login throttling (10 failures / 900 s, the 11th returns **429** with `Retry-After: 896`, and the refusal names no account); share-token **90-day expiry** verified to the second, **hashed at rest**, bearer-use → **401**, revoked/unknown/expired all → an **identical 404** so there is no existence oracle; raw token **absent from all three logs**, replaced by a stable 12-hex non-reversible fingerprint; monetary input bounds (−1,000,000 / 2,000,000,000 / `Infinity` / `NaN` each → **422**); `POST /dss/train` **→ 403 even for the owner**. This is the direct answer to Objective 3 and the largest body of unreported verified evidence in the project. | Closeout §2.7, §5.5 |
| **5-08** | 5.2.3 | "the investor-facing report reuses the per-crop aggregation, so it inherits the reversal defect described above" | **F** | **Delete.** The investor report returned the same **netted** figures unauthenticated. | C-08 |
| **5-09** | 5.2.3 | "The boundary is proven by tests and not by an independent security assessment" | **OK** | Keep verbatim. Still true and still the correct bound. | Closeout §9 item 3 |
| **5-10** | 5.2.4 | "190 passing backend tests at 93% statement coverage and 89 passing frontend tests" | **S** | → "**422 tests collected, 418 passed, 4 skipped, 0 failed, at 96% statement coverage (1,594 statements, 66 missed); 148 frontend tests in 13 files at 43.18% statement coverage (558/1,292)**." Quote the two coverage figures **together** — 96% alone misrepresents the system. State that counts are pytest *collected* counts. Add: one frontend test (`dashboardAccess.test.tsx`) is not timing-robust in a full-suite run — a harness limitation, observed on two separate days, not an application defect. | C-01…C-04, C-07; closeout §9 item 14 |
| **5-11** | 5.2.4 | "Performance benchmarking established that the application is bandwidth-bound below roughly 1 Mbps and that a repeat visit transfers nothing at all" | **S/F** | Re-source to the 29 August set. "Transfers nothing at all" is **now false by measurement**: a warm load still transfers **127 B over 7 requests** — the manifest icon `pwa-192x192.png`, absent from the Workbox precache. Report it; a small measured defect strengthens the chapter. | C-11; closeout §9 item 17 |
| **5-12** | 5.2.4 | "an estimated $15.40 — approximately ₦20,950 — per month" on "178.9–202.8 MiB" | **OK, qualify** | Keep the figures. Add that the total is **part-measured and part-assumed** — the static PWA server and the OS/container runtime were not sampled — and that 145.5 MiB is a **lower bound** on the startup peak, not the peak, because the widest sampling gap (4.11 s) falls across the steepest part of the climb. Give the conversion basis: CBN ₦1,360.58 = US$1 as at 12 August 2026. | Closeout §2.5, §9 item 21 |
| **5-13** | 5.2.4 | "The performance figures … characterise an earlier build than the frozen one." | **S** | **Delete.** They now characterise the submitted build: Lighthouse 13.4.1 at `78a68c2`. | C-11 |
| **5-14** | 5.2.4 | Usability strand outstanding | **OK** | Keep verbatim. It is the honest core of the objective-4 verdict. | Closeout §5.6, §9 item 6 |
| **5-15** | 5.3.1 | "At the freeze the database held exactly as many financial transactions as operational logs." | **S wording** | Re-anchor to the baseline census and give the number: **109 operational logs, 109 financial transactions, 0 unpaired**, `alembic_version` `b9e5f30c74a1`. Replace "at the freeze" with "at the baseline commit". | Closeout §2.8 |
| **5-16** | 5.3.2 | Drying-to-price chain: 100 kg @ 25% → 84 kg @ 13%; ₦35.00 → ₦41.67; 19%; ₦6.67/kg; 86.21 kg predicted | **OK — quote freely** | Keep every figure. The maize row was verified bit-identical across the seed change and its diff touches nothing there. These figures are load-bearing across Chapters 4 and 5. **Do not alter any division here without re-stating the whole chain.** | C-22 |
| **5-17** | 5.3.2 | (implicit) ₦41.67 is presented as *the* break-even/unit-cost figure | **Needs a distinction** | Distinguish the two bases now that the farm owns a depreciating asset: **`break_even_price_CASH` = ₦41.666666666666664** (unchanged) and **`break_even_price_TOTAL` = ₦42.36767852721509**, because maize takes ₦58.88 of the farm-wide overlay. Neither is in the JSON captures. Also keep break-even **yield** (kg, retrospective, deterministic tier) distinct from break-even **price** (₦/kg, dual, enterprise tier) throughout. | C-23, C-24 |
| **5-18** | 5.3.3 | Null-case discipline; 88.25% classified / 11.75% unclassified | **OK** | Keep. Both figures are baseline-valid. This is the strongest interpretive passage in the chapter. | Closeout §8 T8 |
| **5-19** | 5.3.4 | "A 243,724-byte payload takes 4.87 s to transfer at 400 Kbps" | **S** | → "**139,245 B over 8 requests**, which is 2.79 s at 400 Kbps and 0.68 s at 1,638.4 Kbps." (139,245 × 8 ÷ 400,000 = 2.785 s.) Route-level code-splitting removed **104,479 bytes** from the first load, a **43% reduction** against 17 August. | C-11, C-13 |
| **5-20** | 5.3.4 | "cold performance collapses from a score of 95 at 1.6 Mbps to 57 at 0.4 Mbps" | **S** | → "**99 at slow-4G to 65 at slow-3G**" — both from the 29 August set, same host, same session, so the comparison is legitimate. **Never compare a score or TBT across the 17 and 29 August sets**: the host benchmark index differed (425–1654 then, 1406–1996 now). | C-12 |
| **5-21** | 5.3.4 | "Nigerian median mobile throughput is far above that threshold" | **Unsupported** | No source and no measurement supports this. Either cite a figure in the reference list or delete the sentence. The argument that follows does not depend on it. | — |
| **5-22** | 5.3.4 | "first paint in 116 ms and main content in 1.6 s on a link that would otherwise take 7.7 s" | **S** | → warm FCP **70.6 ms**, warm LCP **1,612.0 ms**, against cold slow-3G FCP/LCP **5,661.2 ms**. | C-11 |
| **5-23** | 5.3.4 | "improves first paint by a factor of sixty-six" | **S — arithmetic** | 5,661.2 ÷ 70.6 = **80.2**. → "**by a factor of about eighty**". | computed from closeout §2.4 |
| **5-24** | 5.3.4 | "A stale-revalidation window nevertheless remains reasoned but unreproduced." | **OK** | Keep exactly this wording. Do **not** upgrade it to a defect and do **not** claim it is not one. | Closeout §9 item 16; must-not-claim 21 |
| **5-25** | 5.3 (new subsection) | — | **U — add** | **Add a new interpretive subsection: "A recorded defect that was not one."** The 25 August audit reported that per-crop decision support failed to net reversals and produced a phantom `Unspecified` cost. The finding was read out of code without being reproduced. It was false, it survived into three documents and the chapter text, and it was overturned only by executing the path at two separate commits. The methodological point — *a defect read out of code without being reproduced is not a defect* — is a genuine finding about the evaluation method and belongs in the thesis as one. **Do not quietly delete the passage; convert it.** | C-08; closeout §9 item 25 |
| **5-26** | 5.3.6 | Negative controls: "190 and 93%" | **S** | Re-source to 422/96%/148/43.18%. The argument is unaffected and remains one of the chapter's best. Re-attribute the mutation runs by commit: they were executed at `59a6286` against frontend cache logic the merge did not change — say so, or re-run them at `78a68c2`. | C-01, C-02; closeout §10 (4.4) |
| **5-27** | 5.4 | "the current implementation reports R² and MAE only, and this is recorded as a gap in Section 4.9" | **F** | **Delete.** RMSE is measured and recorded: **0.4883 t/ha** (0.488334). Chapter 3 §3.6.5's "may additionally be reported" becomes "is additionally reported". | C-10 |
| **5-28** | 5.4 | "That is the correct reading of the R² of 0.9762 … recovery of a constructed relationship" | **OK** | Keep verbatim. This is exactly the mandated disclosure, and it is better phrased here than anywhere else in the thesis. Add MAE 0.2414 t/ha and RMSE 0.4883 t/ha alongside. | Closeout §2.3 |
| **5-29** | 5.4 (end) | "Note for submission: several works cited in Chapter Two … do not yet carry full entries in the reference list." | **G** | **This note must not appear in the submitted document.** It is also understated: **12** cited works lack entries, not four. Complete the entries and delete the note. | Part 6 below |
| **5-30** | 5.5 "Scope and deployment" | "no TLS termination, no backup and recovery procedure, no secret management and no observability" | **F (three of four)** | Correct to: a Caddy edge profile is configured and renders, but **automatic certificate issuance has never run against a real hostname**; backup and restore **were executed with the project's own scripts** — a 28,164-byte dump, 8 tables with data, every row count matched on restore, `alembic_version` `b9e5f30c74a1`, 0 unpaired operational logs, live database untouched; the production compose **renders from `.env.example` alone**, with no `SECRET_KEY` literal committed and no tracked `.env`. **Only "no observability" survives** — no metrics, no tracing, no alerting, containers log to stdout only. | Closeout §2.7, §9 items 1, 2, 11 |
| **5-31** | 5.5 "Scope and deployment" | "every restart costs 8.6 s of unavailability" | **OK** | Keep. Measured 8.57 s, driven by the train-on-boot step. State it is an availability cost, not a memory cost. | Closeout §2.5 |
| **5-32** | 5.5 "The forecast tier" | "is not validated, and is not reproducible from the repository" | **F** | **Delete "not reproducible" and replace with the reproducibility evidence**: dataset `sha256 a461b884afc9fafda953ff90cc2f75eb0d8608f2e58ad9d206fc215d7b6ba5bf`, `seed=42`, fixed split seed, re-derived by regenerating and refitting rather than read from the sidecar, agreement to **six decimal places**, 18 reproducibility tests passing, cross-environment agreement across Python 3.14.5 and 3.11.15. The claim understates the project's own rigour. Keep every word of the synthetic-data disclosure. | C-09 |
| **5-33** | 5.5 "Correctness defects" | "Five are known… per-crop breakdown does not net reversals… Unbounded monetary fields, the absence of an equipment edit path…" | **F — three of five** | **Rewrite the paragraph.** Reversal netting works (C-08). Monetary fields **are** bounded — out-of-range values return 422 (closeout §2.7). Equipment **can** be corrected — `PATCH` returns 200 with `updated_at` stamped, and a no-op PATCH leaves `updated_at` unchanged so a non-correction is not recorded. **Two survive**: a mistaken reversal cannot itself be rolled back, only compensated by a new unlinked entry; and the stale-revalidation window remains reasoned but unreproduced. **Add two genuine ones**: `GET /bioprocess/summary` has a typed client method and zero callers; per-operation equipment attribution is captured but not costed. | C-08; closeout §2.7, §9 items 15, 16, 18, 19 |
| **5-34** | 5.5 "Verification boundaries" | "no independent security review, and no load, stress or soak testing" | **OK** | Keep. Add: rate-limit counters are **in-process** — they do not span replicas and do not survive a restart, **both observed**. Naming the residual is stronger than claiming the control. | Closeout §9 item 12 |
| **5-35** | 5.5 | (absent) CI | **U — add** | Add: **no CI run result is recorded for the baseline commit.** The workflow is defined; its jobs' substance was executed locally. **The phrase "CI is green" must not appear anywhere in the thesis.** | C-27; must-not-claim 15 |
| **5-36** | 5.6 | ₦6.67/kg, 19%, ₦105 at 200 farms | **OK** | Keep. Retain "reasoned, not measured" on the tenancy figures. | C-22; closeout §2.5 |
| **5-37** | 5.7.1 Tier A (a) | "Attribute a contra entry to its original's crop… the single most consequential correctness fix" | **F** | **Delete the item.** It is not a defect (C-08). | C-08 |
| **5-38** | 5.7.1 Tier A (b) | "Bound the monetary and quantity fields." | **F** | **Delete.** Bounds are implemented and verified live (422 on four out-of-range inputs). | Closeout §2.7 |
| **5-39** | 5.7.1 Tier A (c) | "Add an equipment update path." | **F** | **Delete.** `PATCH` exists, is verified, and 20 tests pin it. | Closeout §2.7 |
| **5-40** | 5.7.1 Tier A (d) | Two outstanding implementation citations | **Open** | **Keep.** Still open: an agricultural-economics or extension enterprise-budget source for the cost-behaviour taxonomy, and post-harvest handling guidance for the safe-storage moisture ceilings. See ADR 0002. | `docs/adr/0002` |
| **5-41** | 5.7.1 Tier A (e) | "Reconcile 'tamper-evident' to 'audit-trailed'" | **Done** | **Delete the first half.** Every occurrence already reads correctly ("not cryptographic tamper-evidence"; "tamper-proof" appears only in the Chapter 2 blockchain review, where it is correct). **Keep the second half** — the front matter still must be reconciled to the corrected figures. | verified in document |
| **5-42** | 5.7.1 Tier A (f) | Complete the missing reference entries | **Keep, restate** | **12** works, not "several". Enumerated in Part 6. Add that the list is **below the departmental minimum of 15** and below the 70%-recent requirement. | guideline §2.4 |
| **5-43** | 5.7.1 Tier A | (absent) | **Add** | New Tier A item: **re-source every figure in Chapters 4 and 5 to `78a68c2`** and restate both reproduction commands. This is now the largest single submission task. | C-26 |
| **5-44** | 5.7.1 Tier A | (absent) | **Add** | New Tier A item: **capture the interface figures.** The thesis contains **zero figures**; the List of Figures is a bracketed placeholder note. The capture plan is `docs/THESIS_CLOSEOUT_2026-08-30.md` §7. | guideline §2.3(b) |
| **5-45** | 5.7.2 Tier B (e) | "Re-run the performance audit against the frozen, code-split build" | **Done** | **Delete.** Executed 29 August 2026 at `78a68c2`, Lighthouse 13.4.1, 5 cold runs per condition plus 3 flow iterations, medians reported. | C-11 |
| **5-46** | 5.7.2 Tier B (a)–(d), (f) | Usability panel; component tests; E2E browser test; PostgreSQL concurrency; security review and load testing | **OK** | Keep all five. Every one maps to a live evidence gap. (a) remains the highest-value remaining piece of evidence in the project. | Closeout §9 items 3, 6, 7, 8, 10 |
| **5-47** | 5.7.3 Tier C (b) | "add RMSE alongside R² and MAE" | **Done** | **Delete the RMSE half.** **Keep the prediction-interval half** — the confidence band from the forest's tree spread is implemented but not reported prominently. | C-10 |
| **5-48** | 5.7.3 Tier C (c) | "Give the Olympic-average yield baseline an interface surface, and make the entry form's crop list follow the farm's own recorded crops" | **Done — both halves** | **Delete the item.** `YieldBaselinePanel` is rendered; `useCropOptions.ts` merges recorded-crop and predictor-crop sources at runtime and `FarmRecordCreateForm.tsx:79` consumes it. | C-15, C-16 |
| **5-49** | 5.7.3 Tier C (d) | "Capture intermediate drying readings through the interface" | **Done** | **Delete.** `DryingFields.tsx:79-137` provides repeatable optional readings rows, `dryingParams.ts` validates them client-side, and `DryingCurveChart.tsx` plots them. | C-18 |
| **5-50** | 5.7.3 Tier C (e) | Consume `equipment_id` and `hours_used` for cost-per-hour and utilisation | **Keep** | Still correct and still a genuine gap. Add the bound: `hours_used` is populated on **three of eight** seeded mechanisation logs, so any rate would be over an unknown fraction of use. **No machine-hour, utilisation or cost-per-hour figure may appear anywhere in the thesis.** | C-19; closeout §9 item 18 |
| **5-51** | 5.7.3 Tier C | (absent) | **Add** | New Tier C item: **give `GET /bioprocess/summary` a consumer.** The endpoint and its typed client method exist; `apiClient.ts:171` has zero callers. | C-20; closeout §9 item 19 |
| **5-52** | 5.7.3 Tier C (f), (g) | Feature-phone channel against a live gateway; execute the designed field evaluation | **OK** | Keep both. (f) must be reworded so it does not imply a partial implementation exists to extend — nothing exists. | Closeout §9 item 20 |
| **5-53** | 5.8 Conclusion | "verified by 190 passing backend tests at 93% statement coverage and 89 passing frontend tests" | **S** | → 422/418/4/0 at 96% (1,594/66); 148 in 13 files at 43.18%. | C-01…C-04 |
| **5-54** | 5.8 Conclusion | "reaching first paint sixty-six times faster warm than cold on a 0.4 Mbps link, though main content improves by a factor of about five" | **S — arithmetic** | FCP 5,661.2 ÷ 70.6 = **80.2**; LCP 5,661.2 ÷ 1,612.0 = **3.5**. → "about **eighty** times faster … main content improves by a factor of about **three and a half**, and that is the figure a user experiences." | computed from closeout §2.4 |
| **5-55** | 5.8 Conclusion | "the application transfers nothing on a repeat visit" | **F** | → "transfers **127 B over 7 requests** on a repeat visit — the manifest icon, absent from the precache, which is a measured defect reported in §4.10.4." | Closeout §9 item 17 |
| **5-56** | 5.8 Conclusion | "The per-crop breakdown is not reversal-correct." | **F** | **Delete.** | C-08 |
| **5-57** | 5.8 Conclusion | "frozen for evaluation at an identified commit" | **S** | Name it: `78a68c2`, 29 August 2026. **"Development stopped at that tag" is false and must not appear** — the hardening branch merged four days after the freeze tag. | C-26 |
| **5-58** | 5.8 Conclusion | "The system has never been deployed." | **OK, refine** | Keep, but refine: a production **path** exists and was built, started and probed — 3 services healthy, 7 of 7 live checks pass, both application containers non-root, the database publishes no host port. **No instance serves real users.** That is the accurate boundary and it is stronger than the flat negative. | Closeout §2.7, §9 item 1 |
| **5-59** | throughout | "the frozen tag" / "at the freeze" (14 occurrences document-wide) | **S** | Replace with "the baseline commit `78a68c2`" throughout Chapters 4 and 5, and in the two front-matter occurrences. | C-26 |
| **5-60** | 5.1.2 (new) | — | **G — add** | The guideline's 5.1 Summary requires a restatement of the problem and the procedures used. The existing §5.1 Introduction does neither. **Write 5.1.1 and 5.1.2** (see §1.3). | guideline |

### 1.3 The one genuinely new passage — draft text for 5.1.2 Summary of Findings

Everything else in Chapter Five is correction. This section does not exist and
the guideline requires it. **Every figure below is baseline-verified; nothing is
new evidence.**

> **5.1.2 Summary of findings**
>
> The evaluation returned findings in six areas.
>
> *Structural integrity of the record.* At the baseline commit the live database
> held 109 operational logs and 109 financial transactions, with zero unpaired
> operational logs. The one-to-one correspondence is not a property of the
> sample but the paired-write invariant made visible in the data, and it is the
> single most quotable structural result of the work.
>
> *Functional verification.* The backend suite collects 422 tests, of which 418
> pass, 4 are skipped (PostgreSQL-only migration tests, separately executed
> 12/12 against PostgreSQL 15.18) and none fail, at 96% statement coverage
> (1,594 statements, 66 missed). The frontend suite comprises 148 tests in 13
> files at 43.18% statement coverage (558 of 1,292), measured over the whole of
> `src` including page and form components that carry no tests. The two coverage
> figures must be read together. Three sets of negative-control runs establish
> that the tests fail when the behaviour they guard is broken.
>
> *Decision support.* The deterministic tier computes nine metrics from the
> farm's own ledger with no model and no external data, and all six enterprise
> endpoints are reachable in the interface. The decision-support and
> enterprise-economics services both stand at 100% statement coverage. The
> platform withholds a figure wherever its inputs do not support one, and
> 88.25% of recorded cost at farm level carries a cost subtype, with the
> residual 11.75% reported as unclassified rather than distributed into a
> plausible bucket.
>
> *Post-harvest coupling.* A maize harvest of 100 kg at 25% moisture, dried to
> 13% and weighed out at 84 kg against a dry-matter prediction of 86.21 kg,
> moved the unit cost of production from ₦35.00 to ₦41.67 per marketable
> kilogram — a 19% difference, being post-harvest mass reduction expressed in
> money.
>
> *Forecasting.* A 200-estimator Random Forest over 6,000 synthetic samples
> returned R² 0.9762, MAE 0.2414 t/ha and RMSE 0.4883 t/ha, reproducible to six
> decimal places across two Python versions from a dataset with a recorded
> SHA-256 fingerprint. The figure measures the recovery of a constructed
> relationship. It is evidence that the machine-learning pipeline is correctly
> implemented end to end; it is not evidence about Nigerian yields, and the
> model learns from no farm's records.
>
> *Operation under constraint.* Under simulated slow-3G throttling a cold load
> transfers 139,245 B over 8 requests and reaches first paint at 5,661.2 ms; a
> warm load transfers 127 B over 7 requests and reaches first paint at 70.6 ms.
> Two exercised containers consume 178.9–202.8 MiB, supporting an estimated
> $15.40 (approximately ₦20,950) per month and a reasoned ₦105 per farm per
> month at a two-hundred-farm tenancy.
>
> The usability strand of the specified evaluation was not executed. No System
> Usability Scale score, heuristic-severity rating, task-completion measurement
> or evaluator finding is reported anywhere in this work.

### 1.4 Chapter Five sections requiring no correction

For the avoidance of re-editing: §5.3.1 (paired write, once re-anchored),
§5.3.3 (null-case discipline), §5.3.5 (cost structure), §5.4's paragraphs on
fragmentation, interoperability, adoption conditioning, connectivity, the
modelling ladder and usability method, and §5.6 in full, are all sound at the
baseline. **§5.4's interoperability paragraph in particular should be preserved
verbatim** — conceding that the work addresses fragmentation and not
interoperability is exactly the kind of restraint an examiner rewards.

---

## PART 2 — Objective-to-conclusion matrix

Verdicts: **ACHIEVED** · **PARTIALLY ACHIEVED** · **NOT ACHIEVED** ·
**DEMONSTRATED AS PROTOTYPE**.

This matrix should become **Table 5.1** in the corrected chapter — Chapter Five
currently contains no table at all.

| Ch1 objective (§1.3) | Implementation status | Chapter 4 evidence | Chapter 5 conclusion |
|---|---|---|---|
| **(i)** Identify and evaluate the socio-technical barriers — data fragmentation, interoperability constraints and user complexity — hindering FMIS adoption in Nigeria | **Partial.** Barriers identified from the literature and carried into NFRs §3.3.2 as binding requirements. Four answered by implemented mechanisms: paired write (fragmentation), offline queue + service worker (connectivity), fixed-instance cost profile (cost), reduction to ranked satisficing figures (complexity). **NFR (d), the feature-phone channel, is not implemented in any form.** No primary study of Nigerian farmers was conducted. | §4.2 functional inventory; census 109/109/0 unpaired (T1); offline queue and idempotency tests within the 422; §4.10 performance; §4.11.4 cost per farm | **PARTIALLY ACHIEVED.** Achieved as identification and design response; **not** achieved as empirical evaluation. The barrier that is quantitatively largest — the 68% rural device gap — is addressed by a mechanism that was designed and not built, so the work reaches farmers who already hold a smartphone and an intermittent connection. State that as a limit on reach, not as inclusion. |
| **(ii)** Formulate a conceptual system architecture translating static operational and financial records into dynamic, actionable decision-support metrics for optimising mechanisation and input allocation | **Implemented, and beyond what Chapter 3 specifies.** Nine deterministic metrics plus a forecast tier; six enterprise endpoints, all reachable; `dss_service.py` and `enterprise_service.py` at 100% statement coverage; partial budget implemented twice and agreeing with an independent hand-computed fixture across eight cases. **One qualification stands: mechanisation attribution is captured but not costed.** | §4.6 (T6, T7), §4.7 (T8, T9), §4.8 (T10, T11), §4.9 (T12); 100% coverage on both services | **ACHIEVED, DEMONSTRATED AS PROTOTYPE.** The strongest objective in the thesis. Bound it three ways: demonstrated on one seeded five-crop farm, not a season of real records; the forecast tier trains on synthetic data and learns from no farm; and the objective's own words — "optimising farm mechanisation" — are **not** met, because `equipment_id` and `hours_used` are persisted and read by no service. No machine-hour, utilisation or cost-per-hour figure exists. |
| **(iii)** Design and integrate a secure data-sharing framework standardising yield and P&L reporting, as a verifiable analytical tool building operational trust among banks, investors and policymakers | **Implemented, and substantially understated by both Chapters 3 and 5.** Signed-token auth over bcrypt; farm scoping on every path with cross-farm reads returning 404; RBAC over 3 roles / 12 permissions with permission checked before scope; login throttling; share tokens hashed at rest, 90-day expiry, revocable, single identical 404 for unknown/revoked/expired, 401 on bearer use; raw token absent from all three logs; monetary input bounds; ledger deletion refused (405), correction by linked contra entry; CSV export of a standardised P&L. | **Currently unreported.** Requires the new §4.12 recommended by the closeout — the largest body of verified, unreported evidence in the project | **ACHIEVED as an implemented and internally verified mechanism.** Two bounds are non-negotiable. The boundary is proven by the project's own tests and live probes, **not** by any independent security assessment, penetration test or threat model. And "verifiable" must be read exactly: the ledger is **audit-trailed at the application layer**, not cryptographically tamper-evident — there is no hash chaining, no signing, no append-only log, and a party with database access is not constrained by it. The distributed-ledger mechanism reviewed in §2.5 remains the future extension Chapter One scoped it as. |
| **(iv)** Implement and empirically evaluate the platform's usability, cost-effectiveness and operational viability within Nigerian infrastructural constraints | **Three of four specified strands executed.** Functional verification: 422/418/4/0 at 96%, 148 in 13 files at 43.18%, with negative controls. Performance: Lighthouse 13.4.1 at the baseline, 5 cold runs per condition plus 3 flows, medians reported. Hosting cost: measured footprint 178.9–202.8 MiB → estimated $15.40 ≈ ₦20,950/month. **Usability: instruments prepared, study not run.** | §4.3 (T2, T3, T5), §4.4, §4.10 (T13), §4.11 (T14, T15); §4.12 usability reports no figure | **PARTIALLY ACHIEVED — and say so in exactly these words.** The outstanding strand is the consequential one: the platform's central claim is that it reduces cognitive load for a user operating under bounded rationality, and that is precisely the claim no executed strand touches. Each executed strand carries its own bound: performance is simulated Lantern throttling against localhost on one developer machine; cost is estimated and part-assumed, not incurred; tenancy figures are reasoned, not load-tested; and functional verification demonstrates only that the behaviours somebody thought to test behave as specified. |
| **Overall aim** — design, develop and evaluate a secure, integrated farm record and decision-support platform overcoming socio-technical adoption barriers | Built, frozen at `78a68c2`, verified across seven evidence strands; never deployed to serve real users; never placed in front of a farmer | Chapter 4 in full | **DEMONSTRATED AS PROTOTYPE.** A verified prototype: an architecture in which operational and financial records cannot drift apart, a decision-support layer that is arithmetically correct and honest about the limits of its inputs, and a demonstration that post-harvest process measurements can be carried through to a pricing decision automatically. Whether that architecture changes what a Nigerian farmer earns is the question this work makes answerable and does not answer. |

**Traceability rule for the chapter.** Every sentence in §5.2 that asserts an
outcome must name the Chapter 4 section that carries its evidence. Where no
Chapter 4 section carries it, the sentence must be deleted or restated as a
design intention.

---

## PART 3 — Cross-chapter inconsistency register

Chain audited: PROBLEM → OBJECTIVES → METHODOLOGY → DESIGN → IMPLEMENTATION →
RESULTS → CONCLUSION.

### 3.1 Broken chains, by objective

| Objective | Ch1 stated? | Ch3 addressed? | Ch4 evidence? | Ch5 discussed? | Chain status |
|---|---|---|---|---|---|
| (i) Barriers | **Yes**, §1.3 | **Yes**, but §3.6.8 describes a USSD/SMS channel **in the present tense that does not exist**, and NFR §3.3.2(d) asserts feature-phone access as a met requirement | **Partial** — Table 4.26 row 1 concedes the channel is absent | **Yes**, §5.2.1 concedes it | **BROKEN AT CH3.** Chapters 4 and 5 concede what Chapter 3 asserts. An examiner reading in order meets the overclaim first. |
| (ii) Decision-support architecture | **Yes**, §1.3 | **Yes, but understated** — §3.6.5 names two metrics of nine; **no module for post-harvest drying**; **no module for enterprise economics**; Table 3.1 omits `ShareToken`, `crop`, `reverses_id`, `client_id`; §3.6.2 omits ledger immutability and the contra-entry model | **Yes**, §4.6–§4.9 report all nine plus drying and enterprise economics | **Yes**, §5.2.2 | **BROKEN AT CH3.** Chapter 4 reports results for two subsystems (§4.7, §4.8) that the methodology never specifies, and Chapter 5 calls one of them "the engineering contribution". Chapter 4's per-crop, reversal and idempotency analyses all depend on columns Chapter 3 never introduces. |
| (iii) Secure data sharing | **Yes**, §1.3 | **Understated** — §3.6.6 and §3.7 describe authentication with **no authorisation model**; no RBAC, no throttling, no input bounds, no token expiry, no log scrubbing | **Absent** — Chapter 4 has **no section reporting any of this** | **Understated**, §5.2.3 | **BROKEN AT CH3 AND CH4.** The objective is met by the implementation and reported by neither chapter. Closing it requires §3.7 expansion **and** the new §4.12. |
| (iv) Empirical evaluation | **Yes**, §1.3 | **Overclaims** — §3.8.4 presents the usability evaluation among "the evaluation actually undertaken"; it was not undertaken | **Honest** — §4.12 reports no figure; Table 4.26 says partially met | **Honest**, §5.2.4 and §5.5 | **BROKEN AT CH3.** Chapters 4 and 5 are correct; Chapter 3 is not. Move §3.8.4 to §3.8.5 as designed work, or state explicitly in place that the instruments were prepared and the study was not run. |

### 3.2 Content inconsistencies between chapters

| # | Chapters | Inconsistency | Required resolution |
|---|---|---|---|
| X-01 | 3 ↔ 4 ↔ 5 | §3.6.4 calls per-machine equipment association "a future refinement". Ch4 Table 4.2 row 13 says it is captured but not consumed. Ch5 §5.7.3(e) says the data model already stores it. | Single wording everywhere: **captured but not costed** — `equipment_id` and `hours_used` are validated, persisted and read back, and read by no service. No cost-per-hour, utilisation or machine-rate figure is produced anywhere. |
| X-02 | 3 ↔ 4 | §3.6.1 calls runtime caching of read endpoints "a planned enhancement". It is built: `StaleWhileRevalidate` over `ledger`, `reports` and five named `dss` reads, 64 entries / 7 days, purged on write and on auth change, with `/dss/model` and `/dss/predict` deliberately excluded. | Rewrite §3.6.1 as built. State the exclusions and the purge-on-write design; the tenant-driven exclusion is a design result worth a sentence. |
| X-03 | 1 ↔ 3 ↔ 5 | Ch1 §1.5 says offline capability is implemented "primarily for the data-entry (write) path". §3.3.2(b) claims offline data capture generally. Ch5 §5.4 says the write path and shell are local. | Ch1 is the accurate one. Align §3.3.2(b) to it: offline **writes** cover the record-creation path only, and offline **reads** are served by the service worker for the named routes. **"All writes work offline" must not appear.** |
| X-04 | 3 ↔ 4 ↔ 5 | §3.6.3 promises "standardised, exportable reports". Only CSV exists; there is no PDF export. | Say **CSV** in all three chapters. |
| X-05 | 3 ↔ 5 | §3.6.5 says RMSE "may additionally be reported". Ch5 §5.4 says it is not reported and records that as a gap. It **is** measured: 0.4883 t/ha. | §3.6.5 → "is additionally reported". Delete the Ch5 gap sentence and the Tier C(b) RMSE half. Add to §4.9 and to the abstract. |
| X-06 | 3 ↔ 5 | §3.6.7 describes the share token as revocable but not as expiring, hashed at rest, or resolving unknown/revoked/expired to one identical 404. Ch5 §5.2.3 mentions hashing only. | Add expiry, hashing at rest and the single-404 design to §3.6.7, and carry all three into §5.2.3. |
| X-07 | 2 ↔ 5 | Ch2 §2.5 reviews distributed-ledger governance; Ch5 §5.2.3 and §5.4 correctly position the implementation as the weaker deployable alternative. | **No inconsistency.** Preserve this passage verbatim — it is one of the best-calibrated arguments in the thesis. |
| X-08 | front ↔ 4 ↔ 5 | The abstract carries 190 / 93% / 89 and 7,679.9 ms → 116.4 ms → 1,613.8 ms — all superseded. | Re-source the abstract from the baseline. See Part 5 rows N-01…N-27. |
| X-09 | 4 ↔ 5 | Ch4 §4.14 lists five application defects; three are closed (reversal netting, monetary bounds, equipment edit). Ch5 §5.5 restates all five. | Correct **Ch4 §4.14 first**, then Ch5 §5.5 follows. Correcting Ch5 alone creates a new contradiction. |
| X-10 | 1 ↔ 5 | Ch1 §1.5 scopes DSS as "deterministic, rule-based modelling complemented by lightweight statistical regression". The implementation is a 200-estimator Random Forest. | A Random Forest is an ensemble of regression trees, not "lightweight statistical regression". Either widen §1.5 to "lightweight tree-ensemble regression" or state in §5.4 that the implementation went one step up the modelling ladder from the scoped method, and why (van Klompenburg et al., 2020). **The second is preferable — it is a defensible design decision, not a drift.** |
| X-11 | 3 ↔ 4 ↔ 5 | Ch3 §3.4/§3.5 describe the architecture and data model; there is **no architecture diagram and no entity-relationship diagram anywhere in the thesis**. | See Part 7.2. For a B.Tech engineering project this is the single most visible structural gap in the document. |
| X-12 | 4 ↔ 5 | Ch4 reports the demonstration farm as five crops while every per-crop table is captioned "farm 26" and the JSON captures under `docs/ch4-data/` are three-crop. | Re-capture the per-crop tables against the five-crop farm. **No farm-wide total may be quoted from `docs/ch4-data/dss_per_crop.json`.** Per-crop rows did not move; farm-wide totals did. |

---

## PART 4 — Terminology consistency

**Overall finding: terminology is in good shape.** "AGRI-PROFIT" is used
uniformly across all 38 occurrences with no `AgriProfit` / `Agri-Profit`
variant anywhere in the document. Seven issues remain.

| # | Term | Current usage | Recommendation |
|---|---|---|---|
| T-01 | System noun | "the platform" ×68, "the application" ×20, "the system" ×8, "prototype" ×3 | **Adopt "the platform"** as the default noun for the whole artefact. Reserve **"the application"** for the client specifically (bundle, service worker, shell) — Ch5 §5.3.4 already does this correctly. Reserve **"the system"** for the deployed three-container stack. Use **"prototype"** only in Chapter 5's conclusion, where it is a deliberate calibration of the contribution, not a synonym. |
| T-02 | Drying subsystem | Ch1 and Ch3 say "bioprocess" (×4); Ch4 and Ch5 say "post-harvest drying" (×11) | **Use "post-harvest drying module"** for the implemented subsystem. Reserve **"bioprocess"** for the Ch1/Ch2 conceptual framing. The code namespace (`bioprocess_service.py`, `/bioprocess/*`) may keep its name; say so once in Chapter 3 so an examiner reading the appendix is not confused. |
| T-03 | Baseline | "the frozen tag" / "at the freeze" / "the frozen build" ×14 | **Replace all with "the baseline commit `78a68c2`"** (first use in each chapter spelled in full, thereafter "the baseline"). The freeze *tag* names a superseded commit and the phrase carries the false implication that development stopped there. |
| T-04 | Break-even | Break-even **yield** (kg, retrospective, deterministic tier) and break-even **price** (₦/kg, dual cash/total, enterprise tier) are distinct outputs from distinct endpoints | **Always qualify with "yield" or "price"** — never bare "break-even". They come from different tiers and mean different things. |
| T-05 | Records | "operational record" ×5, "operational log" ×11, "farm record" ×9, "financial record" ×10, "financial transaction" ×10 | Use the **entity names — Operational Log, Financial Transaction —** when referring to rows and to the paired-write invariant, and the **generic nouns** only in Chapters 1 and 2 where the discussion is about practice rather than about the data model. Chapter 5 currently mixes both within single paragraphs. |
| T-06 | Forecast vs prediction | "forecast" ×21, "predict*" ×34 | **"Forecast tier"** for the subsystem; **"prediction"** for a single output and for the confidence band. Chapter 2 legitimately uses "prediction" throughout because the literature does. |
| T-07 | Trust | "tamper-proof" (Ch2, blockchain review), "tamper-evidence" (Ch4/Ch5, negated), "audit-trailed" | **No change needed.** Every occurrence is already correct: "tamper-proof" appears only in the Chapter 2 review of what blockchain provides; every reference to AGRI-PROFIT's own ledger already says "audit-trailed" or explicitly negates cryptographic tamper-evidence. Chapter 5 §5.7.1(e) proposes a fix that is already done — delete that half of the item. |

---

## PART 5 — Numerical consistency register

**Correct value** is the closeout baseline (§2) unless the row says otherwise.

### 5.1 Test and coverage figures

| Metric | Locations found | Correct value | Corrections required |
|---|---|---|---|
| **N-01** Backend tests | Abstract; Ch4 ×4 (§4.3.1, Table 4.3, §4.13, §4.15); Ch5 ×3 (§5.2.4, §5.3.6, §5.8) — all read **190** | **422 collected, 418 passed, 4 skipped, 0 failed** | Replace all 8. State the 4 skips are PostgreSQL-only migration tests, separately executed **12/12 against PostgreSQL 15.18**. Quote *collected* counts and say so — `grep -c "^def test_"` yields 355 and undercounts six parameterising modules. |
| **N-02** Backend coverage | Abstract; Ch4 ×7; Ch5 ×3 — all read **93%** | **96%** | Replace all 11. |
| **N-03** Statements / missed | Ch4 ×4 — **1,286 / 91** | **1,594 / 66** | Replace. Both are statement coverage; `--cov-branch` is enabled nowhere in the repository, so **never call it branch coverage**. |
| **N-04** Frontend tests | Abstract; Ch4 ×6; Ch5 ×2 — **89** | **148** | Replace all 9. |
| **N-05** Frontend test files | Ch4 ×2 — **9 files** | **13 files** | Replace. |
| **N-06** Frontend coverage | Ch4 ×2 — **33.48% (378 / 1,129)** | **43.18% (558 / 1,292)**; branch 32.41% (318/981), function 36.16% (149/412), line 43.00% (492/1,144) | Replace. **The backend and frontend coverage figures must be quoted together or not at all** — 96% alone misrepresents the system. State the denominator is the whole of `src`. |
| **N-07** Reconciliation (Table 4.7) | Ch4 §4.3.4 — reconciles 185→190 and 82→89 | **190 → 422** and **89 → 148** | **Rewrite the table entirely.** Cause: nine backend and four frontend test modules added by the merge. Argument: **the four pre-existing backend modules still collect exactly 190**, so the increase is entirely additive and nothing was weakened. |
| **N-08** Module coverage list | Ch4 Table 4.4 — `dss.py` 93%, three modules under 80% | `dss.py` **90%**; **one** module under 80% (`ml/train.py` 47%); `ml/dataset.py` rose 36%→82%; `models/database.py` unchanged at 64% | Re-source from the 29 Aug output. Ten modules sit below 100%. |
| **N-09** Timing robustness | Absent everywhere | `dashboardAccess.test.tsx` exceeds Vitest's 5,000 ms default in a full run, passes in ~3 s alone; **observed on two separate days** | **Add** to Ch4 §4.3 and Ch5. Quote as "148 tests, one of which is not timing-robust in a full-suite run". A harness limitation, not an application defect. |

### 5.2 ML figures

| Metric | Locations found | Correct value | Corrections required |
|---|---|---|---|
| **N-10** R² | Ch4 §4.9 ×2; Ch5 §5.4 — **0.9762** | **0.9762** (0.976204) | **Correct — keep.** Retain the in-distribution disclosure verbatim in both places. |
| **N-11** MAE | Ch4 §4.9 — **0.2414** | **0.2414 t/ha** (0.241393) | Correct — keep. Add units. |
| **N-12** RMSE | Ch4 §4.9 — **`[PLACEHOLDER]`**; Ch3 §3.6.5 "may additionally be reported"; Ch5 §5.4 says not reported | **0.4883 t/ha** (0.488334, tolerance ±0.0005) | Fill the placeholder. Change §3.6.5 to "is additionally reported". Delete the Ch5 gap sentence and the Tier C(b) RMSE half. Add to the abstract. |
| **N-13** Reproducibility | Ch4 §4.9 and Ch5 §5.5 both say **"not reproducible from the repository"** | **Fully reproducible** — `seed=42`, fixed split seed, dataset `sha256 a461b884afc9fafda953ff90cc2f75eb0d8608f2e58ad9d206fc215d7b6ba5bf`, re-derived by regeneration and refit, agreement to **six decimal places**, 18 tests, cross-environment across Python 3.14.5 / 3.11.15 | **Delete both claims** and replace with the evidence. |
| **N-14** Dataset | Ch4 §4.9 | **6,000 synthetic samples**, `test_size=0.2`, `split_random_state=42`, `Pipeline(OneHotEncoder + RandomForestRegressor)`, `n_estimators=200`, `random_state=42`, **zero real farmer records** | Verify all present. The zero-real-records disclosure is mandatory. |

### 5.3 Performance figures

| Metric | Locations found | Correct value | Corrections required |
|---|---|---|---|
| **N-15** Cold transfer | Ch4 ×5, Ch5 §5.3.4 — **243,724 B** (and **243,534 B** in `hostingcostanalysis.md` §4) | **139,245 B over 8 requests**, every run | Replace all 6 plus the cost-analysis file. Entry chunk 400.07 KB raw / 130.03 KB gzipped; charting code 262.12 KB / 82.07 KB gzip, loaded separately. The bandwidth **conclusion** is unaffected — egress remains immaterial. |
| **N-16** Cold slow-3G FCP/LCP | Abstract **7,679.9 ms**; Ch5 §5.3.4 **7.7 s** | **5,661.2 ms** (median of 5); LCP 5,661.2, SI 5,661.2, TBT 10.5, TTI 5,727.6, CLS 0, score 65 | Replace. |
| **N-17** Warm FCP | Abstract and Ch4 ×3, Ch5 ×1 — **116.4 ms** | **70.6 ms** (median of 3 flows) | Replace all 5. |
| **N-18** Warm LCP | Abstract — **1,613.8 ms** | **1,612.0 ms** | Replace. Note it was never network-bound, which is why it barely moved. |
| **N-19** Warm transfer | Ch4 and Ch5 — "transfers nothing at all" | **127 B over 7 requests** | Replace. The 127 B is `pwa-192x192.png`, the manifest icon, absent from the Workbox precache — the §4.10.4 defect, now confirmed **by measurement** rather than by reading the precache listing. |
| **N-20** Transfer time at 400 Kbps | Ch5 §5.3.4 — **4.87 s** | **2.79 s** (139,245 × 8 ÷ 400,000 = 2.785); 0.68 s at 1,638.4 Kbps | Replace, or recompute if the payload changes again. |
| **N-21** Warm-vs-cold FCP ratio | Ch4 ×3, Ch5 ×2 — **"sixty-six"** | **80.2** (5,661.2 ÷ 70.6) → "about eighty" | Replace all 5. |
| **N-22** Warm-vs-cold LCP ratio | Ch5 §5.8 — "a factor of about five" | **3.5** (5,661.2 ÷ 1,612.0) → "about three and a half" | Replace. |
| **N-23** Lighthouse scores | Ch4 and Ch5 — **95 at 1.6 Mbps, 57 at 0.4 Mbps** | **99 slow-4G, 65 slow-3G**, both from the 29 Aug set | Replace. **Never compare a score or TBT across the 17 and 29 August sets** — host benchmark index 425–1654 then, 1406–1996 now. This specifically rules out reading the cold slow-3G TBT movement (121.0 → 10.5 ms) as a code effect. |
| **N-24** Precache | Ch4 §4.10.3 — "21 entries totalling 859.67 KiB" | Not re-measured at the baseline | **Either re-measure or attribute explicitly to `59a6286`.** Do not quote it as a baseline figure. |
| **N-25** Method | Ch4 §4.10.1 | Lighthouse **13.4.1**, headless Chrome, `http://localhost:4173/` (`vite preview` on the production build, service worker active), mobile 412 × 823 @ DPR 1.75, **simulated (Lantern)** throttling with constant 4× CPU, slow-3G 400 ms / 400 Kbps, slow-4G 150 ms / 1638.4 Kbps, 5 cold CLI runs per condition plus 3 flow iterations, **medians** reported | State the method fully. Chapter 3 §3.8.2 says "network throttling applied to approximate a slow mobile connection" — true, but it must name the method: this is **a model of a degraded network, not a measurement of one**. |
| **N-26** Comparable movement | Ch4 §4.10.3 — "likely favourable" hedge | Cold transfer 243,724 → **139,245 B (−43%)**; cold slow-3G FCP 7,674.4 → **5,661.2 ms (−26%)**; cold slow-4G FCP 2,317.7 → **1,709.9 ms (−26%)**; warm FCP 116.4 → **70.6 ms**; warm LCP 1,613.8 → **1,612.0 ms** (unchanged). Code-splitting removed **104,479 bytes** from first load. | **Replace the hedge with the measurements.** |

### 5.4 Cost figures

| Metric | Locations found | Correct value | Corrections required |
|---|---|---|---|
| **N-27** Monthly cost | Abstract; Ch4 ×3; Ch5 ×3 — **$15.40 / ₦20,950** | **$15.40 ≈ ₦20,950** — instance $12.00 (₦16,327) + snapshot backups $2.40 (₦3,265) + domain $1.00 (₦1,361) + TLS $0.00 | **Correct — keep.** Add the conversion basis: **CBN ₦1,360.58 = US$1 as at 12 August 2026**; parallel market ₦1,425 on 13 Aug 2026, so naira figures are indicative rather than exact. Reference instance: 2 GB RAM / 50 GB SSD commodity tier. |
| **N-28** Footprint | Ch4 §4.11.1; Ch5 §5.2.4 — **178.9–202.8 MiB** | **178.9–202.8 MiB** — backend 145.5–161.5, PostgreSQL 33.4–41.3, across two container instances differing by ~11% | **Correct — keep.** Add: the static PWA server and the OS/container runtime were **not** measured, so the total is **part-measured and part-assumed**; and 145.5 MiB is a **lower bound** on the startup peak, not the peak, because the widest sampling gap (4.11 s across seven single-shot samples over a 14.2 s window at a mean 2.37 s interval) falls across the steepest part of the climb. |
| **N-29** Cost per farm | Ch4 §4.11.4; Ch5 ×4 — ₦419 / ₦210 / ₦105 | **₦419 at 50 · ₦210 at 100 · ₦105 at 200 · ₦42 at 500** | Correct — keep. **Always carry "reasoned, not load-tested".** |
| **N-30** Startup | Ch4 §4.11; Ch5 §5.5 — **8.6 s** | **8.57 s** from restart to accepting traffic, driven by the train-on-boot step | Correct — keep. State it is an availability cost, not a memory cost. |
| **N-31** Pricing placeholder | Ch4 §4.11 — **`[CONFIRM — re-check provider pricing pages]`** | Unresolved | **Must be resolved or the retrieval date restated before submission.** No provider was contacted and no quotation obtained; prices are list prices captured on a single date, exclusive of tax and committed-use discount. |

### 5.5 Ledger, DSS and demonstration-data figures

| Metric | Locations found | Correct value | Corrections required |
|---|---|---|---|
| **N-32** Census | Ch4 §4.2.1; Ch5 §5.2.1 — **109 / 109** | farms **14** · users **13** · operational_logs **109** · financial_transactions **109** · equipment **3** · maintenance_logs **1** · share_tokens **10** · `alembic_version` **`b9e5f30c74a1`** · **unpaired operational logs 0** | Correct — keep, and quote the full census as T1. The 109 / 109 / 0 correspondence is the single most quotable structural result in the thesis. |
| **N-33** Maize row | Abstract; Ch4 ×6; Ch5 ×3 — ₦45,000 rev / ₦3,500 exp / GM ₦41,500 / 100 kg / 84 kg marketable / **₦35.00** harvested / **₦41.67** marketable / break-even **7.78 kg** | **All unchanged and VALID — quote freely** | No change. Verified bit-identical across the seed change. **Load-bearing across Chapters 4 and 5 — do not alter any division here without re-stating the whole chain.** |
| **N-34** Maize break-even price | Ch4 Table 4.15 — **₦41.666666666666664** | **CASH ₦41.666666666666664** (unchanged); **TOTAL ₦42.36767852721509** | **Report both, distinguished.** The farm now owns a depreciating asset and maize takes ₦58.88 of the farm-wide overlay. Neither figure is in the JSON captures — re-capture live. |
| **N-35** Demo crop set | Ch4 (three-crop captures under `docs/ch4-data/`) vs "five crops" in the Ch4 text | **Five crops** — cassava 6, cowpea 11, maize 2, sorghum 4, tomato 5 = **28 logs**; two equipment records, one rated and one unrated | Re-capture every per-crop table. **No farm-wide total may be quoted from `docs/ch4-data/dss_per_crop.json`** — it is a three-crop capture of a five-crop farm. Per-crop rows did not move; farm-wide totals did. |
| **N-36** Classification coverage | Ch4 §4.7.1; Ch5 §5.3.3 — **88.25% / 11.75%** | **11.75% unclassified at farm level; maize 100% classified** | Correct — keep. |
| **N-37** Drying run | Ch4 §4.8.2; Ch5 §5.3.2 — 100 kg @ 25% wb → 84 kg @ 13% wb; dry matter 75.0 kg; predicted **86.21 kg** | Unchanged | Correct — keep. The denominator is the mass **weighed out** (84 kg), not the dry-matter prediction (86.21 kg) — the conservative choice, and the sentence explaining why must survive editing. |
| **N-38** Baseline identity | Ch4 §4.1 — tag `thesis-evidence-freeze-2026-08-25`, commit **`59a6286`**, "development stopped at that tag" | **`78a68c292205acdcac1a52f977fbea31b6e8495e`** on `main`, 29 Aug 2026 | **Rewrite §4.1.** Both reproduction commands must be restated. **"Development stopped at that tag" is false** — the hardening branch merged four days later. Correct all 14 "frozen tag" occurrences. |
| **N-39** Endpoint module naming | `THESIS_REPORTING_STATE.md` §6 lists a `share` module | There is no `share.py`. The module is **`backend/app/api/endpoints/investor.py`**; `share_service.py` is the service behind it | Correct wherever the module list appears. |
| **N-40** CI | Risked in drafts | **No CI run result was retrievable for `78a68c2`** and none is recorded in the repository | **"CI is green" must never be written.** Cite the jobs' substance as executed locally. |

---

## PART 6 — Citations and references

### 6.1 The reference list is materially incomplete

**21 distinct works are cited in text. The reference list carries 9 entries.**
Chapter 5's own closing note says "several works … including Poppe et al.,
Tummers et al., Jaiyeola and Gebresenbet et al." — the true figure is **12**.

**Present (9):** Brooke (1996) · Carrer, de Souza Filho & Batalha (2017) ·
Fountas et al. (2015) · Huang (2020) · Mhlanga (2023) · Nielsen (1994) ·
Nielsen & Molich (1990) · Olisah et al. (2024) · van Klompenburg, Kassahun &
Catal (2020).

**Missing (12), with in-text frequency:**

| Missing work | In-text citations | First appears |
|---|---|---|
| **Poppe, Vrolijk & Bosloper (2023)** | 6 | Ch1 §1.2 |
| **Jaiyeola (2023)** | 5 | Ch1 §1.1 |
| **Tummers, Kassahun & Tekinerdogan (2019)** | 5 | Ch1 §1.1 |
| **Gebresenbet et al. (2023)** | 4 | Ch1 §1.2 |
| **Nirosha (2024)** | 4 | Ch1 §1.1 |
| **Basir, Buckmaster, Raturi & Zhang (2024)** | 4 | Ch1 §1.1 |
| **Abbasi, Martinez & Ahmad (2022)** | 3 | Ch1 §1.1 |
| **Dayioglu & Turker (2021)** | 2 | Ch1 §1.1 |
| **Abiri, Rizan, Balasundram, Shahbazi & Abdul-Hamid (2023)** | 2 | Ch1 §1.1 |
| **Javaid, Haleem, Singh & Suman (2022)** | 1 | Ch1 §1.1 |
| **Giua, Materia & Camanzi (2020)** | 1 | Ch1 §1.2 |
| **Husemann & Novkovic (2012)** | 1 | Ch1 §1.4 |

Every reference in the list **is** cited, so there are no orphan entries.
Citation style is consistently APA 7 in text (`Author, Year`, `et al.` from the
first citation of a 3+ author work), and the nine present entries follow APA 7
in the list. **The defect is entirely one of completeness.**

### 6.2 Departmental minimums — currently not met

| Requirement (guideline §2.4) | Current | Gap |
|---|---|---|
| ≥ **15** references for an implementation-based project | **9** listed | **6 short of the minimum**; entering all 21 cited works clears it |
| **70%** of the list within the last five years (2021–2026) | Of the 21 cited works, **11 are 2021 or later** = **52%** | **Not met.** The 10 pre-2021 works (Brooke 1996, Nielsen 1994, Nielsen & Molich 1990, Husemann & Novkovic 2012, Fountas et al. 2015, Carrer et al. 2017, Tummers et al. 2019, Giua et al. 2020, Huang 2020, van Klompenburg et al. 2020) are methodologically necessary and should not be dropped. Holding those 10, reaching 70% requires **24 post-2021 entries** — a 34-entry list, i.e. **adding roughly 13 recent sources**. (23 recent of 33 is 69.7% and fails; 24 of 34 is 70.6% and passes.) |

**Where the additional recent sources should come from, given the thesis's own
argument:** post-harvest drying kinetics and safe-storage moisture thresholds
(also closes Tier A(d) and ADR 0002's second open citation); enterprise-budget
and cost-behaviour classification in agricultural economics (closes ADR 0002's
first); Nigerian mobile-network and smartphone-penetration data post-2021
(supports §5.3.4 and closes correction 5-21); progressive web applications and
offline-first design in low-connectivity contexts; and recent FMIS adoption
studies in Sub-Saharan Africa.

---

## PART 7 — Table and figure register

### 7.1 Tables — numbering is clean; referencing is not

**Numbering audit: PASS.** 27 tables — Table 3.1, then Table 4.1 through Table
4.26 — sequential, no duplicates, no gaps, all Arabic and chapter-conformant,
all captions above the table and un-bold as the guideline requires, all table
content 10 pt and centred.

**Referencing audit: FAIL.** The guideline states "The text should include
useful reference to all tables." Only **5 of 27** are referenced in body text
(Table 3.1, Table 4.4, Table 4.6, Table 4.11, Table 4.20 ×2). **22 tables are
never mentioned in prose.**

| Table/Figure | Problem | Required action | Priority |
|---|---|---|---|
| Tables 4.1, 4.2, 4.3, 4.5, 4.7–4.10, 4.12–4.19, 4.21–4.26 (22) | Never referenced in body text; guideline §2.3(a)(iv) breach | Add one in-text reference each ("Table 4.n presents…"). Mechanical, ~1 hour | **MUST FIX** |
| Table 4.2 rows 11, 12 | Assert the Olympic yield baseline is unreachable and that cowpea/tomato cannot be entered. **Both false at the baseline** | Delete both rows or restate as reachable | **MUST FIX** |
| Table 4.2 row 13 | Equipment attribution "captured, not consumed" | **Keep — verified true.** Restate as "captured but not costed" for consistency with X-01 | **MUST FIX (wording)** |
| Table 4.2 | Omits authorisation, throttling, share-token expiry, input bounds and equipment correction | Add five rows | **MUST FIX** |
| Table 4.3 "Verification results at the frozen tag" | Caption and every figure superseded | Re-caption to the baseline commit; re-source to 422/418/4/0, 96%, 1,594/66, 148/13, 43.18% | **MUST FIX** |
| Table 4.4 | Module coverage superseded (`dss.py` 93%→90%; three modules <80% → one) | Re-source from the 29 Aug output; ten modules sit below 100% | **MUST FIX** |
| Table 4.5 "Frontend test files at the freeze" | 9 files; now 13 | Re-source and re-caption | **MUST FIX** |
| Table 4.7 | Reconciles two superseded states against each other | **Rewrite entirely** as 190→422 / 89→148 with the additive-only argument | **MUST FIX** |
| Tables 4.8, 4.9 | Negative controls and the driven-browser probe were executed at `59a6286` / `c16924e` | Re-run at the baseline, **or** state the commit and date in the caption and note the merge did not change the frontend cache logic | **MUST FIX** |
| Tables 4.10–4.16 (all captioned "farm 26") | Captured against a three-crop farm; the farm now holds five crops. Table 4.15 carries only the CASH break-even price | Re-capture live against the five-crop farm; Table 4.15 must show CASH **and** TOTAL | **MUST FIX** |
| Table 4.19 | RMSE row is `[PLACEHOLDER]`; the reproducibility note is false | Fill **0.4883 t/ha**; replace the reproducibility qualification with the fingerprint and six-decimal agreement | **MUST FIX** |
| Table 4.20 | 17 August Lighthouse set at `c16924e` | **Replace wholesale** with the 29 August set; add a benchmark-index column so the non-comparability across dates is visible | **MUST FIX** |
| Tables 4.24, 4.25 | "to be completed" — usability instruments with no data | **Keep as they are.** The honest empty table is correct and is drafted to receive real data. Do not populate, do not delete | **Keep** |
| Table 4.26 | Objective rows carry 190/93%/89 and the reversal defect | Re-source; Objective 3 row gains the new §4.12; Objective 4 row must read **partly met** | **MUST FIX** |
| **New Table 4.x** (×2) | Security/authorisation verification and deployment/recovery verification are unreported | Add per closeout T18 and T19 | **MUST FIX** |
| **Table 5.1** | **Chapter Five contains no table at all** | Add the objective-to-conclusion matrix (Part 2) as Table 5.1, and update the List of Tables | **MUST FIX** |
| **All figures** | **The thesis contains zero figures.** The List of Figures is a bracketed editorial note: "[NO FIGURES ARE PRESENT IN EITHER SOURCE DOCUMENT…]" | **That bracketed note must not survive to submission.** See below | **MUST FIX — highest** |

### 7.2 Figures — the largest structural gap in the document

The guideline requires figures numbered per chapter with captions **below** and
centred, and requires a List of Figures. There are none. For a B.Tech
engineering project the following are effectively expected:

| Required figure | Chapter | Why | Priority |
|---|---|---|---|
| **Figure 3.1** System architecture | §3.4.1 | §3.4.1 is titled "Overall Architecture" and describes a three-container client–server stack in prose alone | **MUST FIX** |
| **Figure 3.2** Entity-relationship diagram | §3.5 | Table 3.1 lists entities in text; there is no relationship diagram, and Table 3.1 is itself incomplete (omits `ShareToken`, `crop`, `reverses_id`, `client_id`, `extra_data`, `role`) | **MUST FIX** |
| **Figure 3.3** Paired-write sequence | §3.6.2 | The paired write is the thesis's central design claim and its structural contribution; a sequence diagram makes it inspectable at a glance | **MUST FIX** |
| **Figures 4.x** Interface screenshots | §4.5.1 | §4.5.1 explicitly reserves a place for them. The full capture plan — preparation, shot list, quality rules, clean-up, and which states cannot be captured — is `docs/THESIS_CLOSEOUT_2026-08-30.md` §7 | **MUST FIX** |
| **Figure 4.x** Drying curve | §4.8 | The Page/Newton fit is "the engineering contribution" per §5.3.2 and is currently reported only as numbers. `DryingCurveChart.tsx` renders it and the readings input now exists, so it is capturable | **FIX IF TIME** |
| **Figure 4.x** Cold vs warm performance | §4.10 | Makes the 80× first-paint result legible | **FIX IF TIME** |

**Capture warnings from the closeout, which apply to every screenshot:** the
seed script is idempotent, so re-running it is safe; the demonstration farm is
"Demo Farm" (`demo-bioprocess-v2@test.example` / `demo-bioprocess-pw`) with 28
logs across five crops and two equipment records, one rated and one unrated, so
the depreciation overlay is visibly partial. **Shots 4, 7 and 8 of the existing
runsheet are obsolete** — the states they say cannot be captured are now
reachable. **States that cannot be captured must be stated as absent, never
staged.**

---

## PART 8 — Final submission checklist

### CONTENT

- [ ] **Chapter 1 correct** — objectives unchanged; §1.5's "lightweight statistical regression" reconciled with the Random Forest (X-10); §1.5's offline-write scoping is accurate and should be the wording Chapter 3 aligns to
- [ ] **Chapter 2 citations verified** — 12 missing reference entries completed; ≥15 total and ≥70% recent (needs ~13 additional recent sources)
- [ ] **Chapter 3 matches implementation** — §3.6.8 rewritten as designed-not-implemented; NFR §3.3.2(d) restated as unmet; §3.8.4 moved or annotated; RBAC, throttling, input bounds, token expiry and log scrubbing added to §3.6.6/§3.7; post-harvest drying and enterprise economics given modules; Table 3.1 completed; §3.6.2 given immutability and contra-entry correction; §3.6.1 offline reads rewritten as built; §3.6.3 says CSV; §3.6.4 restated as captured-not-costed; §3.6.5 RMSE and the nine metrics; §3.6.7 expiry, hashing, single-404
- [ ] **Chapter 4 uses verified evidence** — §4.1 re-baselined to `78a68c2`; every figure re-sourced; §4.6.4 replaced by the false-positive methodology finding; §4.9 RMSE filled and the reproducibility qualification deleted; §4.10 replaced with the 29 Aug set; new §4.12 security/authorisation/deployment; §4.15 replaced with the verified limitations register; `[CONFIRM]` placeholder resolved
- [ ] **Chapter 5 conclusions trace to evidence** — all 60 corrections in Part 1 applied; Table 5.1 added; 5.1.2 written
- [ ] Abstract re-sourced (it carries 190 / 93% / 89 / 7,679.9 ms / 116.4 ms / 1,613.8 ms)
- [ ] **No `[PLACEHOLDER]`, `[CONFIRM]` or bracketed editorial note survives anywhere**, including the List of Figures note and Chapter 5's closing "Note for submission"

### CONSISTENCY

- [ ] Objectives trace Ch1 → Ch3 → Ch4 → Ch5 with no broken chain (all four chains are currently broken; see Part 3.1)
- [ ] No unsupported feature claims — every item on the closeout's must-not-claim list (25 items) checked and absent
- [ ] No contradictory metrics — all 40 rows of Part 5 applied
- [ ] Terminology consistent — the seven decisions in Part 4 applied
- [ ] "the frozen tag" replaced throughout (14 occurrences)
- [ ] The phrase "CI is green" appears nowhere

### REFERENCES

- [ ] Every citation appears in the references (**12 currently missing**)
- [ ] Every reference is cited (**currently satisfied — no orphans**)
- [ ] Citation style consistent APA 7 (**currently satisfied in both text and list**)
- [ ] Known citation defects resolved — the cost-behaviour taxonomy source and the safe-storage moisture guidance (Tier A(d), ADR 0002)
- [ ] ≥15 entries; ≥70% within five years

### TABLES AND FIGURES

- [ ] Numbering sequential (**currently PASS** — 3.1, 4.1–4.26, no gaps or duplicates)
- [ ] Captions correct — table captions above and un-bold (**PASS**); figure captions below and centred (**no figures exist**)
- [ ] Every figure/table referenced in text (**22 of 27 tables are not**)
- [ ] Screenshots readable — none captured yet
- [ ] No stale evidence — Tables 4.3, 4.4, 4.5, 4.7, 4.8, 4.9, 4.10–4.16, 4.19, 4.20, 4.26 all re-sourced
- [ ] Table 5.1 added and both front-matter lists updated

### WORD FORMATTING — verified in `Thesis_Ch1-5.docx`

- [x] **Margins** — left 1,984 twips = **3.5 cm**; top/right/bottom 1,417 twips = **2.5 cm**. Compliant
- [x] **Font** — Times New Roman throughout via the `Normal` style. Compliant
- [x] **Font size** — body 12 pt (`sz` 24); chapter title 14 pt (`sz` 28); table content 10 pt (`sz` 20). Compliant
- [x] **Line spacing** — body 2.0 (`w:line="480"`); abstract 1.0 (`w:line="240"`); table cells 1.0. Compliant
- [x] **Block paragraphing** — 12 pt after each paragraph. Compliant
- [x] **Justification** — body justified both edges. Compliant
- [ ] **Heading hierarchy** — verify H2/H3 render bold at 12 pt; re-verify Chapter Five's headings after the remap
- [x] **Roman numbering for preliminary pages** — section 0 carries `pgNumType lowerRoman start=1`. Compliant
- [x] **Arabic numbering for the main thesis** — section 1 carries `pgNumType start=1` in the default Arabic format. Compliant
- [x] **Footer sections correctly separated** — two `sectPr`, each with its own `footerReference`. Compliant
- [ ] Table of contents updated after the Chapter 5 remap and any repagination
- [ ] List of tables updated (add Table 5.1)
- [ ] **List of figures updated** — currently a bracketed editorial note and **must not ship in that state**
- [ ] Minimum 50 pages Ch1–Ch5 (**currently ~97 — comfortably met**)

### FINAL REVIEW

- [ ] PDF generated
- [ ] PDF visually inspected page by page
- [ ] No blank pages
- [ ] No broken tables — the per-crop and Lighthouse tables are the widest; check they do not split badly across pages, and consider landscape for any that do
- [ ] No cut-off figures — check every inserted screenshot at print size
- [ ] No header/footer errors — check the roman→arabic transition renders at the right page
- [ ] No obvious formatting defects — the SigLine paragraphs in Declaration and Certification contain runs of dot leaders that may reflow

---

## PART 9 — Prioritised action list

### MUST FIX BEFORE SUBMISSION

**Category A — false statements. The evidence positively contradicts these.**

1. **Delete every "does not net reversals" claim** — Ch4 §4.6.4, §4.14, Table 4.26; Ch5 §5.2.2, §5.2.3, §5.5, §5.7.1(a), §5.8. Replace §4.6.4 with the false-positive methodology finding and add the matching Ch5 interpretive subsection. *(C-08; corrections 5-04, 5-08, 5-25, 5-33, 5-37, 5-56)*
2. **Delete "the model artefact is not reproducible from the repository"** — Ch4 §4.9, Ch5 §5.5. Replace with the fingerprint, the six-decimal agreement, the 18 tests and the cross-environment record. *(C-09; 5-32)*
3. **Delete "the Olympic-average yield baseline is not reachable"** — Ch4 Table 4.2 row 11, Ch5 §5.2.2, §5.7.3(c). *(C-15; 5-05, 5-48)*
4. **Delete "cowpea and tomato cannot be entered"** — Ch4 Table 4.2 row 12. *(C-16)*
5. **Delete "unbounded monetary fields" and "no equipment edit path"** — Ch4 §4.14, Ch5 §5.5, §5.7.1(b), §5.7.1(c). Both are closed and verified live. *(5-33, 5-38, 5-39)*
6. **Delete "development stopped at the freeze tag"** and re-baseline §4.1 to `78a68c2`. *(C-26; 5-57)*
7. **Correct "no TLS, no backup and recovery, no secret management"** — three of the four are false. Only "no observability" survives. *(5-30)*
8. **Correct "a repeat visit transfers nothing"** — it transfers 127 B over 7 requests. *(5-11, 5-55)*
9. **Rewrite Chapter 3 §3.6.8 in the conditional.** The USSD/SMS channel does not exist in any form — no route, no webhook, no parser, no sender mapping, no test, no simulated harness. The present-tense description reads as built, and the sentence about simulated payloads asserts a demonstrability that does not exist. **This is the single most serious overclaim in the thesis.** Reconcile NFR §3.3.2(d), Objective 1's inclusive-entry claim and Ch5 §5.2.1 to it. *(Closeout §5.4, §5.7.1)*
10. **Reconcile Chapter 3 §3.8.4.** The usability evaluation is presented among "the evaluation actually undertaken". It was not undertaken. *(Closeout §5.6)*

**Category B — stale figures.**

11. Apply all 40 rows of the numerical consistency register (Part 5), **including the abstract**. The high-frequency replacements are 190→422/418/4/0, 93%→96%, 89→148, 9 files→13, 33.48%→43.18%, and the whole 17 August performance set → the 29 August set. *(N-01…N-40)*
12. Fill the RMSE placeholder with **0.4883 t/ha** and change §3.6.5's "may additionally be reported" to "is additionally reported". *(N-12)*
13. Resolve the `[CONFIRM — re-check provider pricing pages]` placeholder or restate the retrieval date. *(N-31)*
14. Re-capture Tables 4.10–4.16 against the five-crop farm; report both break-even price bases. *(N-34, N-35)*
15. Correct the two arithmetic ratios: 66× → **80×** (FCP), "about five" → **about three and a half** (LCP). *(N-21, N-22)*

**Category C — structure and completeness.**

16. **Restructure Chapter 5** to the mandated `5.1 Summary / 5.2 Conclusion / 5.3 Recommendations`, or at minimum retitle the chapter. Write **5.1.2 Summary of findings** (draft supplied in Part 1.3). *(5-60)*
17. **Add Table 5.1**, the objective-to-conclusion matrix (Part 2). Chapter 5 currently has no table.
18. **Add Chapter 4 §4.12** — security, authorisation and deployment verification. This is the largest body of verified, unreported evidence in the project and it is the direct answer to Objective 3. Expand Ch5 §5.2.3 to match. *(5-07)*
19. **Complete the 12 missing reference entries**, then bring the list to ≥15 and to ≥70% within five years (≈24 recent of ~34 total). *(Part 6)*
20. **Capture the figures.** Architecture diagram, ERD, paired-write sequence, and the interface screenshots per the closeout §7 capture plan. Then complete the List of Figures — **the bracketed placeholder note must not ship**. *(Part 7.2)*
21. **Add in-text references for the 22 unreferenced tables.** *(Part 7.1)*
22. **Delete Chapter 5's closing "Note for submission"** once the references are complete. *(5-29)*
23. Replace "the frozen tag" throughout (14 occurrences). *(T-03)*
24. Verify no sentence anywhere claims a machine-hour, utilisation or cost-per-hour figure; that "CI is green" appears nowhere; and that no farm-wide total is quoted from `dss_per_crop.json`. *(Closeout §11)*

### FIX IF TIME ALLOWS

25. Add the underclaim corrections to Chapter 3 — RBAC and the five other verified security capabilities in §3.7; the post-harvest drying module; the enterprise-economics module; ledger immutability and contra-entry correction in §3.6.2; offline reads as built in §3.6.1; the nine Tier-1 metrics in §3.6.5; `ShareToken`, `crop`, `reverses_id` and `client_id` in Table 3.1. **Each costs the thesis credit while it stands, and each leaves Chapter 4 reporting results the methodology never specified.** *(Closeout §5.7 items 4–10)*
26. Re-run the negative controls and the driven-browser probe at `78a68c2` rather than attributing them by commit and date. *(5-01, 5-26)*
27. Re-measure the precache figure at the baseline, or attribute it to `59a6286`. *(N-24)*
28. Resolve the two open implementation citations — cost-behaviour taxonomy and safe-storage moisture guidance. These also count toward the recent-reference quota. *(5-40, ADR 0002)*
29. Delete or source the unsupported "Nigerian median mobile throughput is far above that threshold". *(5-21)*
30. Add the drying-curve and performance figures. *(Part 7.2)*
31. Reconcile §1.5's "lightweight statistical regression" with the Random Forest, preferably by arguing the step up the modelling ladder in §5.4 rather than by widening §1.5. *(X-10)*
32. Apply the terminology decisions of Part 4 systematically rather than only where a correction already touches the text.

### POST-SUBMISSION IMPROVEMENT

33. **Run the usability panel** — three to five evaluators, the existing instrument pack, instruments retained as scans. This closes Objective 4 and is the highest-value remaining piece of evidence in the entire project. It is post-submission only because it cannot be done well in the remaining time; if the schedule permits it, it moves to MUST FIX.
34. Component tests for the page and form layer, beginning with the drying-curve chart and the decision-support panels.
35. An end-to-end browser test of the offline-to-online transition and the service-worker lifecycle, used to settle the stale-revalidation window that is presently reasoned but unreproduced.
36. Concurrency measured on PostgreSQL rather than inferred from SQLite.
37. Independent security review and load testing, to replace the reasoned tenancy figures with measured ones.
38. Consume `equipment_id` and `hours_used` to produce cost-per-hour and utilisation figures — bounded by the fact that `hours_used` is populated on three of eight seeded mechanisation logs.
39. Give `GET /bioprocess/summary` a consumer.
40. Report the forecast prediction interval prominently — the confidence band from the forest's tree spread is a better answer to "why should a farmer trust a forecast?" than an in-distribution R².
41. Retrain the forecast tier on accumulated real records, at which point the pre-processing pipeline Olisah et al. (2024) describe becomes the substantive work.
42. Implement the feature-phone entry channel against a live carrier gateway.
43. Execute the field evaluation designed in §3.8.5.

---

## PART 10 — Standing rules for anyone editing the thesis from here

1. **Correct Chapter 4 before Chapter 5.** Chapter 5 interprets Chapter 4. Every Chapter 5 correction in Part 1 assumes the corresponding Chapter 4 correction has landed; doing Chapter 5 alone manufactures a fresh contradiction.
2. **Correct Chapter 3 before either.** All four objective chains are broken at Chapter 3, and an examiner reads in order.
3. **Quote backend and frontend coverage together, or neither.** 96% alone misrepresents the system.
4. **Never write "CI is green."**
5. **Never quote a machine-hour, utilisation or cost-per-hour figure.**
6. **Never compare a Lighthouse score or TBT across the 17 and 29 August sets.**
7. **Never quote a farm-wide total from `docs/ch4-data/dss_per_crop.json`.**
8. **The maize chain — ₦450/kg, 100 kg, 84 kg, 7.78 kg, ₦35.00, ₦41.67 — is load-bearing across two chapters.** Do not change a division in it without re-stating the whole chain.
9. **A state that cannot be captured is stated as absent, never staged.**
10. **Where evidence does not reach a conclusion the reader might expect, say so.** That commitment is stated in Chapter 5 §5.1 and it is the reason the chapter is defensible; every correction above exists to keep it true.
