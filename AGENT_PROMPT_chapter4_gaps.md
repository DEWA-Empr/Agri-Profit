# Agent prompt — close the Chapter Four gaps and produce a data pack

Purpose: turn every `TO COMPLETE` block in `AgriProfit_Chapter4.md` into either a real measured figure or an explicit, defensible absence. Output is one file I can hand back for the chapter to be written.

Paste one prompt at a time. Wait for the report between each.

**Two of the gaps are not in this file.** Evaluators 2 and 3, and the undiagnosed row 10, cannot be closed by an agent. See the final section.

---

## Prompt 0 — Setup

```
We are closing the outstanding data gaps in Chapter Four of the
AGRI-PROFIT dissertation. Read AgriProfit_Chapter4.md in full first,
paying particular attention to every block marked TO COMPLETE.

Rules for this session:

1. Work in phases. Stop at the end of each, report, and wait.
2. Do not edit AgriProfit_Chapter4.md. You produce data; I write prose.
3. Never choose values to produce a tidy result. Whatever the seed
   produces and the endpoint returns is what gets recorded, including
   awkward rounding and unflattering numbers.
4. Every figure you report must be copied verbatim from a command
   output, an endpoint response or a file. If you find yourself typing a
   number from memory or from the chapter, stop.
5. No new dependency. No Alembic migration unless a phase explicitly
   calls for one, in which case stop and ask first.
6. Branch before the first edit, and commit at the end of each phase.

Confirm you have read the chapter, list every TO COMPLETE block you
found with its section number, and state which ones you believe are
executable by you and which are not. Then stop.
```

---

## Prompt 1 — Phase 0, reconnaissance (read only)

```
Phase 0. Read only. Change nothing.

Report as short numbered answers:

1. backend/scripts/seed_bioprocess_demo.py — paste it. State exactly
   what it creates, how idempotency is keyed, and whether re-running is
   safe.
2. The DSS per-crop endpoint: its route, its response schema, and the
   exact field names for revenue, expenses, gross margin, rank, unit
   cost (both bases) and break-even. Paste the schema.
3. The break-even computation in dss_service.py. Paste the function.
   State its unit, its rounding behaviour, and each of the four null
   cases as implemented rather than as documented.
4. Whether a drying-parameters sub-form exists in the frontend. If not,
   state what the log-entry screen currently does when Bioprocess is
   selected, and note that Chapter Four Section 4.8.4 row 4 records that
   the option was REMOVED from the form after it produced an
   unsatisfiable queued record. Do not re-add it without telling me.
5. Whether tests exist for (a) the model-information endpoint's
   untrained state and (b) the offline queue flush. Chapter Four
   Section 4.2.3 claims neither exists. Verify.
6. Current test count and coverage. Run pytest --cov and paste the tail
   verbatim, plus every module line below 100%.
7. Every frontend route and screen that currently renders without error,
   as a list. I need this to plan screenshots.

Stop and report. Do not implement.
```

---

## Prompt 2 — Phase 1, extend the seed script

```
Phase 1. Extend backend/scripts/seed_bioprocess_demo.py.

Leave every existing maize record untouched. The unit-cost figures in
Chapter Four Section 4.3.2 depend on maize being exactly 3,500 naira of
expenses against 100 kg harvested, dried to 84 kg, sold for 45,000
naira. If any of those move, the chapter is wrong.

Add two crops:

  - One profitable crop with a genuine gross margin. Give it recorded
    inputs and a recorded sale. Do not give it a drying run — Chapter
    Four needs a crop without one to demonstrate the fallback path.
  - One loss-making crop: recorded input costs, no sale recorded. This
    is the realistic case a farmer most needs to see, and it exercises
    the negative-margin display and the break-even null path.

Constraints:
  - Amounts must be plausible for a Nigerian smallholder. State your
    source or your reasoning for each figure in the commit message.
  - Do not tune the amounts so that the ranking comes out neatly or so
    that the margins are round numbers.
  - Idempotent by client_id, matching the existing script's approach.
  - Re-running must not duplicate records. Prove it: run it twice and
    paste the record counts after each run.

Commit. Stop and report the script diff and the two record counts.
```

---

## Prompt 3 — Phase 2, capture the DSS output

```
Phase 2. Measurement. Write no application code in this phase.

Reset the database to a known state, run the extended seed, then query
the decision-support endpoints against the seeded farm.

Save the raw responses, unmodified and unformatted beyond
pretty-printing, to docs/ch4-data/ as separate files:

  dss_per_crop.json
  dss_break_even.json
  bioprocess_summary.json
  model_info.json

Then report in the chat, verbatim from those files:

1. The full per-crop table: crop, revenue, expenses, gross margin, rank,
   and both unit-cost figures where present.
2. The break-even value for maize exactly as returned — the number, its
   unit, and its rounding. Chapter Four currently states 7.8 kg from
   3,500 divided by 450. If the endpoint returns something different,
   report the difference and explain why rather than reconciling it.
3. The break-even value for the loss-making crop, which should be null,
   and which of the four null cases fired.
4. Whether any crop returns a null unit cost, and why.
5. Confirmation that maize's figures are unchanged from the chapter.

If any figure surprises you, say so explicitly rather than smoothing it.
An unexpected result here is more useful than a tidy one.

Commit the data files. Stop and report.
```

---

## Prompt 4 — Phase 3, the two missing tests

```
Phase 3. Chapter Four Section 4.2.3 reports two behaviours with no
automated test. Close them if you can.

  a) The model-information endpoint's three display states, with the
     untrained state as the one that matters: an untrained model must be
     reported as untrained, never as zero-valued metrics.
  b) The offline write queue: flushPendingLogs with a mocked client,
     covering the flush on reconnect, the three-strike transition to
     failed, and the retry path.

Test (a) first — it is the smaller. If (b) proves to need more than a
mocked client and a fake timer, stop and tell me rather than building
test scaffolding of unclear value.

Match the existing test style exactly. Do not modify any existing test
to accommodate a new one.

After: run the full suite with coverage. Report the new test count, the
new overall coverage, and every module still below 100%, all pasted
verbatim.

Commit. Stop and report which of the two closed and which did not.
```

---

## Prompt 5 — Phase 4, screenshot preconditions

```
Phase 4. I will take the screenshots; you prepare the states.

For each shot below, tell me: the exact URL, the precondition to reach
it, and any command I must run first. Where a state needs seeding, seed
it. Where a state cannot currently be reached, say so plainly — that
absence is itself a Chapter Four finding.

  4.1  Dashboard, post-cleanup
  4.2  Log-entry form with Bioprocess selected — report what this
       currently shows, given row 4 of 4.8.4
  4.3  Per-crop gross margin and ranking, showing all three seeded crops
       including the loss-making one
  4.4  Unit cost on both bases, maize
  4.5  Break-even rendered in the past tense
  4.6  Model metrics with the disclosure text visible
  4.7  Model info in the untrained state — tell me how to force this
  4.8  Reversal confirmation dialogue
  4.9  Records view showing an original and its contra entry together
  4.10 Offline pending-sync indicator, backend stopped
  4.12 Any screen at 360 px width showing no horizontal overflow
  4.13 Drying result panel — only if it exists

Give me the list as a run-sheet in the order I should capture them, so I
make one pass rather than resetting state repeatedly. Flag any shot that
requires the backend stopped, since those must be grouped.

Stop and report.
```

---

## Prompt 6 — Phase 5, the data pack

```
Phase 5. Assemble one file, docs/ch4-data/DATA_PACK.md, containing
everything needed to finish Chapter Four. Copy values verbatim from the
artifacts; do not retype from the chapter.

Sections:

  1. Test suite — final count, pass/fail, overall coverage, every module
     below 100% with its percentage, and the pytest --cov tail pasted raw.
  2. Which of the two 4.2.3 gaps closed, with test names, and which did
     not, with the reason.
  3. Per-crop DSS table for all three seeded crops, every field.
  4. Break-even: maize exact value with unit and rounding; the null
     result for the loss-making crop and which case fired.
  5. Maize unit cost on both bases, confirmed unchanged.
  6. Bioprocess summary endpoint output.
  7. Whether the drying sub-form exists; if not, one sentence stating
     that the module is exercised through the API rather than the
     interface.
  8. The screenshot run-sheet from Phase 4.
  9. A list of everything you could NOT produce, and why.

Section 9 is the most important. Do not pad it and do not empty it.

Finally paste git log --oneline for this branch.
```

---

## The two gaps no agent can close

**Evaluators 2 and 3.** These need other people. The lead time is the constraint, not the work — 25 minutes each once someone is sitting down. Run them if you can; the run-sheet is already written. If you cannot, Chapter Four stands at one evaluator honestly reported, which the chapter already handles without restructuring. The decision rule is in 4.8.1 and it is correct: a single evaluator honestly reported is a limitation, three reported without three is misconduct. Do not split the difference.

If you do run them, capture during the session rather than after: tasks completed, mean ease, duration, heuristic compliance, the ten SUS item responses rather than only the total, and every issue with the severity that evaluator assigned. Photograph the sheets before they leave the room — the reason row 10 is unrecoverable is that this was not done.

**Row 10.** One question only: do you remember what you were exporting and what came out wrong? If yes, write it down and it replaces the row. If no, it stays as recorded-and-undiagnosed, which is honest and which the chapter already turns into a methodological finding about instrument retention. Do not reconstruct a plausible version. A reconstructed defect is a fabricated result even when it feels like a memory.
