# TICKET — Partial budget: cross-implementation parity fixture

**Repo:** `C:\Users\DELL\Desktop\Agri P`
**Label:** `ready-for-agent`
**Scope:** one duplicated computation only — `frontend/src/features/dss/partialBudget.ts` against `backend/app/services/enterprise_service.partial_budget`.

**Why this exists:** the offline partial budget is a second implementation of a computation that already exists as a pure function on the backend. Both files assert in comments that they must agree — `partialBudget.test.ts:4-6` and `partialBudget.ts:14-17` — and nothing executes both and compares. The two suites share seven cases and not one input tuple between them. A term added to one implementation leaves both suites green. This ticket replaces a prose claim with an executed one.

This is a single phase. There is no phase gating.

---

## 0. Read before writing any code

Report a short summary of what you found **before** editing anything.

```
frontend/src/features/dss/partialBudget.ts
frontend/src/features/dss/partialBudget.test.ts
backend/app/services/enterprise_service.py     (partial_budget only)
backend/tests/test_enterprise_service.py       (lines around 348 and 365)
backend/tests/test_api.py                      (line around 1944)
frontend/tsconfig.json                          (confirm include: ["src"])
frontend/vitest.config.ts or vite.config.ts     (how JSON imports resolve)
```

Establish specifically:

1. The exact signature and field names of both implementations. Paste both. If the two use different parameter names for the same quantity, say so — the fixture schema must not silently paper over that.
2. Whether vitest resolves a JSON import from `src/fixtures/` with no config change. If it does not, say so and stop rather than editing tooling config.
3. How `backend/tests/` resolves paths today — from the test file's own location or from the working directory. The fixture read must not depend on where pytest was invoked from.
4. Anything below that will not work as written.

---

## 1. Decisions already made — do not relitigate

| Decision | Rationale |
|---|---|
| Fixture lives at `frontend/src/fixtures/partial_budget_parity.json` | `tsc -b` uses `include: ["src"]`, so a file outside `src` is not type-checked and may need a resolve alias. Keeping it inside `src` leaves the frontend tooling untouched. The cost is a directional dependency — a backend test reading a path under `frontend/` — which is accepted deliberately and recorded here. |
| Expected values are **hand-computed**, never generated from either implementation | A generated expectation makes the source implementation definitionally correct, so the test detects divergence but cannot detect that both are wrong. Fixtures A–H in the enterprise economics work are hand-computed for the same reason. |
| Additive — the seven existing cases stay exactly as they are | Matches the standing rule that no existing test is modified to accommodate new work. The shared cases sit alongside them. |
| A missing or malformed fixture is a **loud failure in both suites** | A parity test that skips when it cannot find its input is indistinguishable from no parity test, which is the exact condition this ticket exists to end. |
| Fixture set is named **PB-1 … PB-8** | `A`–`H` already name the enterprise economics fixtures. Two disjoint sets under one label is the naming collision recorded as register finding P1-04. |

---

## 2. The computation under test

```
partial_budget = (revenue_gained + cost_saved) - (revenue_lost + cost_incurred)
```

A positive result means better off; a negative result means worse off. **The result is not clamped** — a negative figure is a real and reportable outcome, and it is what the offline path returned during Phase 6 verification.

---

## 3. Fixture file

Path: `frontend/src/fixtures/partial_budget_parity.json`

Schema — a top-level object, not a bare array, so the file carries its own count:

```json
{
  "description": "Shared parity cases for partial budget. Expected values are hand-computed. Do not regenerate from either implementation.",
  "case_count": 8,
  "cases": [
    {
      "id": "PB-1",
      "description": "…",
      "inputs": {
        "revenue_gained": 0,
        "cost_saved": 0,
        "revenue_lost": 0,
        "cost_incurred": 0
      },
      "expected": 0
    }
  ]
}
```

Use the field names established in Phase 0 question 1. If the two implementations disagree on naming, use the backend names in the JSON and map explicitly on the frontend side — do not rename either implementation.

### The eight cases

Each expected value below is hand-computed and the arithmetic is shown so it is checkable without running anything. If an implementation disagrees with one of these, the implementation is wrong, not the fixture.

| ID | revenue_gained | cost_saved | revenue_lost | cost_incurred | Arithmetic | Expected |
|---|---|---|---|---|---|---|
| PB-1 | 96,000 | 21,000 | 0 | 138,500 | 117,000 − 138,500 | **−21,500** |
| PB-2 | 12,000 | 3,000 | 0 | 9,500 | 15,000 − 9,500 | **5,500** |
| PB-3 | 30,000 | 5,000 | 20,000 | 15,000 | 35,000 − 35,000 | **0** |
| PB-4 | 0 | 0 | 0 | 0 | 0 − 0 | **0** |
| PB-5 | 45,000 | 0 | 0 | 0 | 45,000 − 0 | **45,000** |
| PB-6 | 0 | 0 | 40,000 | 12,500 | 0 − 52,500 | **−52,500** |
| PB-7 | 1,234.56 | 78.90 | 200.25 | 1,000.01 | 1,313.46 − 1,200.26 | **113.20** |
| PB-8 | 10,000 | 2,000 | 3,000 | 50,000 | 12,000 − 53,000 | **−41,000** |

What each case is for, since a fixture whose purpose is undocumented gets deleted by someone later:

- **PB-1 — the sign case, and the reason this ticket exists.** This is the tuple verified by hand during Phase 6 by stopping `agrip-backend-1` mid-session; the offline path returned −₦21,500.00. A sign flip between implementations must fail here. **Assert the sign explicitly and separately from the magnitude** — a test that only compares absolute values would pass a reversed implementation.
- **PB-2 — the ordinary positive case.** Already exercised on the backend at `test_enterprise_service.py:348`; now exercised on both sides with one input.
- **PB-3 — exact zero from non-zero terms.** The boundary between better off and worse off. Assert the result is `0` and not `-0`; a negative zero rendering as "−₦0.00" would tell a farmer they are worse off when they are exactly even.
- **PB-4 — all zeros.** Distinguishes "no change recorded" from a computation that happens to return zero. Both must return `0`, and neither may return null or throw.
- **PB-5 — gains only, no losses.** Exercises the loss side summing to zero without short-circuiting.
- **PB-6 — losses only, no gains.** The mirror. Already exercised on the frontend; now on both.
- **PB-7 — kobo precision.** Catches divergence in float handling and any premature rounding. Compare with `pytest.approx(rel=1e-9)` and the vitest equivalent — this case is about precision, so the tolerance is tighter than the `rel=1e-4` used elsewhere. If either implementation rounds internally, this fails and that is the finding.
- **PB-8 — cross-pair transposition trap.** Swapping `cost_saved` with `cost_incurred` gives 60,000 − 5,000 = +55,000, a different figure of the opposite sign. Any implementation that confuses a saved cost for an incurred one fails here rather than passing by symmetry.

---

## 4. Loud failure — both suites

This is the requirement most likely to be quietly softened, so it is stated as behaviour rather than as intent.

**Forbidden in both suites:** `pytest.skip`, `pytest.importorskip`, `describe.skip`, `it.skip`, any `try`/`except` or `try`/`catch` around the fixture read, any `if (!fixture) return`, and any default or fallback value substituted when the file is absent.

**Required in both suites:**

1. A missing file raises and fails the test. Do not catch it.
2. Malformed JSON raises and fails the test. Do not catch it.
3. `case_count` is compared against the actual length of `cases`, and a mismatch fails with a message naming both numbers. A truncated-but-parseable file must not pass with two cases.
4. The parsed length is also compared against a constant declared in each test file, so that silently shrinking the fixture fails both suites rather than passing quietly.
5. Every case in the file is executed. Do not filter, sample, or hard-code a subset.

**Prove requirements 1–3.** Temporarily (a) rename the fixture file, (b) truncate it to invalid JSON, and (c) set `case_count` to 9 while leaving 8 cases. Run both suites after each. Paste the failure output from all six runs, then restore the file and confirm it is unmodified in the commit. This is the same no-op verification discipline used in Phase 6b, and for the same reason: a test that cannot be shown to fail is not evidence.

Record the exact commands and the six expected failure messages in `docs/EVIDENCE.md`.

---

## 5. Test structure

**Backend** — add to `backend/tests/test_enterprise_service.py`. Resolve the fixture from the test file's own location, e.g. `Path(__file__).resolve().parents[2] / "frontend" / "src" / "fixtures" / "partial_budget_parity.json"` — confirm the parent depth against what Phase 0 found. It must not depend on the working directory pytest was invoked from. Parametrise over the cases so each reports as a named test, with the case `id` in the test identifier.

**Frontend** — add to `frontend/src/features/dss/partialBudget.test.ts`. Import the JSON directly if Phase 0 confirmed that resolves; otherwise read it from disk in the test. Iterate with `it.each` or equivalent so each case reports separately by `id`.

**Both:** the existing seven cases stay exactly as written. Add nothing to them, remove nothing from them, renumber nothing.

**Both:** add a comment above the parity block naming the fixture path and stating that expected values are hand-computed and must not be regenerated. Then update the two existing prose comments — `partialBudget.ts:14-17` and `partialBudget.test.ts:4-6` — to point at the fixture file instead of asking the reader to take the claim on trust. That is the whole point of the ticket: the assertion moves from prose into something that executes.

---

## 6. Definition of done

- [ ] `frontend/src/fixtures/partial_budget_parity.json` exists with all eight cases and `case_count: 8`.
- [ ] Both suites execute all eight and pass.
- [ ] PB-1 has an explicit sign assertion separate from its magnitude assertion, in both suites.
- [ ] PB-3 asserts the result is not negative zero.
- [ ] The six loud-failure runs are pasted, and the fixture is unmodified in the commit.
- [ ] `docs/EVIDENCE.md` records the commands and the six expected failure messages.
- [ ] The seven pre-existing cases are untouched — paste `git diff` for both test files and confirm additions only.
- [ ] The two prose comments now name the fixture path.
- [ ] Full backend suite green; full frontend suite green; `eslint` clean; `tsc -b` clean.
- [ ] No new Python or JavaScript dependency.
- [ ] No Alembic migration.
- [ ] Nothing under `backend/app/ml/` modified.

---

## 7. Out of scope

Cache invalidation of any kind — that work closed in Phase 6b and 6c. The `StaleWhileRevalidate` revalidation race. Any change to either implementation of the partial budget: if they disagree, **report it and stop** rather than editing one to match the other, because which one is wrong is a decision for me. Any refactor to share code across the wire — the duplication is deliberate and is what makes the offline path work. Any other duplicated computation; this ticket is the partial budget only.

---

## 8. Agent prompt

```
We are adding a shared hand-computed fixture that proves the offline
partial budget and the backend partial_budget agree. The full
specification is at .scratch/partial-budget-parity.md — read it now, in
full, before doing anything else.

Rules:

1. Add no Python or JavaScript dependency, no Alembic migration, and do
   not touch backend/app/ml/.
2. Do not modify either implementation of the partial budget. If they
   disagree with a fixture, stop and report — do not edit one to match.
3. Do not modify any of the seven existing test cases.
4. Expected values are hand-computed and given in section 3. Do not
   regenerate them from either implementation. If one disagrees, the
   implementation is wrong, not the fixture.
5. No skip, no try/except around the fixture read, no fallback value. A
   missing or malformed fixture must fail loudly in both suites.
6. Create a branch before your first edit:
   git checkout -b feat/partial-budget-parity

Do section 0 first — read only, report, and stop. I will tell you when
to proceed.
```

After the Phase 0 report, the remainder runs in one pass. Then:

```
Proceed. Build the fixture, add the parity cases to both suites, and run
the six loud-failure verification runs in section 4.

Report: the fixture file in full; both diffs, confirming additions only;
the eight case results per suite; the six failure outputs; full suites,
eslint and tsc -b; and the docs/EVIDENCE.md addition. Commit with a
message naming the fixture path.
```

---

## 9. Rescue prompts

**If the two implementations disagree on a case:**

```
Stop. Do not edit either implementation.

Report: the case id, both returned values, the hand-computed expected
value from section 3, and the arithmetic each implementation performed
to reach its answer. Print the intermediate sums — gains total and
losses total — from both sides. Then wait.
```

**If vitest cannot resolve the JSON from src/fixtures/:**

```
Stop. Do not edit tsconfig.json, vite.config.ts or vitest config.

Report what you tried, the exact error, and what the minimum config
change would be. The fixture location was chosen specifically to avoid a
tooling change, so if one is unavoidable that is a decision for me.
```

**If the agent proposes sharing code across the wire:**

```
Stop. The duplication is deliberate — the offline path exists precisely
because the server is unreachable, so it cannot call the server's
implementation. The fixture is how the two are kept in agreement. Do not
propose a shared module, a code generator, or a build step.
```
