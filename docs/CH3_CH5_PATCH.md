# AGRI-PROFIT — Chapter Three and Chapter Five patch specification

Erhabor Israel Isima · 2021/1/83967EA
Prepared 31 August 2026 · against `Thesis_Ch1-5.docx`

One pass through Chapter Three, plus two Chapter Five additions. Every replacement below
is drop-in text. Nothing in this file changes application code.

Two items are marked **PENDING VERIFICATION**. Do not enter those until the candidate has
confirmed them. An unverified citation is worse than an absent one.

---

## PATCH 1 — §3.6.4 Mechanisation and Equipment Tracker

**Find** the paragraph beginning "This module records equipment acquisition cost, maintenance
events and a straight-line depreciation rate" and running to "...recorded in the project's third
architecture decision record."

**Replace the first two sentences and insert a new paragraph.** The sentences about the
per-operation equipment association and ADR-0003 are retained unchanged at the end.

> This module records equipment acquisition cost, maintenance events, and a per-item
> depreciation rate supplied by the user. Depreciation is computed on a straight-line basis
> (Kay et al., 2020) and is not posted to the ledger: it is derived as an overlay at report time
> and allocated to crops in proportion to direct cost, because posting a synthetic depreciation
> row would require either an unpaired financial entry, which violates the paired-write
> invariant, or a fabricated operational log describing an event that did not happen. An
> equipment record can be corrected after entry through a partial-update path, so that a
> mistyped depreciation rate is not permanent.
>
> Three simplifications are stated here rather than concealed. First, the annual charge is taken
> against the full purchase value: conventional machinery costing charges purchase cost less an
> estimated salvage value over the useful life, with salvage estimated as a published
> age-and-class factor applied to the new list price of a comparable machine (Johnson, 2020).
> The platform records only the purchase value and not a list price, so the salvage factor cannot
> be applied even where the user holds one. Second, the derived charge covers depreciation alone,
> where conventional ownership cost also includes interest on the average investment and a
> combined taxes, insurance and housing charge (Johnson, 2020). Third, the two omissions act in
> opposite directions and do not cancel in any principled way: against a full ownership-cost
> calculation for a representative tractor, a rate entered as the reciprocal of useful life gives
> a figure approximately six per cent below the conventional total, while a salvage-adjusted rate
> gives one approximately forty per cent below it. The direction and magnitude of the divergence
> therefore depend on the rate the user supplies, and no claim of conservatism is made.
>
> The break-even price on a cash basis and the operating-expense ratio exclude all non-cash
> charges and are unaffected by any of the above. Only the break-even price on a total-cost basis
> inherits the divergence. Representative machine performance and salvage parameters, where a
> user holds them, are published in the machinery-management data standard of the American
> Society of Agricultural and Biological Engineers (ASABE, 2011).
>
> [RETAIN UNCHANGED:] A per-operation association between an individual activity and a specific
> equipment item, together with the hours that item was used, is captured and validated at the
> point of entry but is consumed by no service: the platform produces no machine-hour,
> utilisation or cost-per-hour figure, and none appears anywhere in this work. The boundary is
> stated as captured but not costed, and the reasoning is recorded in the project's third
> architecture decision record.

**Why:** the section previously described straight-line depreciation with no source and did not
disclose that salvage value, interest and TIH are all omitted. The arithmetic in the third
sentence is derived from the worked tractor example in Johnson (2020): conventional total annual
ownership cost of $12,241 against $11,500 at a reciprocal-of-life rate, and $7,060 at a
salvage-adjusted rate.

---

## PATCH 2 — §3.6.9 Post-Harvest Drying Module

**Find:** "and, where at least three readings exist, a least-squares fit of the Newton and Page
models on their linearising transforms, returning the rate constant k and, for the Page model,
the exponent n."

**Replace with:**

> a rate constant for the Newton model obtained in closed form from the initial and final
> moisture ratio; and a least-squares fit of the Page model on its linearising transform,
> ln(−ln MR) = ln k + n·ln t, returning the rate constant k and the exponent n. The Newton
> constant is computable from the endpoints alone; the Page fit requires at least three usable
> readings and is withheld, rather than approximated, below that threshold.

**Why:** the code does not fit Newton. `newton_k` is closed-form, k = −ln(MR_final)/t, with no
regression and no intermediate readings. Only `page_fit` performs a least-squares fit. Chapter
Three currently claims a method the implementation does not use.

---

## PATCH 3 — §3.6.5(b) Predictive Decision-Support Engine

**Insert** at the end of the Tier 2 paragraph, after the description of the Random Forest
regressor:

> The forecast is accompanied by a dispersion measure computed across the individual trees of the
> ensemble, reported as a confidence percentage and as an interval about the ensemble mean. The
> measure indicates agreement among trees; it is not a calibrated prediction interval, and is
> reported as such. Established methods for interval estimation from a random forest exist
> (Meinshausen, 2006; Wager et al., 2014) and are identified in Chapter Five as the route to a
> calibrated figure.

**Why:** Chapter Four reports a confidence band. Chapter Three specifies no method for producing
it, so a number reaches the results chapter by a route the methodology never describes.

---

## PATCH 4 — §3.6.10 Enterprise Economics Module, four sourcing insertions

The section currently cites Kay, Edwards & Duffy once and describes five further methods with no
source. Apply the four replacements below within the existing paragraph.

### 4a — Operating-expense ratio

**Find:** "computes an operating-expense ratio that excludes all non-cash charges"

**Replace with:**

> computes an operating-expense ratio following the conventional definition of operating expense
> over gross revenue with non-cash charges excluded (Farm Financial Standards Council, 2024;
> Griffith et al., 2024), with one divergence: the numerator counts only cost that carries a
> behaviour classification, so cost recorded but unclassified is excluded rather than
> distributed, and the classification-coverage figure reported alongside states what proportion
> of recorded cost the ratio rests on. Interest is excluded because no interest is modelled

### 4b — Olympic average · **PENDING VERIFICATION**

**Find:** "and computes an Olympic-average yield baseline, which discards the highest and lowest
season before averaging and is refused, with the season count stated, below three seasons."

**Replace with:**

> and computes an Olympic-average yield baseline following the convention used in United States
> farm programme benchmark yields, which discards the highest and lowest observation before
> averaging the remainder (USDA Farm Service Agency, [YEAR]). That convention is applied there
> over five seasons; the present implementation admits three, the minimum at which any
> observation survives the discard, and at exactly three seasons the result is therefore the
> median rather than a mean of several values. The season count is reported with every baseline,
> so that a figure resting on three seasons is not read as one resting on five.

**HOLD.** Do not enter until the candidate confirms the current ARC benchmark-yield form at
fsa.usda.gov and supplies the publication year and document title. Note for the record: USDA
RMA's Actual Production History yield is a *simple* 4-to-10-year average and is **not** the
correct source for this claim.

### 4c — Partial budget

**Find:** "A partial-budget calculator evaluates a proposed change by four terms"

**Replace with:**

> A partial-budget calculator evaluates a proposed change by four terms — added revenue, reduced
> cost, lost revenue and added cost — following the standard method for appraising incremental
> change in smallholder farming systems (CIMMYT, 1988; Kay et al., 2020)

### 4d — Fixed-cost allocation base

**Insert** immediately after "derives the fixed-cost overlay of Section 3.6.4 and allocates it in
proportion to direct cost":

> — conventional practice allocates fixed cost on a physical base, most commonly cultivated area
> (Kay et al., 2020; Johnson, 2020), but no field, plot or area entity exists in the data model,
> so no physical base is available. The substitution is stated rather than concealed: it
> distributes fixed cost toward the enterprise that spent most, which coincides with an
> area-based allocation only where spending per unit area is uniform across crops —

---

## PATCH 5 — §3.7 Security Design · **PENDING VERIFICATION**

**Find:** "three roles are defined over a table of twelve named permissions"

The code reconnaissance reports **eleven** permissions in `ROLE_PERMISSIONS` (`core/roles.py`).
The thesis says twelve at four sites: §3.7, and three further sites in Chapters Four and Five.

**HOLD.** Count the entries in `core/roles.py` directly. If eleven, correct all four sites to
"eleven named permissions". If twelve, no change and the reconnaissance undercounted. Do not
change one site without changing all four.

---

## PATCH 6 — Chapter Five, machinery costing as future work

**Insert** as a new paragraph in the future-work section.

> The mechanisation data captured but not costed (Section 3.6.4) is precisely the input required
> by the conventional cost-per-hour and cost-per-area method: total annual machine cost divided
> by annual hours of use, then divided by field capacity in area per hour (Johnson, 2020).
> Implementing it requires three additions to the data model — a new list price per equipment
> item, so that a published salvage factor can be applied; an annual-use figure; and consumption
> of the per-operation hours-used field already captured — together with the interest and
> taxes-insurance-housing components omitted from the present ownership calculation. Published
> parameters for useful life, salvage and repair factors are available by machine class (ASABE,
> 2011). The work is bounded, the method is published, and the data model change is additive
> rather than structural.

---

## PATCH 7 — Chapter Five, depreciation limitation

**Insert** in the limitations section.

> The depreciation overlay omits salvage value, interest on the average investment, and the
> combined taxes, insurance and housing charge that conventional machinery costing includes. The
> resulting divergence from a full ownership-cost figure depends on the depreciation rate the
> user supplies and is not consistently in one direction, so the break-even price on a total-cost
> basis should be read as indicative rather than as a costed figure. The break-even price on a
> cash basis and the operating-expense ratio are unaffected, both excluding non-cash charges.

---

## REFERENCE ENTRIES TO ADD

Verified and ready:

> ASABE. (2011). *Agricultural machinery management data* (ASAE D497.7, R2025). American Society
> of Agricultural and Biological Engineers.

> CIMMYT. (1988). *From agronomic data to farmer recommendations: An economics training manual*
> (Rev. ed.). International Maize and Wheat Improvement Center.

> Griffith, C., Mills, B., Kim, K., & Johnson, J. (2024). *Farm financial analysis series: Ratios
> to measure farm financial health* (Publication 3712). Mississippi State University Extension
> Service.
> https://extension.msstate.edu/sites/default/files/publications/P3712_web.pdf

> Johnson, J. (2020). *Farm machinery cost calculations* (Publication 3543). Mississippi State
> University Extension Service. https://www.agecon.msstate.edu/whatwedo/budgets.php

> Meinshausen, N. (2006). Quantile regression forests. *Journal of Machine Learning Research, 7*,
> 983–999.

> Wager, S., Hastie, T., & Efron, B. (2014). Confidence intervals for random forests: The
> jackknife and the infinitesimal jackknife. *Journal of Machine Learning Research, 15*(1),
> 1625–1651.

Requiring confirmation before entry:

> Farm Financial Standards Council. (2024). *Financial guidelines for agriculture*. Farm Financial
> Standards Council.
> — **CONFIRM:** the candidate must hold the 2024 edition and verify that its operating-expense
> ratio definition matches Patch 4a. The FFSC ratio set was revised between the 2021 and 2022
> editions (21 recommended measures reduced to 13). If the 2024 edition is not in hand, cite the
> edition that is.

> Kay, R. D., Edwards, W. M., & Duffy, P. A. (2020). *Farm management* ([Xth] ed.). McGraw-Hill.
> — **CONFIRM the edition number** from the copyright page. The existing reference list carries a
> 2016 edition; Johnson (2020) cites a 2020 edition without an edition number. If the 2020
> edition is obtainable, use it — the salvage-value factors are published there. Whichever is
> used, the in-text year must be consistent across §1.4, §2.7.2, §3.6.10 and Chapter Five.

> ASABE. (2006). *Agricultural machinery management* (ASAE EP496.3, R2020). American Society of
> Agricultural and Biological Engineers.
> — **CONFIRM** the reaffirmation date from ASABE's own standards listing at asabe.org. Do not
> cite a document-reseller page.

> USDA Farm Service Agency. ([YEAR]). [Title of ARC benchmark-yield documentation].
> — **HOLD** pending Patch 4b verification.

---

## CHANGE LOG

| # | Site | Change | Type |
|---|---|---|---|
| 1 | §3.6.4 | Depreciation sourced to Kay et al.; three omissions disclosed with quantified divergence; ASABE cited for parameters | Sourcing + honesty |
| 2 | §3.6.9 | Newton described as closed-form, not fitted; Page fit and its 3-reading floor stated | **Factual correction** |
| 3 | §3.6.5(b) | Confidence band method stated; described as uncalibrated; Meinshausen and Wager identified as the route to calibration | Method gap |
| 4a | §3.6.10 | Operating-expense ratio sourced; narrower numerator disclosed | Sourcing + honesty |
| 4b | §3.6.10 | Olympic average sourced; 3-vs-5 season divergence disclosed | **PENDING** |
| 4c | §3.6.10 | Partial budget sourced to CIMMYT and Kay et al.; four terms named | Sourcing |
| 4d | §3.6.10 | Allocation base sourced; proportional-to-direct-cost stated as a substitution with its failure condition | Sourcing + honesty |
| 5 | §3.7 + 3 sites | Permission count, eleven vs twelve | **PENDING** |
| 6 | Ch5 future work | Machine-rate implementation named as bounded work with published method | Addition |
| 7 | Ch5 limitations | Depreciation divergence, direction not fixed | Addition |

---

## RULES FOR THE AGENT

1. Do not enter Patch 4b or Patch 5 until the candidate confirms them.
2. Do not write any reference entry marked CONFIRM until the candidate supplies the field.
3. Do not modify application code, tests, schemas or configuration.
4. Do not modify Chapters One, Two or Four.
5. Preserve existing heading styles and numbering. Do not reflow untouched paragraphs.
6. After applying, report a diff of every paragraph changed, and confirm no other occurrence of
   "least-squares fit of the Newton" survives anywhere in the document.
