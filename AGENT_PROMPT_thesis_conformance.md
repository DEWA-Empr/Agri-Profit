# Agent prompts — Thesis conformance to the departmental guideline

Paste these **one at a time**, in order. Wait for the agent to report before sending the next. The gating is deliberate: several phases can silently destroy evidence, and a checkpoint is cheaper than a rollback.

**Before you start:** put `Updated_B_Tech_Final_Project_Guideline_for_2025_2026_v1.pdf` and every chapter file in the repo, and save this file alongside them.

**Governing document.** The Department of Computer Science, School of Information and Communication Technology, Federal University of Technology, Minna guideline. Where any project document conflicts with it, the guideline wins.

**Commits.** One per phase, with a real message. Structural edits to a thesis are exactly the kind of change you will want to bisect.

---

## Prompt 0 — Session setup

```
We are conforming a completed B.Tech project document to the departmental
guideline. The guideline PDF is the governing document for structure,
formatting, language and references. Read it in full before doing anything
else.

The project is AGRI-PROFIT, an offline-first farm record management and
decision-support platform, submitted to the Department of Computer Science,
Federal University of Technology, Minna.

Rules for this entire session:

1. Work in phases. Stop at the end of each, report, and wait for me. Do not
   run ahead.
2. Never invent a result. Every number in Chapter Four is measured, computed
   from data the system holds, or derived arithmetically from one of those.
   If a value is missing, it stays missing. Fabricating one is misconduct and
   ends the project, not just the session.
3. Every block marked TO COMPLETE is preserved verbatim and is never resolved
   by invention. They are instructions to the author, not gaps for you to fill.
4. Do not delete a limitation, a discarded measurement, an unflattering figure,
   or an admission of a gap. These are load-bearing. If conformance appears to
   require removing one, stop and tell me.
5. Where the guideline and an existing chapter conflict, the guideline wins —
   except on rules 2, 3 and 4, which override everything.
6. Report every change as a before/after pair. I need to be able to veto
   individually.
7. Create a branch before your first edit: git checkout -b docs/guideline-conformance
8. Commit at the end of each phase.

Confirm you have read the guideline and state the eight rules back in one line
each. Then stop.
```

---

## Prompt 1 — Phase 0, conformance audit (read only)

```
Phase 0. Read only — change nothing.

Read every chapter file, plus the consistency register, the bioprocess session
addendum, the hosting-cost analysis, the performance benchmarking report, and
CONTEXT.md, LIMITATIONS.md, PROGRESS.md and the PRD.

Then produce a conformance gap table with one row per violation:
  file | location | guideline rule violated | current text | severity

Audit against, at minimum:

STRUCTURE
  - Preliminary pages present and in order: Cover Page, Title Page,
    Declaration, Certification, Dedication, Acknowledgements, Abstract, Table
    of Contents, List of Tables, List of Figures.
  - Chapter One section order and numbering: 1.1 Background to the Study,
    1.2 Motivation of Study, 1.3 Statement of Problem, 1.4 Aim and Objectives
    of Study, 1.5 Significance of Study, 1.6 Scope and Limitation of Study,
    1.7 Organization of Study, 1.8 Definition of Terms.
  - Chapter Two is not less than 15 pages (implementation-based project).
  - Chapter Three answers WHEN, WHERE, WHAT materials and techniques, HOW, and
    WHAT procedures.
  - Chapter Four contains discussion of each result, and screenshots.
  - Chapter Five is 5.1 Summary, 5.2 Conclusion, 5.3 Recommendations, nothing
    else.
  - Whole document is not less than 50 pages, Chapters One to Five.

LANGUAGE
  - UK English spelling throughout.
  - No first-person pronouns anywhere in chapter text. Reported speech or
    "the author".
  - No contractions. No "etc.", "and so on", or any open-ended list.
  - Organisations and institutions written in full at first mention with the
    abbreviation in brackets, abbreviation alone thereafter.
  - Non-English words italicised and defined under Definition of Terms.
  - No single-sentence paragraphs.

NUMBERS AND DATES
  - Numbers under ten in words, except units of measurement.
  - Comma in numerals over 1,000.
  - "first", "second" — not "1st", "2nd".
  - Dates in the form 18th August, 2026.
  - Decades as 1990s, no apostrophe.
  - Percentage sign not mixed with spelt-out figures.
  - Units spelt out when alone in text, abbreviated when qualified by a number
    and in tables and figures. Metric units.

TABLES, FIGURES, PLATES
  - Tables numbered per chapter (Table 4.1, Table 4.2), title unbold and above
    the table, content centralised, gridlines, font not below 10 point, and
    referenced in the text by number.
  - Figures numbered per chapter (Figure 4.1), caption below and centred, the
    word Figure written in full in text, no captions beginning "Graph
    showing" or similar.
  - Photographs are Plates, roman numerals.

LISTS
  - First level alphabets (a), except project objectives which use roman
    numerals (i). Second level roman numerals. No third level — use
    subheadings.

REFERENCES
  - APA 7th edition, in-text and reference list.
  - Not fewer than 15 entries (implementation-based).
  - 70% within the last five years.
  - Every in-text citation has a reference entry, and vice versa.

Also report, separately:
  8. Every cross-reference in Chapters Two to Five that points at a Chapter One
     section number, with its current target.
  9. Every table in Chapter Four that currently has no number and no title.
  10. Every location where a component is justified by appeal to agricultural
      or bio-process engineering as a discipline rather than as software
      engineering.
  11. Anything in these instructions that will not work given what you found.
      Be specific. This is the most important answer.

Do not begin editing. Stop after reporting.
```

---

## Prompt 2 — Phase 1, Chapter One restructure and the renumbering map

```
Phase 1. Chapter One, and every cross-reference to it.

The guideline's Chapter One structure is fixed. Remap the existing content:

  1.1 Background to the Study        <- existing 1.1
  1.2 Motivation of Study            <- NEW. Draft from the existing background
                                        and problem statement; the 68% rural
                                        smartphone gap and the per-seat
                                        licensing exclusion belong here.
  1.3 Statement of Problem           <- existing statement of problem
  1.4 Aim and Objectives of Study    <- existing 1.3. Objectives as roman
                                        numerals (i), (ii), (iii), (iv).
  1.5 Significance of Study          <- NEW or relocated. Must answer who
                                        benefits and what each benefits.
  1.6 Scope and Limitation of Study  <- existing 1.5
  1.7 Organization of Study          <- NEW. One paragraph per chapter.
  1.8 Definition of Terms            <- NEW. Source it from CONTEXT.md, which
                                        is already a disciplined glossary.
                                        Include Drying Run, Moisture Content,
                                        Marketable Mass, Process Loss,
                                        Reversal, Activity Category, and every
                                        abbreviation used in the document.

Two corrections that must land in this phase, because they are wrong on the
facts and Chapter One is read most closely:

  - The forecast model is described as "lightweight statistical regression".
    It is a Random Forest — a tree-based ensemble. Correct it to "a lightweight
    tree-based ensemble model rather than advanced deep-learning algorithms".
  - Chapter 1.5 (now 1.6) should no longer imply that bioprocess monitoring is
    out of scope. Post-harvest drying is implemented, measured and reported in
    Chapter Four.

Then update EVERY cross-reference in Chapters Two, Three, Four and Five that
points at an old Chapter One section number. Objectives move from 1.3 to 1.4;
scope and limitations move from 1.5 to 1.6.

Output a remap table: file | line | old reference | new reference. I will check
this table against your Phase 0 answer 8 before you continue.

Commit. Stop and show me the remap table and the Chapter One diff.
```

---

## Prompt 3 — Phase 2, the disciplinary framing sweep

```
Phase 2. Framing only. Change no numbers, no results, no structure.

This project is submitted to the Department of Computer Science. Several
passages currently justify components by appeal to agricultural or bio-process
engineering as a discipline. The clearest is in 4.5.2: the drying module is
described as "what makes this an agricultural and bio-process engineering
artefact rather than a bookkeeping application". Under a Computer Science
submission that sentence defends against a charge nobody is making.

Rewrite each such passage so the claim being made is a software engineering
one. The available claims are:

  - domain modelling: a physical process represented as a validated schema at
    the API edge, with bounds enforced rather than assumed
  - derived-on-read computation: no stale denormalised values, every metric
    recomputable from the stored record
  - invariant preservation: the paired write, so a physical process posts its
    cost through the same path as any other activity
  - separation of pure computation from persistence: bioprocess_service.py has
    no database access, which is why it can be verified by hand-calculated
    fixture at all
  - verification by designed fixture: parameters known in advance and
    recovered exactly, which is a testing argument before it is an
    agronomy one

THE AGRONOMIC CONTENT STAYS. The thin-layer kinetics, the mass balance, the
fixtures, the moisture conversions, the safe-storage thresholds — all of it
remains, in full, with its numbers unchanged. What changes is what the
surrounding prose claims those things prove. You are re-aiming an argument,
not deleting evidence.

Check at minimum:
  - 4.5.2, the closing sentence and the paragraph containing it
  - 4.9, the Objective 3 row and its wording
  - 4.10, wherever the moisture-to-price chain is restated
  - Chapter One background, significance, and the aim
  - Chapter Three, the bioprocess module rationale
  - anything ADR-0001 language was propagated into

Report every passage as a before/after pair in a table. Change nothing else.
Commit. Stop.
```

---

## Prompt 4 — Phase 3, fold discussion into Chapter Four

```
Phase 3. Chapter Four structure.

The guideline states that in Chapter Four each result is expected to be
extensively discussed. Chapter Four currently defers discussion to Chapter
Five, and Chapter Five under this guideline has no room for it. Invert that
contract.

For each strand — 4.2 functional verification, 4.3 decision-support output,
4.4 the forecast model, 4.5 post-harvest drying, 4.6 performance, 4.7 cost,
4.8 usability — the section reports the result and then discusses it in place:
what it means, why it came out that way, what it does and does not support,
and how it bears on the problem stated in Chapter One.

Much of this discussion already exists in the chapter as inline commentary.
Where it does, promote and consolidate it rather than writing new prose. The
interpretation of the warm-cache result in 4.6.2, the synthetic-data caveat in
4.4, and the two patterns named at the end of 4.8.4 are already discussion and
should be recognised as such.

Specific edits:
  - 4.1: delete the sentence deferring discussion and recommendations to
    Chapter Five. Replace it with a statement that each strand is reported and
    discussed in turn.
  - 4.10: remove the closing sentence that hands interpretation to Chapter
    Five. The chapter now closes on its own summary.
  - Add a new section 4.11, Limitations of the Evaluation, gathering the
    limitations currently scattered across strands and currently deferred to
    Chapter Five: simulated throttling on localhost, reasoned rather than
    load-tested tenancy figures, a single evaluator against a specified panel
    of three to five, the two untested behaviours of 4.2.3, synthetic training
    data, the part-measured hosting footprint, and the read cache that is not
    invalidated by mutation.

Note on ordering: 4.11 sits after 4.10 Summary because that is where I want
it. If you judge that the summary reads as a chapter close and limitations
after it are orphaned, say so and propose the alternative — do not reorder on
your own initiative.

Every existing TO COMPLETE block survives this phase untouched and in place.

Commit. Stop and report the new section outline with a one-line note on where
each piece of discussion came from.
```

---

## Prompt 5 — Phase 4, tables, figures and plates

```
Phase 4. Presentation of tables and figures across all chapters.

TABLES
Every table gets a number and a self-explanatory title, unbold, placed above
the table close to its body. Number consecutively within the chapter: Table
4.1, Table 4.2. Content centralised, gridlines on, font not below 10 point.
Every table must be referenced in the text by its number — if a table is never
referenced, add the reference; do not delete the table.

Chapter Four currently has approximately a dozen unnumbered, untitled tables.
Number them in order of appearance. Suggested titles are yours to draft, but
each must be readable without the surrounding text, per the guideline.

Any table too long for the body goes to the Appendix with a pointer left in
place.

FIGURES
The guideline expects screenshots for an implementation-based project, and
Chapter Four currently contains none. You cannot take screenshots. Therefore:

For each figure the chapter needs, insert a numbered placeholder with a
caption below it, centred, and an adjacent capture instruction addressed to
me. Do not fabricate an image, and do not describe an interface you have not
seen as though it were pictured.

At minimum, propose placeholders for:
  - the decision-support view showing per-crop gross margin and ranking
  - the unit-cost display showing both wet and marketable bases
  - the reversal control and its confirmation dialogue
  - the pending-sync indicator during the offline task
  - the model-information panel in its untrained and trained states
  - the drying-run result panel, if the sub-form is built
  - the Lighthouse warm-versus-cold comparison

Captions go below, centred, and must not begin with "Screenshot showing" or
any equivalent. Write Figure in full when referencing in text.

PLATES
Any photograph — for instance a scanned completed SUS instrument in the
Appendix — is a Plate with a roman numeral.

Then build List of Tables and List of Figures from what now exists.

Commit. Stop and report the full table and figure inventory with numbers.
```

---

## Prompt 6 — Phase 5, Chapter Five to template shape

```
Phase 5. Chapter Five.

The guideline permits exactly three sections:

  5.1 Summary — restatement of the problem, and description of the procedures
      used. Not a restatement of results.
  5.2 Conclusion — conclude the objectives achieved. One passage per
      objective, stating what was achieved and, where an objective was
      partially met, saying so plainly. Objective 4 in particular: the
      evaluation was conducted at a reduced scale and that is part of the
      conclusion, not a footnote to it.
  5.3 Recommendations — recommendations arising from the study, then
      suggestions for further studies.

Everything currently drafted for Chapter Five that is discussion of results
has moved to Chapter Four in Phase 3, and everything that is a limitation has
moved to 4.11. What remains here is summary, conclusion and recommendation
only.

Recommendations should be drawn from what the evaluation actually found, not
from a generic list. The candidates already evidenced in the project include:
route-level code-splitting as a first-visit optimisation for the worst-served
users specifically; externalising the model artefact for availability rather
than for cost; identity-scoping the offline write queue; a discard path for
permanently-failed queued records; extending the precache glob to the manifest
icon; server-side token revocation and a password-reset flow; validation
against real yield data before any predictive claim is made.

Suggestions for further studies should include the field evaluation this
project could not conduct, and proportional cost attribution where only part
of a harvest is dried.

Commit. Stop and report.
```

---

## Prompt 7 — Phase 6, language and mechanics sweep

```
Phase 6. Mechanics across all five chapters and the preliminary pages.

Apply every rule from the LANGUAGE and NUMBERS AND DATES sections of the
Phase 0 audit. Work file by file and report a count of changes per rule so I
can see where the document was weakest.

Particular attention:
  - First-person pronouns. Chapter text uses reported speech or "the author".
    The TO COMPLETE blocks are addressed to me and are exempt — leave their
    wording alone, but ensure each is visibly marked as an editorial note that
    must not survive into the submitted file.
  - Dates. The document uses "18 August 2026" throughout. The guideline form
    is "18th August, 2026".
  - Numbers under ten in words, except units of measurement. "Five fixtures"
    is correct; "5 kg" is correct; "7 / 7" inside a table is acceptable as
    tabular data but the surrounding text must say seven.
  - UK English. Check -ise endings, "programme", "centre", "colour",
    "modelling", "labelled".
  - No single-sentence paragraphs.
  - Every abbreviation expanded at first mention.

Do not change a number's value while changing its presentation. If a
presentation rule appears to require altering a measured figure, stop.

Commit. Stop and report the per-rule change counts.
```

---

## Prompt 8 — Phase 7, references

```
Phase 7. References and citations.

Requirements: APA 7th edition; not fewer than 15 entries; 70% published within
the last five years; every in-text citation has a reference entry and every
entry is cited.

Known debt, from the consistency register:
  - The reference list carries nine entries against roughly twenty-one works
    cited in text.
  - Twelve citations need full entries: Abbasi, Martinez & Ahmad (2022);
    Abiri et al. (2023); Basir et al. (2024); Dayioglu & Turker (2021);
    Gebresenbet et al. (2023); Giua, Materia & Camanzi (2020); Husemann &
    Novkovic (2012); Jaiyeola (2023); Javaid et al. (2022); Nirosha (2024);
    Poppe, Vrolijk & Bosloper (2023); Tummers, Kassahun & Tekinerdogan (2019).
  - Uncited empirical claims in Chapter Two: the approximately 17% adoption-
    odds figure; the three phases of Nigerian precision agriculture; the FAO
    Digital Village Initiative; bounded rationality and satisficing; the
    opening paragraph of 2.1.1.
  - A bracketed note-to-author sits in Chapter Two and must not reach the
    submitted file.
  - The safe-storage moisture thresholds in the bioprocess module carry a
    TODO(cite) and need a real source — FAO post-harvest handling guidance, or
    an IITA or NSPRI publication.
  - The performance report cites Nigerian median mobile download speed via a
    secondary report; cite the Ookla Global Index directly.

For each uncited claim, do ONE of these and say which:
  (a) supply a real, verifiable source and the APA entry
  (b) flag it for me to source, with the specific claim quoted
  (c) recommend deletion, with a note on what the surrounding argument loses

Never invent a citation. A plausible-looking reference to a paper that does
not exist is worse than an uncited claim, because it is discoverable and it is
misconduct.

Report the reference list with a recency count: how many of the total are
within five years, and whether that clears 70%.

Commit. Stop.
```

---

## Prompt 9 — Final compliance check

```
Final check. Produce a compliance table with one row per guideline rule, each
marked pass or fail with evidence. Cover:

STRUCTURE
  - preliminary pages present and ordered
  - Chapter One sections 1.1 to 1.8 in guideline order
  - Chapter Two page count (paste it)
  - Chapter Three answers when, where, what, how, what procedures
  - Chapter Four discusses each result; figures present or placeheld
  - Chapter Five is 5.1, 5.2, 5.3 and nothing else
  - total page count, Chapters One to Five (paste it)

PRESENTATION
  - every table numbered, titled above, unbold, gridlined, centred, referenced
  - every figure numbered, captioned below, centred, referenced in full
  - List of Tables and List of Figures build correctly
  - Times New Roman; 12pt body; 14pt chapter number and title; double spacing;
    abstract single-spaced and not italicised; block paragraphing; margins
    3.5cm left and 2.5cm elsewhere

LANGUAGE
  - zero first-person pronouns in chapter text (paste your search result)
  - zero contractions, zero "etc." (paste)
  - UK English (paste your check)
  - zero single-sentence paragraphs

REFERENCES
  - entry count, recency percentage, orphan citations, orphan entries

INTEGRITY — report each explicitly
  - every TO COMPLETE block still present, verbatim (list them)
  - no measured figure altered anywhere (paste git diff filtered to numerals
    in Chapter Four)
  - the single evaluator is still reported as one evaluator
  - the SUS score is still 60.0 and still characterised as below the benchmark
  - both discarded measurements are still reported
  - the two untested behaviours of 4.2.3 are still declared
  - no citation was invented

Then paste git log --oneline for this branch, and list every item you flagged
for me rather than resolving.
```

---

## Rescue prompts

**If the agent proposes filling a TO COMPLETE block:**

```
Stop. Those blocks mark values that do not yet exist. Filling one with a
plausible value is fabrication, and every figure in Chapter Four is traceable
to an artifact an examiner can request. Restore the block verbatim and tell me
what you were about to write and why you thought it was available.
```

**If conformance appears to require deleting a limitation or an unflattering result:**

```
Stop. The chapter's argument depends on reporting what was found, including
the single evaluator, the below-benchmark SUS score, the performance that did
not improve, and the two discarded measurements. If a guideline rule genuinely
conflicts with reporting one of these, quote the rule and the passage and wait.
```

**If the framing sweep starts removing agronomic content:**

```
Stop. Phase 2 re-aims arguments; it does not remove evidence. The drying
kinetics, the mass balance, the fixtures and the moisture figures all stay.
List everything you removed and restore it, then show me only the sentences
that make disciplinary claims.
```

**If a cross-reference remap looks incomplete:**

```
Search every file for references to Chapter One section numbers, including
prose forms — "Section 1.3", "Ch 1.5", "the objectives set out in Chapter
One", "Chapter 1.5". Paste every hit with its file and line, then diff that
list against your Phase 1 remap table and report what was missed.
```
