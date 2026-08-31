# Merge Audit — `Thesis_Ch1-5.docx`

**Date:** 26 August 2026
**Output:** `Thesis_Ch1-5.docx` (115 pages, 26,481 words, 27 tables, 2 sections)

---

## 1. Files used

| Role | File | Why |
|---|---|---|
| Chapters 1–3 | `Thesis_Ch1-3.docx` | Contains Chapter One–Three plus preliminary pages and the reference list. 310 paragraphs. |
| Chapters 4–5 | `Thesis_Ch4-5.docx` | Contains Chapter Four (§4.1–4.15) and Chapter Five (§5.1–5.8) and 26 tables. No preliminaries, no reference list. |
| Formatting standard | `Updated B.Tech Final Project Guideline for 2025_2026_v1.pdf` | 23-page departmental guideline. Its margin comments (Commented [MP1]–[MP66]) and §2.2–2.5 are the presentation authority used throughout. |

**Files inspected and deliberately NOT used:**

- `docs/print/Thesis_Ch1-3.docx` — an older save of the same Chapters 1–3 (18:38 vs 19:06 on 19 Aug, 44,744 vs 45,920 bytes). Superseded.
- `AgriProfit_Chapters_1-3.docx`, `AgriProfit_Chapters_1-3_corrected.docx` — earlier drafts (160 paragraphs vs 310, US Letter page size, no preliminary pages). Superseded by `Thesis_Ch1-3.docx`.
- `AgriProfit_Evaluation_Pack.docx`, `AgriProfit_Viva_Prep.docx` — supporting material, not thesis chapters.

---

## 2. Formatting normalised to the standard

| Element | Standard requires | Applied |
|---|---|---|
| Page size | A4, 21.0 × 29.7 cm | A4. (Sources were 8.5 × 11 in and A4-with-wrong-margins.) |
| Margins | Left 3.5 cm; top/bottom/right 2.5 cm | Exactly. Source Ch1–3 used 3.81/2.54 cm. |
| Font | Times New Roman throughout | Every run in the document forced to Times New Roman (0 non-conforming runs verified). Code block kept in Courier New — see §6.5. |
| Body size | 12 pt | 12 pt. |
| Chapter number and title | 14 pt, bold, centre, capitalise case | 14 pt bold centred caps, on two lines: `CHAPTER FOUR` then `4.0  RESULTS AND ANALYSIS`. |
| Other headings | 12 pt bold, sentence case | All 44 second-level and 73 third-level headings. |
| Line spacing | 2.0 throughout; abstract 1.0; indented quotations 1.0 | Body, headings, references, TOC at 2.0. Abstract, the indented author's note in §4.12 and the code block at 1.0. |
| Paragraphing | Block paragraphing, one extra line space between paragraphs | No first-line indent; 12 pt space after each paragraph. |
| Alignment | Justify right and left | All body paragraphs, list items and reference entries. |
| Page numbering | Roman for preliminaries, Arabic for the body | Two Word sections: preliminaries i–xvii, body 1–98. Bottom-centre `PAGE` fields. |
| Table title | Un-bold, on top, close to the table | All 27 captions un-bold, above the table, 3 pt gap, `keep with next`. Source had them bold. |
| Table content | Centralised, gridlines, not below 10 pt | Centred, full gridlines, 10 pt (≥5 columns) or 11 pt. Header row bolded and set to repeat across page breaks. |
| Lists | First level `(a)`; project objectives `(i)`; second level roman | Word auto-numbering replaced with literal markers: the four objectives in §1.3 as `i.`–`iv.`; the other nine lists as `(a)`, `(b)`, … |
| References | APA 7th | Existing APA formatting preserved; 0.5″ hanging indent, double spaced. |
| Preliminary pages | Cover, Title, Declaration, Certification, Dedication, Acknowledgements, Abstract, Table of Contents, List of Tables, List of Figures | All ten present. See §5 for the two that need your content. |

---

## 3. Numbering and cross-reference corrections

- **Table numbering** — verified sequential with no gaps: Table 3.1, then 4.1 → 4.26. Nothing renumbered; the source numbering was already correct.
- **Caption placement** — all 27 captions verified to sit immediately above their table (0 adjacency failures).
- **Section numbering** — all 117 headings verified in sequence (1.1→1.5, 2.1→2.7, 3.1→3.9, 4.1→4.15, 5.1→5.8, and every third-level heading). 0 problems.
- **Chapter numbering** — flows One → Five, then References. No duplicate chapter headings from the merge.
- **In-text cross-references** — every `Table N.N` mentioned in the text has a matching table; every `Section N.N` mentioned has a matching heading. 0 dangling references.
- **Chapter number prefix added** — chapter titles were bare (`INTRODUCTION`); they now read `1.0  INTRODUCTION` … `5.0  DISCUSSION, CONCLUSION AND RECOMMENDATIONS` as the standard requires.
- **Manual page numerals removed** — Chapters 1–3 had roman numerals typed as body text at the top of preliminary pages, and they were wrong: the sequence ran I, II, III, **VI, V, VI** (VI twice, out of order). These were deleted and replaced with real page-number fields.
- **Old hand-typed table of contents removed** — the 51-line manual TOC in Chapters 1–3 carried stale page numbers. Replaced with a live Word `TOC` field, now populated with correct page numbers. A live List of Tables field was added likewise. Both refresh on open.

---

## 4. References

- **9 entries** carried across from Chapters 1–3. Chapters 4–5 contained no reference list, so there was nothing to merge and **no duplicates were found or removed**.
- The reference list was moved to sit after Chapter Five.
- In-text citations were checked against the list. See issue **#5** below — this needs your attention.

---

## 5. Issues requiring your decision

> These were **not** silently altered. Each needs an academic decision.

### #1 — The Certification page certifies the wrong degree ✅ RESOLVED 26 Aug 2026 (see §10)

The certification page reads:

> "…meets the regulations governing the award of the degree of **Bachelor of Technology in Computer Science** of the Federal University of Technology, Minna."

This is template text carried over from the guideline (whose sample is a Computer Science project). It contradicts the title page in the same document, which reads **Bachelor of Engineering in Agricultural and Bioresources Engineering**. Left unchanged because a degree title is an administrative fact, not a typo. **Correct this before submission.**

### #2 — Your surname is spelled two ways

- Cover page and title page: **EHRABOR** ISRAEL ISIMA
- Declaration and certification: **ERHABOR**, ISRAEL ISIMA

Both spellings are preserved exactly as found. Pick the correct one and make it consistent. (The guideline's format is `SURNAME, OtherNames`.)

### #3 — The Abstract contradicts Chapter Four ✅ RESOLVED 26 Aug 2026 (see §10)

The abstract was written against earlier figures. Chapter Four, written against the frozen evidence tag, reports different ones:

| Abstract says | Chapter Four says |
|---|---|
| "87 passing tests at 90% backend statement coverage" | §4.3.1, §4.15: **190** passing backend tests at **93%** statement coverage, plus 89 frontend tests |
| "Five evaluators returned a mean System Usability Scale score of 60.0" | §4.12: the usability strand is **outstanding**. Table 4.24 is headed "to be completed". §4.13 reports Objective 4 as only **partially met** and states that no usability finding may be claimed |
| "reducing largest contentful paint from 7.68 s to 1.61 s" | §4.10.2: **first paint** fell from 7,679.9 ms; LCP in the warm run was 1,613 ms. The abstract merges two different metrics |
| "below 205 MiB, ₦20,950 per month, ₦105 per farm per month" | §4.11.2 explicitly records a **correction** to an earlier reasoned estimate |

The SUS claim is the serious one: the abstract asserts a completed usability evaluation that Chapter Four says was never run. **The abstract needs rewriting against the Chapter Four figures.** The ₦35.00 / ₦41.67 / 19% drying figures agree between the two and were left untouched.

### #4 — Chapter Two is below the required length → gap analysis in §10

The guideline (page 15) requires the literature review to be **"NOT less than 15 pages"** for implementation-based projects. Chapter Two runs from page 8 to page 19 — approximately **11 pages**. Chapter lengths as merged: Ch1 ≈ 7, Ch2 ≈ 11, Ch3 ≈ 12, Ch4 ≈ 45, Ch5 ≈ 21 pages. The 50-page whole-document minimum is met comfortably (98 body pages).

### #5 — The reference list fails two guideline requirements → audit table in §10

The guideline (§2.4) requires **at least 15 references** for implementation-based projects, of which **70% must be from the last five years**.

- Present: **9 entries**, of which **2 (22%)** are 2021 or later (Mhlanga 2023, Olisah et al. 2024). The rest are 1990, 1994, 1996, 2015, 2017, 2020, 2020.
- Works cited with **no entry in the reference list** (first appearance is Chapter One, not Chapter Two — corrected in §10): Abbasi/Martinez/Ahmad (2022), Abiri et al. (2023), Basir et al. (2024), Dayioglu & Turker (2021), Gebresenbet et al. (2023), Giua/Materia/Camanzi (2020), Husemann & Novkovic (2012), Jaiyeola (2023), Javaid et al. (2022), Nirosha (2024), Poppe/Vrolijk/Bosloper (2023), Tummers/Kassahun/Tekinerdogan (2019).

Adding these twelve would satisfy the count. No bibliographic information was invented. Your own note at the end of the reference list records the same twelve and has been **kept in the document** (see #6) so it is not forgotten.

### #6 — Author notes and placeholders retained, not removed

Five author-facing markers were left in place deliberately, because deleting them would hide unfinished work. **All must be resolved and removed before submission:**

| Location | Marker |
|---|---|
| End of References | `[Note to author — remove before submission: …]` listing the twelve missing citations |
| §4.5.1 | `[INSERT VERIFIED RESULT HERE — figure numbers and captions for the interface screenshots…]` |
| §4.10.3 | `[INSERT VERIFIED RESULT HERE — re-run the Lighthouse audit against the frozen tag…]` |
| §4.12 | Table 4.24 and Table 4.25, both headed "to be completed", plus the indented "Author's note — what must exist before each cell is filled" |
| §5.4 | `Note for submission: several works cited in Chapter Two…` |

### #7 — Two preliminary pages need your content

- **ACKNOWLEDGEMENTS** — required by the guideline, present in neither source. The page was created with a bracketed placeholder. Nothing was written on your behalf.
- **LIST OF FIGURES** — the document contains **zero figures**. Neither source has a single image, chart or plate. §4.5.1 reserves a place for interface screenshots that were never supplied. The page exists with a bracketed note explaining this. If you add screenshots, caption them below the image as `Figure 4.1`, `Figure 4.2` … and the list will populate.

### #8 — Chapter One is missing sections the guideline lists

The guideline's Chapter One template lists 1.1 Background, 1.2 Motivation, 1.3 Statement of Problem, 1.4 Aim and Objectives, 1.5 Significance, 1.6 Scope and Limitation, 1.7 Organization of Study, 1.8 Definition of Terms. Your Chapter One has five sections (Background, Statement of the Problem, Aim and Objectives, Justification, Scope and Limitations). **Motivation of Study, Organization of Study and Definition of Terms have no counterpart.** Nothing was fabricated to fill them — confirm with your supervisor whether they are required.

### #9 — Three tables are dense

Tables 4.10 (7 columns), 4.18 (8 columns) and 4.20 (8 columns) fit inside the text column at 10 pt but are tight. The guideline permits landscape orientation for large tables. They were left portrait to avoid introducing section breaks and blank pages; convert them if your supervisor objects.

### #10 — Minor: no numbered equations

Chapter Four states the Page model (`MR = exp(−k·tⁿ)`) and its linearisation inline as running text. There are no display equations and therefore no equation numbering. The guideline does not require equation numbering, so this was left as written.

---

## 6. Corrections made (typographical only)

Each of these had an unambiguous intended reading. Everything else was left alone.

1. **Declaration** — `titled:” AGRI-PROFIT` → `titled: “AGRI-PROFIT` (missing opening quotation mark and space).
2. **Certification** — `The project tilted: …” …”…` → `The project titled: “…”` ("tilted" → "titled"; stray ellipses around the quoted title removed).
3. **Title page** — `PARTIAL FULFILLMENT` → `PARTIAL FULFILMENT` (guideline §2.1.1 requires UK English).
4. **Title page** — `AUGUST 2026` → `AUGUST, 2026`, matching the cover page and the guideline's `MONTH, YEAR` form.
5. **Abstract** — `largest contently paint` → `largest contentful paint`. **Note:** this fixes the spelling only; the claim itself is disputed by Chapter Four, see issue #3.
6. **Abstract** — `…per kilogram, and the 19% difference being post-harvest…` → `…per kilogram, the 19% difference being post-harvest…` (dangling conjunction). No figure changed.
7. **Abstract** — full stop added to the final sentence.
8. **Declaration signature block** — the source ran `Signature and Date` above the matriculation number. Restructured to the guideline's two-column layout: dotted rules, then `2021/1/83967EA` and `Signature and Date` side by side.
9. **Certification signature blocks** — the source had none. Blank signature blocks added for **Project Supervisor**, **Head of Department** and **External Examiner** as the guideline requires. Names left blank; none was invented.

**No numerical result, no equation, no table value, no citation and no academic argument was altered.**

---

## 7. Quality-control pass

Checks run against the finished document:

| Check | Result |
|---|---|
| Blank pages | **0** (all 115 PDF pages carry content) |
| Tables overflowing the text column | **0 of 27** — every table pinned to the 425.25 pt text column |
| Non-Times-New-Roman runs | **0** |
| Caption separated from its table | **0** |
| Table numbering gaps | **0** |
| Section numbering errors | **0 of 117 headings** |
| Dangling table cross-references | **0** |
| Dangling section cross-references | **0** |
| Duplicate chapter or section headings | **0** |
| Duplicate references | **0** |
| Chapter 3 → Chapter 4 transition | Intact — §3.9 Summary ends p. 30, Chapter Four opens p. 31 |
| Chapter 5 → References transition | Intact — §5.8 Conclusion ends p. 96, References opens p. 97 |
| Page numbering | Preliminaries i–xvii roman; body 1–98 arabic; both bottom-centre |
| Table of Contents | Live field, populated, correct page numbers |
| List of Tables | Live field, all 27 captions, correct page numbers |
| Content integrity vs. both sources | **0 paragraphs and 0 table cells unaccounted for.** Every difference maps to a logged transformation (list markers, numbered chapter titles, the replaced manual TOC, or a §6 correction) |

The fields were updated and repaginated in Microsoft Word, so the saved file already contains correct page numbers. `updateFields` is also set, so Word refreshes them again if you edit and reopen.

---

## 8. Source documents

`Thesis_Ch1-3.docx` and `Thesis_Ch4-5.docx` were **opened read-only and not modified**. Their timestamps and byte sizes are unchanged (45,920 bytes / 19 Aug 19:06 and 66,309 bytes / 26 Aug 03:07). All merging was done into a new file. No other file in the project was touched.

---

## 9. Before you submit — checklist

1. Fix the degree name on the Certification page (#1).
2. Settle the surname spelling (#2).
3. Rewrite the Abstract against the Chapter Four figures, especially the SUS claim (#3).
4. Add the twelve missing reference entries, and enough recent sources to reach 15 total with 70% from the last five years (#5).
5. Delete all five author notes and placeholders (#6).
6. Write the Acknowledgements (#7).
7. Add interface screenshots as numbered figures, or confirm with your supervisor that a figure-free submission is acceptable (#7).
8. Confirm whether Chapter Two needs expanding to 15 pages (#4) and whether the three missing Chapter One sections are required (#8).
9. Fill in the supervisor, HOD and external examiner names on the Certification page.

---

## 10. Academic-integrity and guideline-compliance remediation pass — 26 August 2026

This pass worked from the merged document. No chapter was rebuilt, no formatting was regenerated, and no numerical research result was altered.

### 10.1 Changes made to `Thesis_Ch1-5.docx`

| # | Location | Before | After | Evidence relied on |
|---|---|---|---|---|
| 1 | Certification page (single body paragraph) | "…award of the degree of **Bachelor of Technology in Computer Science** of the Federal University of Technology, Minna." | "…award of the degree of **Bachelor of Engineering in Agricultural and Bioresources Engineering** of the Federal University of Technology, Minna." | The title page of the same document: "…IN PARTIAL FULFILMENT OF THE REQUIREMENT FOR THE AWARD OF THE DEGREE OF **BACHELOR OF ENGINEERING IN AGRICULTURAL AND BIORESOURCES ENGINEERING**". Cover page and title page both name the Department of Agricultural and Bioresources Engineering, School of Infrastructure Process Engineering and Technology. The replaced wording is verbatim guideline template text (guideline pp. 2 and 4), whose sample project is a Computer Science one. |
| 2 | ABSTRACT | Three paragraphs, 431 words, containing "87 passing tests at 90% backend statement coverage", "Five evaluators returned a mean System Usability Scale score of 60.0", and an LCP claim that merged two metrics | One paragraph, **249 words**, reporting 190 backend tests at 93% statement coverage and 89 frontend tests; first paint 7,679.9 ms → 116.4 ms with largest contentful paint at 1,613.8 ms stated separately; and the usability evaluation stated as **not conducted, with no SUS score reported and Objective 4 only partly met** | §4.3.1, §4.15 (190 / 93% / 89); §4.10.2 (7,679.9 ms → 116.4 ms; LCP 1,613.8 ms); §4.11 and §4.15 (205 MiB, ₦20,950/month, ₦105/farm); §4.8 and §4.15 (₦35.00 → ₦41.67, 19%); §4.12, §4.13, §5.2.4, §5.5 (usability strand outstanding) |
| 3 | Abstract length and structure | 431 words over three paragraphs | 249 words in one paragraph | Guideline p. 7: the abstract "is a one paragraph summary … It should not be more than 150 – 250 words. It must be single-spaced, and must not be italicized." The existing single-spaced, non-italic `Abstract Body` style was retained unchanged. |
| 4 | `settings.xml` | no `w:updateFields` | `w:updateFields` set to true | The abstract shortened by roughly one page, so the preliminary-page sequence and both automatic listings needed a refresh. The document was then opened in Microsoft Word, all fields and the Table of Contents were updated, it was repaginated and saved, so the file already holds correct page numbers; the flag makes Word refresh them again after any further edit. |

**No figure in Chapters Four or Five was changed. No usability result was supplied. No reference was added.**

#### The one judgement inside change #1

The *discipline* is established beyond doubt — every other identity-bearing page in the document names Agricultural and Bioresources Engineering. The *degree style* is not equally certain: the title page says **Bachelor of Engineering**, while the departmental guideline this document is formatted against is titled "Updated **B.Tech** Final Project Guideline" and its template certification reads "Bachelor of Technology in …". The certification page was aligned to the title page, because internal agreement with the candidate's own title page is the strongest source the project contains, and because leaving "Computer Science" in place was not an option. See *Requires user verification* below: if the department awards B.Tech rather than B.Eng, **both** the certification page and the title page must change together.

### 10.2 Missing-reference audit (issue #5)

Twelve in-text citations carry no reference-list entry. Contrary to §5 above, their **first appearance is Chapter One**, not Chapter Two; the full corrected locations are given below. Full author lists were recovered from the first, un-abbreviated in-text mention wherever the document contains one.

| Citation | Chapter/Section | Existing bibliographic information | What is missing |
|---|---|---|---|
| Dayioglu & Turker (2021) | §1.1 (first use); §1.4 | Two authors, surnames Dayioglu and Turker; year 2021. Supports: global food production must rise for a population approaching 10 billion by 2050. | Title, journal or publisher, volume/issue, pages, DOI/URL, author initials. **REQUIRES EXTERNAL SOURCE VERIFICATION** |
| Abbasi, Martinez, & Ahmad (2022) | §1.1 (first use); §1.2; §1.5 | Three authors, surnames Abbasi, Martinez, Ahmad; year 2022. Supports: the shift of traditional farming methodology towards "Agriculture 4.0". | Title, journal or publisher, volume/issue, pages, DOI/URL, author initials. **REQUIRES EXTERNAL SOURCE VERIFICATION** |
| Abiri, Rizan, Balasundram, Shahbazi, & Abdul-Hamid (2023) | §1.1 (first use); §1.3 | Five authors, surnames Abiri, Rizan, Balasundram, Shahbazi, Abdul-Hamid; year 2023. Supports: integration of ICT, IoT, AI and data analytics to optimise agricultural systems. | Title, journal or publisher, volume/issue, pages, DOI/URL, author initials. **REQUIRES EXTERNAL SOURCE VERIFICATION** |
| Basir, Buckmaster, Raturi, & Zhang (2024) | §1.1 (first use); §1.4; §1.5 | Four authors, surnames Basir, Buckmaster, Raturi, Zhang; year 2024. Supports: accurate real-time data collection and on-farm recordkeeping as the foundation of precision agriculture. | Title, journal or publisher, volume/issue, pages, DOI/URL, author initials. **REQUIRES EXTERNAL SOURCE VERIFICATION** |
| Tummers, Kassahun, & Tekinerdogan (2019) | §1.1 (first use); §1.2; §2.4.2; §5.4 | Three authors, surnames Tummers, Kassahun, Tekinerdogan; year 2019. Supports: the evolution of FMIS from digitalised field books into decision-support platforms. Co-cited throughout with Fountas et al. (2015), which is in the list. | Title, journal or publisher, volume/issue, pages, DOI/URL, author initials. **REQUIRES EXTERNAL SOURCE VERIFICATION** |
| Javaid, Haleem, Singh, & Suman (2022) | §1.1 (only use) | Four authors, surnames Javaid, Haleem, Singh, Suman; year 2022. Supports: the globally unequal distribution and adoption of digital agricultural technologies. | Title, journal or publisher, volume/issue, pages, DOI/URL, author initials. **REQUIRES EXTERNAL SOURCE VERIFICATION** |
| Nirosha (2024) | §1.1 (first use); §1.2; §1.5; §2.4.2 | Single author, surname Nirosha; year 2024. Supports: Nigerian smallholders and medium-scale enterprises lacking technological infrastructure and capital. | Title, journal or publisher, volume/issue, pages, DOI/URL, author initials. Given name is not recorded anywhere in the project. **REQUIRES EXTERNAL SOURCE VERIFICATION** |
| Jaiyeola (2023) | §1.1 (first use); §1.5; §5.2.1 | Single author, surname Jaiyeola; year 2023. Supports a specific statistic attributed to the GSMA: 68% of rural Nigerians lacked smartphones in 2022; rural ownership 32% against 58% urban. The named originating body (GSMA) is the strongest identification clue the project holds. | Title, publication (the citation reads as journalism or a market-analysis report rather than a journal article), publisher, date, URL. **REQUIRES EXTERNAL SOURCE VERIFICATION** — and the underlying GSMA figures should be verified at source, since a secondary report of a statistic is being used to carry it. |
| Giua, Materia, & Camanzi (2020) | §1.2 (only use) | Three authors, surnames Giua, Materia, Camanzi; year 2020. Supports: commercial FMIS/ERP complexity, absent data standards and prohibitive cost excluding small and medium-scale farmers. | Title, journal or publisher, volume/issue, pages, DOI/URL, author initials. **REQUIRES EXTERNAL SOURCE VERIFICATION** |
| Poppe, Vrolijk, & Bosloper (2023) | §1.2 (first use); §1.4; §2.4.2; §2.7; §5.2.1; §5.3.1 | Three authors, surnames Poppe, Vrolijk, Bosloper; year 2023. Supports: Farm Financial Accounts kept separately from operational and bioprocess records, causing duplicated entry and administrative fatigue. This is the load-bearing citation for the paired-write argument in §5.3.1. | Title, journal or publisher, volume/issue, pages, DOI/URL, author initials. **REQUIRES EXTERNAL SOURCE VERIFICATION** |
| Gebresenbet et al. (2023) | §1.2 (first use); §1.3; §1.4; §2.5 | Year 2023, first author surname Gebresenbet. Supports: siloed metrics preventing farmers correlating mechanisation and biological inputs with financial profitability. | **The document never gives the full author list** — every one of the four occurrences is abbreviated to "et al.", so the co-authors cannot be recovered from the project at all. Title, journal or publisher, volume/issue, pages, DOI/URL, all initials. **REQUIRES EXTERNAL SOURCE VERIFICATION** |
| Husemann & Novkovic (2012) | §1.4 (only use) | Two authors, surnames Husemann and Novkovic; year 2012. Supports: the transition from intuition-based strategy to evidence-based precision farming. | Title, journal or publisher, volume/issue, pages, DOI/URL, author initials. **REQUIRES EXTERNAL SOURCE VERIFICATION** |

Every earlier draft in the project was searched for these entries (`AgriProfit_Chapters_1-3.docx`, `AgriProfit_Chapters_1-3_corrected.docx`, `Thesis_Ch1-3.docx`, `docs/print/Thesis_Ch1-3.docx`, `AgriProfit_Evaluation_Pack.docx`, `AgriProfit_Viva_Prep.docx`, and every tracked markdown file). **None contains bibliographic detail for any of the twelve** — each carries only the same author-note listing them. No entry was therefore constructed, and no placeholder that could be mistaken for a real reference was written into the document.

### 10.3 Reference-count and recency requirement

Guideline §2.4: "Reference list shouldn't be less than 15 for implementation based projects … 70% of the reference list should be RECENT (i.e. within the last five years)."

Present state: **9 entries**, of which 2 are 2021 or later — **22%**.

| Scenario | Total entries | Recent (2021–2026) | % recent | Meets ≥15? | Meets 70%? |
|---|---|---|---|---|---|
| As it stands | 9 | 2 | 22% | ✗ | ✗ |
| After adding the 12 missing works | 21 | 11 | 52% | ✓ | ✗ |
| Minimum compliant | **34** | **24** | **70.6%** | ✓ | ✓ |

The twelve missing works carry years 2012, 2019, 2020, 2021, 2022, 2022, 2023, 2023, 2023, 2023, 2024, 2024 — nine of them recent, three not. Adding them satisfies the count but not the recency ratio, because the existing list is weighted towards foundational method sources (Nielsen & Molich 1990, Nielsen 1994, Brooke 1996) that cannot and should not be dropped.

**Therefore: 12 entries must be completed, and a further 13 legitimate sources from 2021 or later must be added — 25 new entries, for a total of 34.** On the stricter reading of "the last five years" as 2022–2026, 16 further recent sources are needed, for a total of 37.

These must come from real literature relevant to the argument the thesis actually makes — offline-first and low-bandwidth agricultural software, farm financial record-keeping and enterprise budgeting, thin-layer drying kinetics, FMIS adoption in sub-Saharan Africa, and yield prediction for smallholder contexts. Two are already named as required by the document itself, in §4.14: an agricultural-economics or extension enterprise-budget source for the cost-behaviour taxonomy, and post-harvest handling guidance for the safe-storage moisture ceilings.

**This task was not attempted in this pass and remains outstanding.** No external bibliographic lookup was performed, and padding the list to reach 34 with sources not actually read would be worse than the present shortfall.

### 10.4 Chapter Two Guideline Gap Analysis

The guideline's Chapter Two requirement is stated once, on p. 15, and it prescribes **no subsection structure**: "This is a documentation of the related works done by others, its merits and limitations, i.e., critical analysis of reported research on the problem or topic under review. The review may be placed under sub-headings for clarity and more critical analysis. In principle, this section should provide an account of project works done by others on the topic. Implicitly, it has to be a critique of the previous research results. It should NOT be less than 15 pages, and 20 pages for implementation based and research based projects respectively."

The length requirement is therefore **strict in form** ("NOT less than 15 pages") and, for this implementation-based project, the figure is **15**. Sub-headings are permitted, not mandated, so the chapter's own 2.1–2.7 structure is not itself a non-conformance. Chapter Two currently runs body pages 8–18 — **11 pages, 2,247 words** — a shortfall of about **4 pages, roughly 820 words** at the chapter's own measured density of ~204 words per double-spaced page.

| # | Required guideline element | Present / Missing | Current location | Recommended action |
|---|---|---|---|---|
| 1 | Not less than 15 pages | **Missing** — 11 pages | §2.1–§2.7, body pp. 8–18 | Expand by ≈820 words. The expansion must come from rows 2–4 below, which are genuine substantive gaps; it must not come from restating what is already there. |
| 2 | "An account of project works done by others on the topic" | **Present but thin** | §2.4.1 Review of Existing Systems — **74 words**, the shortest section in the chapter, and it names no individual system | Name and describe the actual comparators the thesis positions itself against. §1.2 and §5.4 already argue against per-seat, connectivity-assuming commercial FMIS; §2.4.1 is where those systems belong, individually, with what each does and for whom. |
| 3 | "Its merits **and limitations**" | **Missing as a systematic treatment** | §2.4.1 gives one general merit ("flexibility") and three general limitations for unstructured digital methods; no reviewed work is assessed on both | Add a merits-and-limitations treatment per reviewed work or per system class. A comparison table (Table 2.1) of system, target farm scale, connectivity assumption, pricing model, record-to-finance coupling, merits, limitations would satisfy this, would give the chapter its first table, and would be directly supported by material the project already holds in §1.2, §2.4.1, §2.4.2 and §5.4. |
| 4 | "Implicitly, it has to be a **critique** of the previous research results" | **Partly present** | §2.7 Gap in Literature (194 words) states the gap; §2.4.2 reports barriers | Extend §2.7 from a statement of the gap into a critique of why the reviewed work leaves it open — which is the argument §5.4 already makes at length against Fountas et al. (2015), Carrer et al. (2017), Poppe et al. (2023) and Tummers et al. (2019). §5.4 is the source material; the critique belongs in Chapter Two as well. |
| 5 | Sub-headings for clarity | **Present** | §2.1–§2.7, 7 second-level and 12 third-level headings | No action. |
| 6 | Critical analysis of *reported research on the problem under review* | **Present** | §2.1–§2.3, §2.5, §2.6 | No action. §2.6 (Structuring the Decision-Support Prediction Model, 776 words) is the chapter's largest block and reads as design rather than review; it is defensible where it reviews van Klompenburg et al. (2020) and Olisah et al. (2024), but it should not be extended further, since more of it would move the chapter away from the guideline's stated purpose rather than towards it. |

**Chapter Two was not rewritten in this pass.** Rows 2–4 can each be supported by material the project already contains, but writing them requires the twelve missing references to exist first — the comparison table and the critique both turn on works that currently have no bibliographic entry. Expansion should follow reference completion (§10.3), not precede it.

### 10.5 Placeholders and author notes — disposition

Every marker was checked against the rest of the project before being left in place.

| Location | Marker | Information found elsewhere in the project? | Disposition |
|---|---|---|---|
| §4.5.1 | `[INSERT VERIFIED RESULT HERE — figure numbers and captions for the interface screenshots…]` | No. `docs/ch4-data/screenshot-runsheet.md` specifies how to take the screenshots; no screenshot exists, and the document holds **0 inline shapes**. | **Retained.** Cannot be resolved without taking the screenshots. |
| §4.9 | `[INSERT VERIFIED RESULT HERE — RMSE, if computed over the held-out predictions…]` | No — and positively refuted. `docs/STATE_REPORT_2026-08-25.md` records that `model_meta.json` stores `r2` and `mae` only, and that no RMSE is computed, stored or served. | **Retained.** Filling this would require re-running the evaluation, not retrieving a value. |
| §4.10.3 | `[INSERT VERIFIED RESULT HERE — re-run the Lighthouse audit against the frozen tag…]` | No. The retained artefacts are for commit `c16924e`, which precedes the frozen tag, as §4.10.3 itself states. | **Retained.** |
| §4.11.3 | `[CONFIRM — re-check provider pricing pages and restate the retrieval date…]` | No. Prices are list prices captured on a single date; no quotation was obtained. | **Retained.** |
| §4.12, Table 4.24 | "Usability evaluation — to be completed from retained instruments" | No. §4.12 records that the frozen evidence base contains **no completed instrument of any kind** — no scored SUS forms, no heuristic checklists, no session notes, no participant records. | **Retained, and correctly so.** This is the table the abstract was contradicting. Filling any cell without a retained instrument would be fabrication. |
| §4.12, Table 4.25 | "Usability issue log — to be completed" | No. As above. | **Retained.** |
| §4.12 | Indented "Author's note — what must exist before each cell is filled" | n/a — it is instruction, not result | **Retained** until the panel is run; delete it once the tables are filled. It is the procedure that makes Tables 4.24–4.25 fillable, and it is single-spaced and indented as the guideline requires of indented passages. |
| §5.4 | "Note for submission: several works cited in Chapter Two … do not yet carry full entries…" | Superseded in scope only — §10.2 above gives all twelve, not the four named there | **Retained.** Delete together with the reference-list note when §10.3 is completed. |
| End of References | `[Note to author — remove before submission: …]` listing all twelve citations | n/a | **Retained.** This is the working list; §10.2 above is its audited form. |

Nine markers, **nine retained, zero resolved, zero fabricated**. Not one of them could be closed from information the project holds; each requires work in the world — screenshots taken, a metric computed, an audit re-run, prices re-checked, a usability panel actually convened, references actually looked up.

### 10.6 Acknowledgements and List of Figures — the guideline's position

**Both are required regardless of content, so both were preserved.**

- The guideline's Table of Contents template (p. 8) lists ten preliminary pages by name, Acknowledgements and List of Figures among them, with no conditional wording anywhere. Acknowledgements has a dedicated template page (p. 6) carrying a substantive instruction — "include your supervisor, HOD and all academic and non-academic staff of the department" — and margin comment MP21 goes as far as specifying that the word must carry an 'S'. List of Figures has its own template page (p. 11) and its own format comments (MP37, MP38). Nothing makes either page conditional on the body containing figures.
- **Neither was written on the candidate's behalf.** The Acknowledgements page holds a bracketed instruction naming who the guideline requires to be thanked; the List of Figures page holds a bracketed note recording that the document contains no figures.
- A second, larger point about figures: guideline p. 17 states that in Chapter Four "your results are presented for research based project, and **screenshots for implementation based project**." This is an implementation-based project with **zero figures and zero screenshots**, which is a substantive non-conformance in its own right, not merely an empty preliminary page. §4.5.1 already reserves the place for them. See *Blocking issues*.

### 10.7 Final cross-document consistency scan

Run across all 719 paragraphs and all 700 table cells of the edited document.

| Item | Result |
|---|---|
| Project title | 4 occurrences, all "AGRI-PROFIT (A Farm Record and Decision-Support Platform)". Consistent. |
| Degree / programme | "Bachelor of Technology": **0**. Title page (upper case) and certification page now both read Bachelor of Engineering in Agricultural and Bioresources Engineering. Consistent — subject to the B.Eng/B.Tech question in *Requires user verification*. |
| Author surname | **EHRABOR ×2** (cover page, title page) vs **ERHABOR ×2** (declaration, certification). **Unresolved — see below.** |
| Research aim and objectives | Four objectives, numbered i.–iv. in §1.3, addressed in the same order and wording in §3.4, §4.13 (Table 4.26) and §5.2.1–§5.2.4. Consistent. |
| Methodology | Design-and-build with a four-strand evaluation, specified in §3.8 and reported strand-by-strand in §4.3, §4.10, §4.11, §4.12. Abstract now matches. Consistent. |
| Number of tests | 190 backend / 89 frontend throughout (abstract, §4.3.1, §4.15, §5.2). The figures 185 and 92% appear only in §4.3.4, which is the explicit reconciliation of the earlier reported figures, and is labelled as such. Consistent. |
| Test coverage | 93% backend statement coverage throughout; frontend 33.48% stated wherever the backend figure is given at length. Consistent. |
| Evaluation methodology | "Three to five evaluators" appears only in §3.8.4 and §4.12, both describing the *specified* panel, not a panel that sat. Correct as written. |
| Usability / SUS claims | "Five evaluators": **0**. "Score of 60.0": **0**. Every remaining mention of SUS is either method specification (§3.8.4), the statement that the strand is outstanding (§4.12, §4.13, §4.15, §5.2.4, §5.5, §5.8), or future work (§5.7). §4.12's assertion that "no claim of a usability finding, a task-completion measurement, a SUS score or a comparison against paper-based practice appears anywhere in this thesis" is now **true of the whole document**; before this pass it was false of the abstract. |
| Numerical results | ₦35.00 and ₦41.67 (7 and 10 occurrences), 19%, 205 MiB (3), ₦20,950 (5), ₦105 (7), 7,679.9 ms, 116.4 ms, 1,613.8 ms — each agrees wherever it appears. The two apparent "87"/"90%" hits are "4.87 s" and a "90%" yield-scenario row label in Table 4.16, not the withdrawn claims. |
| Tables | 27 tables, 700 cells, numbering 3.1 then 4.1–4.26 with no gap; captions un-bold and above each table; header rows repeat. Unchanged by this pass. |
| Conclusions and recommendations | §5.8 and §5.7 state the usability strand outstanding and Objective 4 partly met; the abstract now says the same. No contradiction found between abstract, results, discussion, conclusion and recommendations. |
| References | 9 entries, alphabetical, APA 7th, no duplicates. In-text/list mismatch is the 12 of §10.2 — unchanged and unresolved. |
| Chapter numbering | One → Five then References; headings 1.1–1.5, 2.1–2.7, 3.1–3.9, 4.1–4.15, 5.1–5.8; 117 second- and third-level headings in sequence, 0 errors. |

### 10.8 Structural validation of the output

| Check | Result |
|---|---|
| Document opens | **Yes** — opened in Microsoft Word, fields and Table of Contents updated, repaginated, saved, and exported to PDF without error |
| Page count | 115 pages, unchanged from the pre-remediation document |
| Word count | 26,418 (was 26,481) — consistent with a 182-word reduction in the abstract offset by regenerated field content |
| Paragraphs | 719 (was 721) — exactly the two deleted abstract paragraphs |
| Content accidentally deleted | **None.** Every paragraph outside the abstract is byte-identical to the pre-edit document apart from the single certification sentence |
| Tables | 27 tables / 700 cells, unchanged; no table corrupted |
| Figures | 0 inline shapes before and after — none to corrupt |
| Numbering regressions | None. 117 headings in sequence, table numbering 3.1 / 4.1–4.26 with no gap, preliminaries i–xvii roman, body 1–98 arabic, both bottom-centre |
| Formatting regressions | None. A4; margins 3.5 cm left, 2.5 cm elsewhere; **0 non-Times-New-Roman runs**; 12 pt body, 14 pt bold centred chapter headings; double spacing with the abstract, the §4.12 indented note and the code block at 1.0; block paragraphs, justified; 0 blank pages |
| Unsupported research results introduced | **None.** Every figure in the new abstract is quoted from a numbered Chapter Four section, listed in §10.1 |
| Fabricated references added | **None.** The reference list is untouched at 9 entries |
| Output file readable | **Yes** — `Thesis_Ch1-5.docx`, re-opened and re-parsed after saving |

---

## Final Submission Readiness

### RESOLVED

1. **Certification page degree — the Computer Science reference is gone.** Was: "…award of the degree of Bachelor of Technology in Computer Science of the Federal University of Technology, Minna." Now: "…award of the degree of Bachelor of Engineering in Agricultural and Bioresources Engineering of the Federal University of Technology, Minna." Evidence: the title page of the same document, plus cover page and title page department lines. One residual question about degree style is listed under *Requires user verification*.

2. **The abstract no longer contradicts Chapter Four.** The withdrawn claims — 87 tests, 90% coverage, five evaluators, a mean SUS of 60.0, and an LCP figure that merged first paint with largest contentful paint — are replaced by the figures §4.3.1, §4.10.2, §4.11 and §4.15 actually report. Verified: "87 passing", "90% backend", "Five evaluators" and "score of 60.0" now return **zero matches** across the whole document.

3. **The abstract states the usability position truthfully.** It now reads "The usability evaluation was not conducted and no System Usability Scale score is reported, so that objective is only partly met", which is what §4.12, §4.13, §5.2.4 and §5.5 establish. No SUS score was manufactured; no Chapter Four result was altered to fit.

4. **The abstract now meets the guideline's own format rule** — one paragraph of 249 words against the stated 150–250, single-spaced and not italicised (guideline p. 7). It was previously three paragraphs of 431 words.

5. **The twelve unmatched citations are audited** (§10.2), with corrected chapter locations — first appearance is Chapter One, which §5 of this audit had wrong — full recovered author lists, the claim each supports, and a per-entry statement of exactly what is missing.

6. **Chapter Two's shortfall is quantified against the guideline** (§10.4): 11 pages against a strict 15, a gap of ≈820 words, with the four substantive gaps identified and each mapped to project material that can support it.

7. **All nine placeholders and author notes are accounted for** (§10.5), each checked against the rest of the project before being left in place.

8. **Acknowledgements and List of Figures are settled** (§10.6): the guideline requires both unconditionally, so both are preserved.

9. **Formatting is intact** (§10.8). Nothing validated by the merge audit regressed.

### REQUIRES USER VERIFICATION

1. **Author surname — EHRABOR or ERHABOR.**
   - *Location:* cover page and title page read **EHRABOR ISRAEL ISIMA**; declaration and certification read **ERHABOR, ISRAEL ISIMA**. Two occurrences each.
   - *Why it is a problem:* the candidate's name is the identity the degree is awarded against. A thesis that spells its author's surname two ways is an administrative failure independent of its academic content, and an examiner will see it on the first two pages.
   - *Evidence available:* none that decides it. Both source documents (`Thesis_Ch1-3.docx` and its earlier save in `docs/print/`) carry the same 2–2 split. Every other draft in the project inherits it. The document metadata author fields read "Un-named" and "python-docx". The git author is "DEWA_EMPR". No project file, file name, matriculation record or commit resolves the spelling.
   - *Action required:* confirm the spelling against your matriculation record or student ID, then apply it to all four locations. **Do not let a tool pick.** Note the guideline's format is `SURNAME, OtherNames` — the cover and title pages currently omit the comma, which should be added at the same time.

2. **Degree style — Bachelor of Engineering or Bachelor of Technology.**
   - *Location:* certification page (now B.Eng) and title page (B.Eng, upper case).
   - *Current state:* consistent within the document, at Bachelor of Engineering in Agricultural and Bioresources Engineering.
   - *Why it is a problem:* the departmental guideline this document is formatted against is titled "Updated **B.Tech** Final Project Guideline for 2025_2026" and its certification template reads "Bachelor of Technology in …". If the School of Infrastructure Process Engineering and Technology awards B.Tech, both pages are now wrong in the same way.
   - *Action required:* confirm the awarded degree with the Department. If it is B.Tech, change **both** the certification page and the title page — they must not diverge again.

3. **Supervisor, Head of Department and External Examiner names** are blank on the certification page.
   - *Why it is a problem:* the guideline's template names them; blank signature blocks will be returned.
   - *Action required:* supply the names. None was invented.

4. **Acknowledgements page is a bracketed instruction, not acknowledgements.**
   - *Location:* preliminary page, after Dedication.
   - *Action required:* write it. The guideline requires the supervisor, the HOD and the academic and non-academic staff of the Department of Agricultural and Bioresources Engineering to be named. Nothing was written on your behalf.

5. **Chapter One is missing three sections the guideline's template lists** — 1.2 Motivation of Study, 1.7 Organization of Study, 1.8 Definition of Terms. Unchanged from issue #8 above; confirm with your supervisor whether the department enforces the template. Definition of Terms is the one an examiner is most likely to expect, since the thesis uses paired write, contra entry, partial budget, thin-layer kinetics, service worker and SUS as terms of art.

6. **Chapter Two expansion** (§10.4). The route is identified and the material exists, but writing it is an academic act, not a remediation one, and it depends on the references being completed first.

### REQUIRES EXTERNAL RESEARCH

1. **Twelve reference entries must be found and written** (§10.2). Every one is marked REQUIRES EXTERNAL SOURCE VERIFICATION: the project contains no bibliographic detail for any of them beyond author surnames and year, recovered from the in-text citations themselves. **Gebresenbet et al. (2023) is the hardest** — the document never gives its full author list, so the co-authors cannot be recovered from the project at all.

2. **Thirteen further sources from 2021 or later must be added** to satisfy the 70% recency rule (§10.3): 12 completions plus 13 new gives 34 entries with 24 recent, or 70.6%. On the stricter 2022–2026 reading, 16 are needed for a total of 37. The count rule alone (≥15) is satisfied by the twelve completions; **the recency rule is the binding constraint and is the one currently failed most badly, at 22%.**

3. **Two citations the implementation itself still needs**, recorded in §4.14 and not yet in the reference list: an agricultural-economics or extension enterprise-budget source for the cost-behaviour taxonomy, and post-harvest handling guidance for the safe-storage moisture ceilings. Both count towards the totals above.

4. **The GSMA statistic behind Jaiyeola (2023)** — 68% of rural Nigerians without smartphones in 2022, 32% rural against 58% urban ownership — should be verified at its origin, since a secondary report is currently carrying a specific quantitative claim in §1.1 and §1.5.

**No external bibliographic lookup was performed in this pass, and no entry was constructed.** This task remains outstanding in full.

### BLOCKING ISSUES

Resolve before submission.

1. **The reference list fails the guideline outright.** 9 entries against a minimum of 15; 22% recent against a required 70%; and 12 in-text citations with no entry at all. *Why blocking:* a citation with no reference entry is unverifiable by an examiner, and twelve of them across Chapters One, Two and Five is a systematic failure rather than an oversight. *Action:* §10.2 and §10.3.

2. **Chapter Two is 11 pages against a strict "NOT less than 15".** *Why blocking:* the guideline states it as a floor, not a target. *Action:* §10.4, after the references exist.

3. **The document contains no figures and no screenshots.** *Why blocking:* guideline p. 17 requires screenshots in Chapter Four for an implementation-based project, and this is one. §4.5.1 reserves the place and holds a placeholder describing exactly how they must be captured — against the frozen tag, signed in as farm 26, following `docs/ch4-data/screenshot-runsheet.md`, and never using a farm-list view to establish identity, because two farms share the name "Demo Farm". *Action:* take the screenshots, caption them below the image as Figure 4.1, Figure 4.2 …, and the List of Figures will populate on the next field update.

4. **Nine placeholders and author notes are still in the document** (§10.5), including two "to be completed" tables. *Why blocking:* a bracketed note to the author inside a submitted thesis reads as an unfinished draft. *Action:* each requires real work, not deletion — deleting Table 4.24's heading without running the panel would remove the honest record of a gap that Chapter Five relies on.

5. **The usability strand of the specified evaluation was never run**, so Objective 4 is met in part only. *Why blocking, or at least a decision for your supervisor:* §5.2.4 states it plainly — "the platform's central claim is that it reduces cognitive load for a user operating under bounded rationality, and that claim is precisely the one no strand of the completed evaluation touches." *Action:* §5.7(a) already identifies this as the highest-value remaining evidence in the project — three to five evaluators, the existing instrument pack, instruments retained as scans. This is now recorded consistently and honestly everywhere in the document, including the abstract, so it is a **completeness** problem rather than an **integrity** one.

6. **The author's surname is spelled two ways on the first four pages** (see *Requires user verification* 1). *Why blocking:* it is on the cover.

### Status

**Not submission-ready.** The academic-integrity contradiction that motivated this pass — an abstract claiming a usability evaluation that Chapter Four states was never conducted, alongside superseded test and coverage figures — **is resolved**, and no fabricated result, reference or acknowledgement was introduced anywhere. What remains blocking is unfinished work rather than untruthful work: references to find, a chapter to lengthen, screenshots to take, a usability panel to run, and a surname to confirm.
