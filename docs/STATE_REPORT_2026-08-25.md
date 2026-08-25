# Project State Report — 2026-08-25

Compiled read-only. No source file, document, test, seed script or configuration
was modified. Nothing was reseeded, migrated or rebuilt except the frontend
production bundle, which Section 7.5 explicitly requires (`frontend/dist` is
git-ignored, so no tracked file changed).

Working directory: `C:\Users\DELL\Desktop\Agri P`. Branch: `feat/partial-budget-parity`.

Thesis chapter files were NOT read as evidence. They exist at the repository
root with these filenames, noted here only for completeness:
`AgriProfit_Chapters_1-3.docx`, `AgriProfit_Chapters_1-3_corrected.docx`,
`AgriProfit_Evaluation_Pack.docx`, `AgriProfit_Viva_Prep.docx`,
`docs/print/Thesis_Ch1-3.docx`, `docs/print/Thesis_Ch1-3.pdf`.

---

## 1. Repository and git state

### 1.1 `git branch -a`

```
  feat/bioprocess-drying
  feat/enterprise-economics
* feat/partial-budget-parity
  main
  remotes/origin/HEAD -> origin/main
  remotes/origin/feat/bioprocess-drying
  remotes/origin/feat/partial-budget-parity
  remotes/origin/main
```

### 1.2 `git tag --list`

```
```

Empty. There are no tags in this repository.

### 1.3 Current branch and `git status --porcelain`

Current branch: `feat/partial-budget-parity`

```
 M CLAUDE.md
?? .scratch/TICKET_enterprise_economics.md
?? .scratch/TICKET_partial_budget_parity.md
?? AGENT_PROMPT_chapter4_gaps.md
?? AGENT_PROMPT_thesis_conformance.md
?? "Updated B.Tech Final Project Guideline for 2025_2026_v1.pdf"
?? docs/print/
```

### 1.4 Uncommitted work

`git diff --stat`:

```
 CLAUDE.md | 73 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 73 insertions(+)
```

`git diff --stat --cached`:

```
```

Empty — nothing is staged.

The uncommitted work is a 73-line addition to `CLAUDE.md` (agent working rules),
plus six untracked paths: two ticket files under `.scratch/`, two agent-prompt
files at the root, a project-guideline PDF, and the `docs/print/` directory
holding the Chapters 1–3 DOCX and PDF. No backend or frontend source file is
modified.

### 1.5 `git log --oneline -40`

```
09bcc32 docs(evidence): state the baseline the "no new dependency" item is read against
7e3e798 docs(evidence): record the command behind every figure quoted on this branch
330f1d9 test(dss): prove offline and backend partial budgets agree via a shared fixture
1337787 chore(git): add .gitattributes so line endings stop churning
e8c60c6 refactor(cache): move the reversal purge into the client, test it, write the race down
d82419d fix(cache): purge the read cache on log, flush, equipment and maintenance writes
94e554a feat(dss): show cost structure, both break-even prices and the sensitivity table
6f926a5 feat(seed): add cowpea, sorghum and two assets to the demo farm
fab45d8 fix(enterprise): import the cost taxonomy relatively, so the app boots
0543cd9 docs(adr): record why a zero depreciation rate is refused, not stored
a9a4c28 feat(equipment): capture the depreciation rate, settle its unit
2dcf328 feat(enterprise): pin the depreciation window, ratio on cost structure
8f9554a feat(dss): expose cost structure, break-even price and sensitivity
da96e7e feat(enterprise): derive cost structure, dual break-even and sensitivity
14362f4 feat(schema): classify mechanisation cost at the schema edge
432214a docs(context): give cost structure its own glossary section
502dced fix(investor): show marketable mass beside the rate that divides by it
2a282ba feat(dss): surface marketable unit cost beside the harvest-unit figure
6e8bac2 docs(ch4): assemble the Chapter Four data pack (phase 5)
e3bb674 docs(ch4): add the screenshot run-sheet for Phase 4
ec00162 test(frontend): measure coverage, and take the sync queue to 100%
d2f45af test(sync): cover the offline write queue's flush, three-strike and retry paths
ab7a0da docs(ch4): capture the DSS, bioprocess and model responses for Chapter Four
b1987f5 feat(seed): add a profitable and a loss-making crop to the demo farm
e833667 chore(repo): drop the unused design mockups, add the cleanup analysis
856200a feat(bioprocess): capture drying runs and show their metrics (ticket 08 phase 6)
59554cc perf(frontend): code-split the routes and the dashboard charts
73176dc refactor(frontend): extract the nav module and clear the lint backlog
d254e2a fix(backend): replace deprecated SQLAlchemy and FastAPI APIs
8690289 fix(bioprocess): water_removed_kg is a water balance, not a mass difference
dd8ebac test(bioprocess,dss): discriminating water-balance fixture; cover GET /dss/model
ef847f0 docs: chapter correction redline for Chapters 1-3
69d1aca feat(dss): surface model quality metrics on the prediction page
7bcadd5 feat(dss): rank crops by margin, add retrospective break-even yield
b6e2ddb feat(ui): responsive layout, and remove the USSD/WhatsApp placeholders
fbdadca fix(dss): omit empty crop buckets from decision support
d63d0ca docs: date the measurement set 17 August throughout
99676a3 docs: add limitations, progress summary and the Objective 4 evaluation strands
13f95a6 docs(perf): re-measure against the c16924e build, supersede the 15 Aug set
c16924e fix(ui,dss): remove unsupported claims, add reversal UI, group yield by unit
```

### 1.6 `git log --oneline --all --graph -25`

```
* 09bcc32 docs(evidence): state the baseline the "no new dependency" item is read against
* 7e3e798 docs(evidence): record the command behind every figure quoted on this branch
* 330f1d9 test(dss): prove offline and backend partial budgets agree via a shared fixture
* 1337787 chore(git): add .gitattributes so line endings stop churning
* e8c60c6 refactor(cache): move the reversal purge into the client, test it, write the race down
* d82419d fix(cache): purge the read cache on log, flush, equipment and maintenance writes
* 94e554a feat(dss): show cost structure, both break-even prices and the sensitivity table
* 6f926a5 feat(seed): add cowpea, sorghum and two assets to the demo farm
* fab45d8 fix(enterprise): import the cost taxonomy relatively, so the app boots
* 0543cd9 docs(adr): record why a zero depreciation rate is refused, not stored
* a9a4c28 feat(equipment): capture the depreciation rate, settle its unit
* 2dcf328 feat(enterprise): pin the depreciation window, ratio on cost structure
* 8f9554a feat(dss): expose cost structure, break-even price and sensitivity
* da96e7e feat(enterprise): derive cost structure, dual break-even and sensitivity
* 14362f4 feat(schema): classify mechanisation cost at the schema edge
* 432214a docs(context): give cost structure its own glossary section
* 502dced fix(investor): show marketable mass beside the rate that divides by it
* 2a282ba feat(dss): surface marketable unit cost beside the harvest-unit figure
* 6e8bac2 docs(ch4): assemble the Chapter Four data pack (phase 5)
* e3bb674 docs(ch4): add the screenshot run-sheet for Phase 4
* ec00162 test(frontend): measure coverage, and take the sync queue to 100%
* d2f45af test(sync): cover the offline write queue's flush, three-strike and retry paths
* ab7a0da docs(ch4): capture the DSS, bioprocess and model responses for Chapter Four
* b1987f5 feat(seed): add a profitable and a loss-making crop to the demo farm
* e833667 chore(repo): drop the unused design mockups, add the cleanup analysis
```

The graph is a single unbranched line: every other branch is an ancestor of `HEAD`.

### 1.7 Branches not fully merged into the current branch

`git branch --no-merged HEAD -a` returns **nothing**. Every local and remote
branch is fully contained in `feat/partial-budget-parity`. Verified individually:

| Branch | Last commit date | `git log --oneline <branch> ^feat/partial-budget-parity` |
|---|---|---|
| `feat/bioprocess-drying` | `6e8bac2` — 2026-08-19 05:10:39 +0900 | (empty) |
| `feat/enterprise-economics` | `1337787` — 2026-08-25 16:03:50 +0900 | (empty) |
| `main` | `a667060` — 2026-07-20 21:57:41 +0900 | (empty) |
| `origin/main` | `a667060` — 2026-07-20 21:57:41 +0900 | (empty) |
| `origin/feat/bioprocess-drying` | `d63d0ca` — 2026-08-18 07:17:10 +0900 | (empty) |
| `origin/feat/partial-budget-parity` | `09bcc32` — 2026-08-25 17:03:34 +0900 | (empty) |

The reverse direction is not empty: `main` is far behind. The
enterprise-economics and bioprocess work has never been merged to `main`, and
`origin/feat/partial-budget-parity` is level with local `HEAD`.

### 1.8 The commit corresponding to the state defended on 19 August 2026

**Nothing in the repository identifies it.** There are no tags at all (1.2), and
no commit message contains "defend", "viva", "presentation" or a date reference
to 19 August. `git log --all --oneline --grep='defen' --grep='19 Aug' -i`
returns one unrelated match (`acf5efe feat: security and API-consistency
hardening`), which matches on a coincidental substring.

Circumstantial only, and offered as such rather than as an identification:
twelve commits carry an author date of 2026-08-19, the last being
`6e8bac2 docs(ch4): assemble the Chapter Four data pack (phase 5)` at
2026-08-19 05:10:39 +0900, which is also the tip of `feat/bioprocess-drying`.
To establish the defended commit properly would need a tag, a release note, or
the user's own record of what was demonstrated.

---

## 2. Test suite — current results

### 2.1 Full backend suite

Command (run from the repository root — `backend/tests/conftest.py:8` imports
`backend.app.main`, so running from `backend/` fails with
`ModuleNotFoundError: No module named 'backend'`):

```
python -m pytest -q
```

Complete output:

```
........................................................................ [ 40%]
........................................................................ [ 80%]
...................................                                      [100%]
============================== warnings summary ===============================
..\..\AppData\Roaming\Python\Python314\site-packages\fastapi\testclient.py:1
  C:\Users\DELL\AppData\Roaming\Python\Python314\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
179 passed, 1 warning in 101.20s (0:01:41)
```

### 2.2 Totals

| | |
|---|---|
| Collected | 179 |
| Passed | 179 |
| Failed | 0 |
| Skipped | 0 |
| Errored | 0 |

No failure output to paste. One warning, a `StarletteDeprecationWarning` about
`httpx` in `starlette.testclient`, originating in the installed FastAPI package
rather than in this repository.

### 2.3 Coverage

Command:

```
python -m pytest --cov=backend/app --cov-report=term-missing -q
```

This measures **statement coverage**, not branch coverage — `--cov-branch` is
not passed, and the repository carries no coverage configuration that would turn
branch measurement on.

Full per-module table, verbatim:

```
Name                                         Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------
backend\app\__init__.py                          0      0   100%
backend\app\api\__init__.py                      0      0   100%
backend\app\api\deps.py                         20      3    85%   37-38, 41
backend\app\api\endpoints\__init__.py            0      0   100%
backend\app\api\endpoints\auth.py               21      1    95%   40
backend\app\api\endpoints\bioprocess.py         54      0   100%
backend\app\api\endpoints\dss.py                46      3    93%   45-47
backend\app\api\endpoints\equipment.py          21      0   100%
backend\app\api\endpoints\investor.py           22      0   100%
backend\app\api\endpoints\ledger.py             34      0   100%
backend\app\api\endpoints\reports.py             20      0   100%
backend\app\api\router.py                       10      0   100%
backend\app\core\__init__.py                     0      0   100%
backend\app\core\config.py                      18      0   100%
backend\app\core\enums.py                       12      0   100%
backend\app\core\exceptions.py                  16      0   100%
backend\app\core\security.py                    30      2    93%   36-38
backend\app\main.py                             48      6    88%   33-35, 70-71, 82
backend\app\ml\__init__.py                       0      0   100%
backend\app\ml\dataset.py                       50     32    36%   75-88, 93-103, 116-121, 125-129
backend\app\ml\predict.py                       46      4    91%   31, 44, 59-60
backend\app\ml\train.py                         53     31    42%   36-45, 53-64, 69-105, 116-117, 121-123
backend\app\models\__init__.py                   0      0   100%
backend\app\models\database.py                  11      4    64%   11-15
backend\app\models\models.py                    76      0   100%
backend\app\schemas\__init__.py                  0      0   100%
backend\app\schemas\schemas.py                 170      0   100%
backend\app\services\__init__.py                 0      0   100%
backend\app\services\auth_service.py            22      0   100%
backend\app\services\bioprocess_service.py      68      0   100%
backend\app\services\dss_service.py            162      0   100%
backend\app\services\enterprise_service.py      72      0   100%
backend\app\services\equipment_service.py       27      0   100%
backend\app\services\ledger_service.py          56      8    86%   57-66, 116
backend\app\services\reports_service.py         68      4    94%   90-91, 109, 112
backend\app\services\share_service.py           32      0   100%
--------------------------------------------------------------------------
TOTAL                                         1285     98    92%
179 passed, 1 warning in 53.62s
```

(The `reports.py` row is reproduced with the column alignment as printed; the
figures are 20 statements, 0 missed, 100%.)

### 2.4 Overall coverage

**92%** — 1,285 total statements, 98 missed.

### 2.5 Modules at 100% coverage

25 rows read 100%. Eight of them are empty `__init__.py` files carrying zero
statements, so the two groups are listed separately.

**17 modules with executable statements, fully covered:**

1. `backend/app/api/endpoints/bioprocess.py` (54 stmts)
2. `backend/app/api/endpoints/equipment.py` (21)
3. `backend/app/api/endpoints/investor.py` (22)
4. `backend/app/api/endpoints/ledger.py` (34)
5. `backend/app/api/endpoints/reports.py` (20)
6. `backend/app/api/router.py` (10)
7. `backend/app/core/config.py` (18)
8. `backend/app/core/enums.py` (12)
9. `backend/app/core/exceptions.py` (16)
10. `backend/app/models/models.py` (76)
11. `backend/app/schemas/schemas.py` (170)
12. `backend/app/services/auth_service.py` (22)
13. `backend/app/services/bioprocess_service.py` (68)
14. `backend/app/services/dss_service.py` (162)
15. `backend/app/services/enterprise_service.py` (72)
16. `backend/app/services/equipment_service.py` (27)
17. `backend/app/services/share_service.py` (32)

**8 empty modules (0 statements), reported as 100% by coverage.py:**
`app/__init__.py`, `api/__init__.py`, `api/endpoints/__init__.py`,
`core/__init__.py`, `ml/__init__.py`, `models/__init__.py`,
`schemas/__init__.py`, `services/__init__.py`.

### 2.6 Modules below 80% coverage

| Module | Coverage |
|---|---|
| `backend/app/ml/dataset.py` | 36% |
| `backend/app/ml/train.py` | 42% |
| `backend/app/models/database.py` | 64% |

Three modules. Nothing else falls below 85%.

### 2.7 Frontend tests

A runner is configured: Vitest (`frontend/package.json` → `"test": "vitest run"`,
with `vitest.config.ts` and a `jsdom` environment).

Command: `cd frontend && npm test`

```
> frontend@0.0.0 test
> vitest run


 RUN  v4.1.10 C:/Users/DELL/Desktop/Agri P/frontend


 Test Files  6 passed (6)
      Tests  41 passed (41)
   Start at  19:38:16
   Duration  39.05s (transform 1.24s, setup 0ms, import 17.40s, tests 810ms, environment 85.52s)
```

**6 test files, 41 tests, all passing.** Per file, from `npx vitest list`:

| File | Tests |
|---|---|
| `src/features/dss/partialBudget.test.ts` | 15 |
| `src/features/farm-records/dryingParams.test.ts` | 10 |
| `src/lib/sync.test.ts` | 8 |
| `src/lib/cacheInvalidation.test.tsx` | 5 |
| `src/features/auth/AuthProvider.test.tsx` | 2 |
| `src/lib/apiCache.test.ts` | 1 |

### 2.8 Every test file under `backend/tests/`

| File | Tests |
|---|---|
| `backend/tests/test_api.py` | 128 |
| `backend/tests/test_enterprise_service.py` | 40 |
| `backend/tests/test_bioprocess_service.py` | 11 |
| `backend/tests/conftest.py` | 0 — fixtures only, no test functions |

Total 179. There is no `tests/__init__.py`; `__pycache__` is the only other entry
in the directory.

---

## 3. Enterprise economics — actual implementation state

Determined from source, coverage output, the router, the ADR directory, the
frontend tree and live endpoint responses. The ticket file was consulted only
for the *specification* in 3.10, never as evidence of what exists.

### 3.1 `backend/app/services/enterprise_service.py`

**It exists** (72 statements, 100% covered — Section 2.3). It is a pure module:
its only import from the application is `from ..schemas.schemas import
CostBehaviour, cost_behaviour_for`. Eight public functions:

```
backend/app/services/enterprise_service.py:39
def cost_structure(
    entries: Sequence[tuple[float, str, Optional[str]]],
) -> dict:

backend/app/services/enterprise_service.py:84
def depreciation_overlay(
    equipment: Sequence[dict],
    period_days: float,
) -> dict:

backend/app/services/enterprise_service.py:132
def allocate_fixed_cost(
    period_fixed_cost_ngn: float,
    direct_cost_by_crop: dict[str, float],
) -> dict:

backend/app/services/enterprise_service.py:178
def break_even_prices(
    cash_cost: float,
    total_recorded_cost: float,
    allocated_fixed_ngn: Optional[float],
    marketable_mass_kg: Optional[float],
    classification_coverage_pct: Optional[float] = None,
) -> dict:

backend/app/services/enterprise_service.py:246
def yield_sensitivity(
    baseline_marketable_mass_kg: Optional[float],
    cash_cost: float,
    total_cost: float,
    percentages: Sequence[int] = DEFAULT_SENSITIVITY_PCT,
) -> dict:

backend/app/services/enterprise_service.py:290
def operating_expense_ratio_pct(
    cash_operating_cost_ngn: float,
    revenue_ngn: float,
) -> Optional[float]:

backend/app/services/enterprise_service.py:318
def partial_budget(
    added_revenue_ngn: float,
    reduced_cost_ngn: float,
    lost_revenue_ngn: float,
    added_cost_ngn: float,
) -> dict:

backend/app/services/enterprise_service.py:359
def olympic_average_yield(season_yields_kg: Sequence[float]) -> dict:
```

Module-level constants, verbatim:

```
backend/app/services/enterprise_service.py:81
DAYS_PER_YEAR = 365.0

backend/app/services/enterprise_service.py:243
DEFAULT_SENSITIVITY_PCT: tuple[int, ...] = (75, 90, 100, 110, 125)

backend/app/services/enterprise_service.py:356
MIN_SEASONS_FOR_OLYMPIC = 3
```

### 3.2 `CostBehaviour`, `MechanizationParams`, `COST_BEHAVIOUR`

All three exist, all in `backend/app/schemas/schemas.py` (there is nothing
cost-related in `backend/app/core/enums.py`).

```
backend/app/schemas/schemas.py:98
class CostBehaviour(str, Enum):
    VARIABLE      = "VARIABLE"
    SEMI_VARIABLE = "SEMI_VARIABLE"
    FIXED         = "FIXED"
```

```
backend/app/schemas/schemas.py:104
class MechanizationParams(BaseModel):
    cost_subtype: Literal["FUEL", "LUBRICANTS", "REPAIRS", "MACHINERY_HIRE", "DEPRECIATION"]
    equipment_id: int | None = None
    hours_used: float | None = Field(default=None, gt=0, le=1000)
```

```
backend/app/schemas/schemas.py:110-129
# TODO(cite): cost-behaviour classification follows standard enterprise-budget
# practice (variable = scales with output; fixed = independent of output).
# Cite an agricultural economics text or extension enterprise-budget guide
# before submission. "The taxonomy was supplied" is not a citation.
#
# Keyed on (activity category, cost subtype) so a category that later gains a
# subtype model of its own — LABOUR splitting into permanent and casual — is
# added by replacing its single None-keyed row with one row per subtype, with no
# change to the lookup. Categories absent here (YIELD, OTHER) are unclassified.
COST_BEHAVIOUR: dict[tuple[str, str], CostBehaviour] = {
    ("MECHANIZATION", "FUEL"):           CostBehaviour.VARIABLE,
    ("MECHANIZATION", "LUBRICANTS"):     CostBehaviour.VARIABLE,
    ("MECHANIZATION", "REPAIRS"):        CostBehaviour.SEMI_VARIABLE,
    ("MECHANIZATION", "MACHINERY_HIRE"): CostBehaviour.VARIABLE,
    ("MECHANIZATION", "DEPRECIATION"):   CostBehaviour.FIXED,
    ("SEED",      None):                 CostBehaviour.VARIABLE,
    ("FERTILIZER", None):                CostBehaviour.VARIABLE,
    ("LABOUR",    None):                 CostBehaviour.VARIABLE,
    ("BIOPROCESS", None):                CostBehaviour.VARIABLE,
}
```

A pure lookup `cost_behaviour_for(activity_type, cost_subtype)` sits at
`backend/app/schemas/schemas.py:132`, returning `None` for any unlisted pair.

Note the outstanding `TODO(cite)` above the constant: the taxonomy carries no
citation in the repository.

### 3.3 Conditional MECHANIZATION validation at the schema edge

Yes. Inside `OperationalLogCreate._validate_activity_payload`:

```
backend/app/schemas/schemas.py:180-189
        # A Mechanization log MAY carry cost-classification parameters, and they
        # are validated when present. extra_data is None on every legacy row and
        # classification is opt-in, so absence is accepted and simply classifies
        # as None — refusing it would break a shipped write path.
        if self.activity_type == Category.MECHANIZATION and self.extra_data is not None:
            try:
                MechanizationParams.model_validate(self.extra_data)
            except ValidationError as exc:
                raise ValueError(f"Invalid Mechanization cost parameters: {exc}") from exc
        return self
```

**A MECHANIZATION log with `extra_data = None` is ACCEPTED**, and classifies as
unclassified rather than defaulting into a bucket. Established by two artifacts:

- the guard `and self.extra_data is not None` at
  `backend/app/schemas/schemas.py:184`, which skips validation entirely when
  `extra_data` is absent;
- the passing test
  `backend/tests/test_api.py::test_mechanization_without_extra_data_accepted_and_unclassified`.

Contrast with BIOPROCESS at `backend/app/schemas/schemas.py:175-179`, which is
unconditional: a missing or malformed drying payload is rejected
(`test_bioprocess_missing_payload_rejected`).

### 3.4 Enterprise-economics routes registered in the router

`backend/app/api/router.py` registers seven routers; there is no separate
enterprise router — the enterprise routes extend the existing `/dss` surface:

```
backend/app/api/router.py:1-11
from fastapi import APIRouter
from .endpoints import auth, ledger, dss, equipment, reports, investor, bioprocess

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(ledger.router)
api_router.include_router(dss.router)
api_router.include_router(equipment.router)
api_router.include_router(reports.router)
api_router.include_router(investor.router)
api_router.include_router(bioprocess.router)
```

`backend/app/main.py:74` mounts it: `app.include_router(api_router, prefix="/api/v1")`.
`backend/app/api/endpoints/dss.py:17` sets `router = APIRouter(prefix="/dss", tags=["dss"])`.

Five enterprise-economics routes are registered:

| Method | Path | Handler (file:line) |
|---|---|---|
| GET | `/api/v1/dss/cost-structure` | `dss.py:68 get_cost_structure` |
| GET | `/api/v1/dss/break-even-price` | `dss.py:92 get_break_even_price` |
| GET | `/api/v1/dss/sensitivity` | `dss.py:121 get_sensitivity` |
| POST | `/api/v1/dss/partial-budget` | `dss.py:147 post_partial_budget` |
| GET | `/api/v1/dss/yield-baseline` | `dss.py:161 get_yield_baseline` |

Registration decorators as they appear:

```
backend/app/api/endpoints/dss.py:67   @router.get("/cost-structure", response_model=schemas.CostStructureResponse)
backend/app/api/endpoints/dss.py:91   @router.get("/break-even-price", response_model=schemas.BreakEvenPriceResponse)
backend/app/api/endpoints/dss.py:120  @router.get("/sensitivity", response_model=schemas.SensitivityResponse)
backend/app/api/endpoints/dss.py:146  @router.post("/partial-budget", response_model=schemas.PartialBudgetResponse)
backend/app/api/endpoints/dss.py:160  @router.get("/yield-baseline", response_model=schemas.YieldBaselineResponse)
```

The pre-existing DSS routes on the same prefix are `GET /decision-support`
(`dss.py:20`), `POST /predict` (`dss.py:32`), `POST /train` (`dss.py:42`) and
`GET /model` (`dss.py:50`).

### 3.5 Depreciation overlay

Computed, not stubbed, and it returns real numbers. The pure function:

```
backend/app/services/enterprise_service.py:84-127
def depreciation_overlay(
    equipment: Sequence[dict],
    period_days: float,
) -> dict:
    """Periodic depreciation charge across a set of equipment records.

        annual_charge_ngn = purchase_value_ngn * depreciation_rate
        period_charge_ngn = annual_charge_ngn * (period_days / 365)
    ...
    """
    annual = 0.0
    unrated = 0

    for item in equipment:
        rate = item.get("depreciation_rate")
        value = item.get("purchase_value_ngn")
        if not rate or not value:
            unrated += 1
            continue
        annual += value * rate

    return {
        "annual_charge_ngn": annual,
        "period_charge_ngn": annual * (period_days / DAYS_PER_YEAR),
        "period_days": period_days,
        "equipment_count": len(equipment),
        "equipment_unrated_count": unrated,
    }
```

It is wired through `dss_service.get_break_even_price`
(`backend/app/services/dss_service.py:542`), which also calls
`enterprise_service.break_even_prices` at line 585. The live response in 6.6
returns `"period_fixed_cost_ngn": 10068.493150684932`, `"equipment_count": 2`,
`"equipment_unrated_count": 1` and a non-null `allocated_fixed_ngn` — so it is
neither null nor stubbed. Nothing is posted to the ledger; the value is derived
at read time.

### 3.6 Break-even metrics — three distinct names

Yes, there are two break-even **price** fields, and they are distinct from the
retrospective break-even **yield**. All three, as they appear in code:

```
backend/app/schemas/schemas.py:306   break_even_yield: Optional[float] = None
backend/app/schemas/schemas.py:464   break_even_price_cash_ngn_per_kg: Optional[float] = None
backend/app/schemas/schemas.py:467   break_even_price_total_ngn_per_kg: Optional[float] = None
```

(The two price names recur at `schemas.py:505-506` on the sensitivity row model,
and are produced in `enterprise_service.break_even_prices` at lines 230–231 and
in `yield_sensitivity` at lines 275–276.)

The yield figure carries a companion unit field,
`break_even_unit` (`schemas.py:307`), and is computed at
`backend/app/services/dss_service.py:226-246` from realised revenue — it is
retrospective. The two prices are conditional and per marketable kilogram. All
three appear on live responses in Section 6.

### 3.7 `docs/adr/`

Two ADRs are present:

| File | Title | Status |
|---|---|---|
| `docs/adr/0001-bioprocess-drying-parameters-in-extra-data.md` | 1. Bioprocess drying parameters in `extra_data`, not a new table | Accepted |
| `docs/adr/0002-derived-fixed-cost-overlay-and-temporary-domain-assumptions.md` | 2. Derived fixed-cost overlay, and three temporary domain assumptions | Accepted |

ADR-0002 exists. Its Decision section, verbatim:

> ## Decision
>
> ### 1. Depreciation is a derived overlay, computed at report time, never posted
>
> The periodic charge is `purchase_value × depreciation_rate × (period_days ÷
> 365)`, computed in `enterprise_service.depreciation_overlay` when a report is
> read. No depreciation Financial Transaction is ever written by this code path.
>
> Posting synthetic depreciation rows would require either unpaired entries — a
> direct violation of the paired-write invariant — or fabricated Operational Logs
> describing events that did not happen. Neither is acceptable in a ledger whose
> whole claim is that every row records something a farmer did. The overlay is
> consistent with `unit_cost_per_kg_marketable` and every other derived figure on
> this platform: computed, transparent, recomputable, never stored.
>
> Three simplifications ride along, stated rather than hidden: straight line, no
> salvage value, and no accumulated-depreciation floor, so an asset held past its
> implied life keeps charging. The charge is therefore an upper bound. Equipment
> with a null or zero rate contributes nothing and is counted in
> `equipment_unrated_count`, so a partial overlay is visible as partial rather
> than being read as a small true fixed cost.
>
> A **recorded** `DEPRECIATION` cost subtype on a real ledger row is a different
> thing entirely and stays in its own bucket, `fixed_cost_recorded`. The two are
> never added together.
>
> ### 2. TEMPORARY: fixed cost is allocated to crops in proportion to direct cost
>
> `allocated_fixed = period_fixed_cost × (crop_direct_cost ÷ total_direct_cost)`.
>
> Proportional-to-direct-cost is the standard fallback where no physical base
> exists, and it is an **assumption, not a measurement**. It will over-allocate to
> an input-intensive crop and under-allocate to a land-intensive one, because
> direct cost is not a proxy for the share of a tractor's life a crop consumed.
>
> Where the total direct cost is zero, every share and every allocation is `None`.
> An even split would invent an allocation base that does not exist; a zero would
> claim the fixed cost had disappeared. "Undefined" is the better answer, in the
> same way a unit cost over no yield is undefined.
>
> The allocation base is computed **farm-wide, before any crop filter is applied**.
> Deriving it from a filtered subset would give a single filtered crop a share of
> 1.0 and hand it the entire overlay — the same figure would change depending on
> how it was requested.
>
> ### 3. TEMPORARY: a season is a calendar year of recorded yield
>
> `get_yield_baseline` groups a crop's yield observations by
> `timestamp.year`, sums within the year, and treats each year as one season for
> the Olympic average. Several yield logs in one year are one season, not several.
>
> This is the only grouping the model can express. It is **wrong wherever a crop
> does not align with the calendar**: a double-cropped season straddling December
> becomes two seasons or one depending on which side of the new year the harvest
> was logged, and a single long cycle spanning a year boundary is split in half.
> For a single rain-fed cycle harvested mid-year — the case the platform is built
> around — it is correct.
>
> `n_seasons` is reported in **every** branch of the response, including the ones
> that return no average at all, so a null Olympic average is never read without
> the count that explains it. One season and ten seasons are different reasons for
> the same null.
>
> ### 4. The depreciation window defaults to the ledger span but can be pinned
>
> By default `period_days` runs from the farm's first surviving log to its last,
> inclusive, so the charge lines up with the costs it is compared against. An
> optional `period_days` query parameter overrides it, and `period_source`
> (`"derived"` | `"specified"`) travels in the response.
>
> The override is a **reproducibility** measure, not a convenience. A derived span
> widens every time a log is entered; the charge is proportional to the span; the
> allocation is drawn from the charge; the break-even price to cover total cost is
> drawn from the allocation. So entering an unrelated log silently moves a price
> that was already reported, quoted in a document, or written down — and nobody
> can re-derive it afterwards, because the window it was computed over no longer
> exists. A pinned window makes a figure reproducible; `period_source` makes the
> two cases distinguishable, so a reader comparing reports knows whether a moved
> price means the farm changed or only the window did.
>
> An explicit period is used as given and is **not** clamped to the ledger span. A
> window longer than the records is a legitimate question — what a full season of
> machine wear costs against a part-season of logs — and silently shrinking it
> would answer a different one. It is bounded above at a century of days, beyond
> which the caller is not describing a reporting period.

### 3.8 Enterprise-economics tests

**79 tests**, in two backend files: 40 in `test_enterprise_service.py` and 39 in
`test_api.py` (`pytest --collect-only -q -k "enterprise or mechanization or
depreciation"` on `test_api.py` collects 39 of 128).

`backend/tests/test_enterprise_service.py` — 40 tests (unit tests over the pure
functions):

```
test_fixture_a_classification_and_coverage
test_zero_total_cost_has_undefined_coverage
test_fixed_recorded_cost_is_its_own_bucket_and_stays_out_of_cash
test_unclassified_categories_never_default_into_a_bucket
test_fixture_b_depreciation_overlay
test_zero_rate_equipment_counts_as_unrated_not_as_a_zero_charge
test_equipment_with_no_purchase_value_is_unrated
test_overlay_over_no_equipment_is_a_zero_charge_over_zero_records
test_fixture_b_proportional_allocation
test_allocation_with_no_base_is_undefined_not_an_even_split
test_fixture_c_dual_break_even_price
test_cash_price_is_strictly_lower_even_with_full_coverage_and_no_overlay
test_unclassified_cost_sits_inside_total_and_outside_cash
test_break_even_price_is_undefined_without_marketable_mass[0.0]
test_break_even_price_is_undefined_without_marketable_mass[None]
test_allocated_fixed_cost_may_be_absent
test_fixture_d_yield_sensitivity_matrix
test_sensitivity_accepts_caller_supplied_percentages
test_sensitivity_over_zero_baseline_yields_undefined_prices
test_fixture_e_operating_expense_ratio
test_operating_expense_ratio_excludes_the_depreciation_overlay
test_operating_expense_ratio_is_undefined_at_zero_revenue
test_fixture_f_partial_budget_solar_dryer_is_worth_it
test_fixture_f_negative_partial_budget_is_returned_signed
test_fixture_g_olympic_average_discards_one_instance_not_all_ties
test_fixture_g_five_maize_seasons
test_fixture_g_two_seasons_is_undefined_never_a_two_value_mean
test_olympic_average_over_no_seasons_has_no_average_of_any_kind
test_three_identical_seasons_survive_the_single_instance_rule
test_parity_fixture_is_internally_consistent
test_parity_partial_budget_matches_hand_computed_expectation[PB-1]
test_parity_partial_budget_matches_hand_computed_expectation[PB-2]
test_parity_partial_budget_matches_hand_computed_expectation[PB-3]
test_parity_partial_budget_matches_hand_computed_expectation[PB-4]
test_parity_partial_budget_matches_hand_computed_expectation[PB-5]
test_parity_partial_budget_matches_hand_computed_expectation[PB-6]
test_parity_partial_budget_matches_hand_computed_expectation[PB-7]
test_parity_partial_budget_matches_hand_computed_expectation[PB-8]
test_parity_pb1_sign_is_asserted_separately_from_magnitude
test_parity_pb3_exact_zero_is_not_negative_zero
```

`backend/tests/test_api.py` — 39 tests (endpoint and schema layer):

```
test_equipment_accepts_a_null_depreciation_rate
test_depreciation_rate_is_converted_to_a_fraction_exactly_once
test_mechanization_valid_payload_accepted
test_mechanization_unrecognised_cost_subtype_rejected
test_mechanization_hours_used_out_of_range_rejected
test_non_mechanization_log_keeps_arbitrary_extra_data
test_mechanization_without_extra_data_accepted_and_unclassified
test_enterprise_cost_structure_matches_fixture_a
test_enterprise_cost_structure_reads_subtype_only_for_mechanization
test_enterprise_reversal_excluded_from_buckets_and_does_not_lower_coverage
test_enterprise_operating_expense_ratio_is_reported_on_cost_structure
test_enterprise_operating_expense_ratio_is_null_for_an_input_only_crop
test_enterprise_operating_expense_ratio_excludes_recorded_depreciation
test_enterprise_operating_expense_ratio_is_not_on_the_break_even_response
test_enterprise_break_even_prices_null_without_marketable_mass
test_enterprise_break_even_prices_with_marketable_mass_never_collapse
test_enterprise_zero_total_cost_gives_null_coverage
test_enterprise_sensitivity_matrix_is_labelled_conditional
test_enterprise_period_defaults_to_the_derived_ledger_span
test_enterprise_specified_period_overrides_the_derived_span
test_enterprise_pinned_period_is_reproducible_when_a_new_log_widens_the_span
test_enterprise_sensitivity_honours_the_pinned_period
test_enterprise_period_days_is_bounded_at_the_edge[0-break-even-price]
test_enterprise_period_days_is_bounded_at_the_edge[0-sensitivity]
test_enterprise_period_days_is_bounded_at_the_edge[-1-break-even-price]
test_enterprise_period_days_is_bounded_at_the_edge[-1-sensitivity]
test_enterprise_period_days_is_bounded_at_the_edge[36526-break-even-price]
test_enterprise_period_days_is_bounded_at_the_edge[36526-sensitivity]
test_enterprise_partial_budget_returns_a_negative_net_change
test_enterprise_yield_baseline_needs_three_seasons
test_enterprise_routes_cross_farm_read_is_404[/api/v1/dss/cost-structure?crop=maize]
test_enterprise_routes_cross_farm_read_is_404[/api/v1/dss/break-even-price?crop=maize]
test_enterprise_routes_cross_farm_read_is_404[/api/v1/dss/sensitivity?crop=maize]
test_enterprise_routes_cross_farm_read_is_404[/api/v1/dss/yield-baseline?crop=maize]
test_enterprise_yield_baseline_mixed_units_is_null_with_a_reason
test_enterprise_yield_baseline_mixed_units_still_reports_its_season_count
test_enterprise_yield_baseline_season_count_distinguishes_two_kinds_of_null
test_enterprise_yield_baseline_three_seasons_discards_one_high_and_one_low
test_enterprise_yield_baseline_reports_a_crop_with_no_yield
```

There is also a frontend counterpart: `src/features/dss/partialBudget.test.ts`,
15 tests, of which 11 are the shared PB-1..PB-8 parity block.

**A defect found while counting, reported and not fixed.** `docs/EVIDENCE.md`
records the command behind the figure "Fixture H (endpoint layer): **32 passed,
96 deselected**" as:

```
python -m pytest backend/tests/test_api.py -q -k "enterprise or mechanis"
```

The token `mechanis` matches **nothing**. Measured on this machine:

```
-k 'enterprise'   -> 32/128 tests collected (96 deselected)
-k 'mechanization'->  6/128 tests collected (122 deselected)
-k 'mechanis'     -> no tests collected (128 deselected)
```

So that command selects only the 32 `enterprise*` tests; the six mechanisation
schema tests it appears to include are silently deselected, and the quoted "32"
is the `enterprise`-only figure with a second clause that contributes zero. The
tests themselves pass — this is a defect in the recorded command and in what the
figure is understood to cover, not in the suite.

### 3.9 Frontend panels

Every panel described for this feature exists.

| Panel | Component file | Present? |
|---|---|---|
| Section container / tier divider | `frontend/src/features/dss/components/EnterpriseEconomics.tsx` | PRESENT |
| Cost structure panel | `frontend/src/features/dss/components/CostStructurePanel.tsx` | PRESENT |
| Dual break-even price | `frontend/src/features/dss/components/BreakEvenPricePanel.tsx` | PRESENT |
| Sensitivity table | `frontend/src/features/dss/components/SensitivityTable.tsx` | PRESENT |
| Partial budget form | `frontend/src/features/dss/components/PartialBudgetForm.tsx` | PRESENT |
| Marketable unit cost line | `frontend/src/features/dashboard/components/DecisionSupport.tsx:85` | PRESENT |

All four panels are mounted through `EnterpriseEconomics`, which is rendered at
`frontend/src/features/dss/DSSPredictPage.tsx:236`. There is **no** frontend
surface for `GET /dss/yield-baseline` — no component references it (see 10.2).

### 3.10 Which phases have landed

Two readings of "eight phases" are possible, and they do not agree, so both are
reported rather than one being chosen.

**Reading A — the ticket's own phase numbering.** `.scratch/TICKET_enterprise_economics.md`
defines a Phase 0 reading step and Phases 1–6, not eight. Against artifacts:

| Phase | State | Justifying artifact |
|---|---|---|
| 0 — Read before writing code | CANNOT DETERMINE | A reading step leaves no artifact. Nothing in the repository records that the summary was produced. |
| 1 — Domain and documentation | **LANDED** | `CONTEXT.md` carries an entire `### Cost structure` heading with 11 terms (8.4); ADR-0002 exists and is Accepted (3.7). |
| 2 — Schema and classification | **LANDED** | `CostBehaviour`, `MechanizationParams`, `COST_BEHAVIOUR`, `cost_behaviour_for` all present (3.2); conditional edge validation present and tested (3.3). One residue: the `TODO(cite)` above `COST_BEHAVIOUR` is unresolved. |
| 3 — Enterprise service | **LANDED** | All eight functions present (3.1); module at 100% statement coverage; 40 unit tests including fixtures A–G (3.8). |
| 4 — Endpoints | **LANDED** | Five routes registered (3.4), all returning 2xx live (6.6), 34 endpoint tests (3.8). |
| 5 — Multi-crop seed | **LANDED** | `seed_bioprocess_demo.py` posts five crops and two assets with a full cost-subtype spread (5.2); the seeded farm holds 28 logs and 2 equipment rows (5.3). |
| 6 — Frontend | **PARTIAL** | Four of the four named panels plus the marketable unit-cost line are present (3.9). Nothing renders `/dss/yield-baseline`, which Phase 4 shipped — the endpoint has no user-reachable surface (7.3, 10.2). |

**Reading B — the eight numbered sub-items 4.1–4.8 inside Phase 3.** Each has a
function, and each has at least one hand-computed fixture test:

| Sub-item | Function | State | Justification |
|---|---|---|---|
| 4.1 Cost structure summary | `cost_structure` (line 39) | LANDED | `test_fixture_a_classification_and_coverage`; live at `/dss/cost-structure` (6.6) |
| 4.2 Depreciation overlay | `depreciation_overlay` (line 84) | LANDED | `test_fixture_b_depreciation_overlay`; live `period_fixed_cost_ngn` (6.6) |
| 4.3 Proportional allocation | `allocate_fixed_cost` (line 132) | LANDED | `test_fixture_b_proportional_allocation`; live `allocated_fixed_ngn` (6.6) |
| 4.4 Dual break-even price | `break_even_prices` (line 178) | LANDED | `test_fixture_c_dual_break_even_price`; both fields live (6.6) |
| 4.5 Yield sensitivity | `yield_sensitivity` (line 246) | LANDED | `test_fixture_d_yield_sensitivity_matrix`; five live rows (6.6) |
| 4.6 Operating expense ratio | `operating_expense_ratio_pct` (line 290) | LANDED | `test_fixture_e_operating_expense_ratio`; live on cost-structure (6.6) |
| 4.7 Partial budget | `partial_budget` (line 318) | LANDED | Fixture F plus the PB-1..PB-8 parity block, both suites (3.8) |
| 4.8 Olympic average yield | `olympic_average_yield` (line 359) | LANDED | Fixture G including the tie trap; live at `/dss/yield-baseline` (6.6) — **but with no frontend surface** |

Nothing in either reading is "not started". The single incomplete item under
both readings is the frontend surface for the yield baseline.

---

## 4. Bioprocess — actual implementation state

### 4.1 `backend/app/services/bioprocess_service.py`

**Confirmed present** — 68 statements, 100% statement coverage (Section 2.3).
Fourteen public functions, signatures as written (there are no leading-underscore
private helpers):

```
backend/app/services/bioprocess_service.py:46
def wb_to_db(moisture_wb: float) -> float:

backend/app/services/bioprocess_service.py:51
def db_to_wb(moisture_db: float) -> float:

backend/app/services/bioprocess_service.py:58
def dry_matter_kg(mass_in_kg: float, moisture_initial_wb: float) -> float:

backend/app/services/bioprocess_service.py:63
def expected_outlet_mass_kg(
    mass_in_kg: float, moisture_initial_wb: float, moisture_final_wb: float
) -> float:

backend/app/services/bioprocess_service.py:71
def process_loss(
    mass_in_kg: float,
    moisture_initial_wb: float,
    moisture_final_wb: float,
    mass_out_actual_kg: float,
) -> dict:

backend/app/services/bioprocess_service.py:90
def water_removed_kg(
    mass_in_kg: float,
    mass_out_actual_kg: float,
    moisture_initial_wb: float,
    moisture_final_wb: float,
) -> float:

backend/app/services/bioprocess_service.py:130
def drying_rate_kg_h(water_removed: float, drying_time_hours: float) -> float:

backend/app/services/bioprocess_service.py:135
def specific_drying_rate(
    water_removed: float, dry_matter: float, drying_time_hours: float
) -> float:

backend/app/services/bioprocess_service.py:144
def moisture_ratio_final(moisture_initial_wb: float, moisture_final_wb: float) -> float:

backend/app/services/bioprocess_service.py:149
def newton_k(
    moisture_initial_wb: float, moisture_final_wb: float, drying_time_hours: float
) -> float:

backend/app/services/bioprocess_service.py:159
def page_fit(
    moisture_initial_wb: float,
    readings: Sequence[tuple[float, float]],
    min_readings: int = 3,
) -> Optional[dict]:

backend/app/services/bioprocess_service.py:219
def safe_storage_threshold(crop: Optional[str]) -> Optional[float]:

backend/app/services/bioprocess_service.py:227
def is_safe_to_store(crop: Optional[str], moisture_final_wb: float) -> Optional[bool]:

backend/app/services/bioprocess_service.py:238
def compute_drying_metrics(
    mass_in_kg: float,
    mass_out_kg: float,
    moisture_initial_wb: float,
    moisture_final_wb: float,
    drying_time_hours: float,
    crop: Optional[str] = None,
    readings: Optional[Sequence[tuple[float, float]]] = None,
) -> dict:
```

### 4.2 Crop safe-storage threshold constant, verbatim with its TODO

```
backend/app/services/bioprocess_service.py:22-41
# Indicative safe-storage moisture ceilings (% wet basis) for tropical storage.
# The parenthetical qualifiers (paddy, shelled, chips) describe the form the
# figure applies to; the dict key is the crop name as entered on a log.
# TODO(cite): FAO / NSPRI / IITA post-harvest handling guidance — replace this
# comment with the actual citation before the thesis; an examiner will ask.
SAFE_STORAGE_MOISTURE_WB: dict[str, float] = {
    "maize": 13.0,
    "rice": 14.0,       # paddy
    "sorghum": 12.5,
    "millet": 12.0,
    "cowpea": 12.0,
    "groundnut": 7.0,   # shelled
    "soybean": 12.0,
    "cassava": 12.0,    # chips
    "yam": 12.0,        # chips
}

# A |process loss| beyond this fraction is flagged as a data-quality signal, not
# rejected — measurement error and genuine handling loss both live here.
PROCESS_LOSS_WARN_PCT = 5.0
```

The `TODO(cite)` is unresolved: the thresholds carry no citation in the repository.

### 4.3 Bioprocess routes

`backend/app/api/endpoints/bioprocess.py:25` sets
`router = APIRouter(prefix="/bioprocess", tags=["bioprocess"])`, registered at
`backend/app/api/router.py:11`.

| Method | Path | Handler |
|---|---|---|
| GET | `/api/v1/bioprocess/summary` | `bioprocess.py:47 get_bioprocess_summary` |
| GET | `/api/v1/bioprocess/{log_id}` | `bioprocess.py:134 get_drying_run` |

Two routes, both reads. Drying runs are **created** through the shared ledger
write path (`POST /api/v1/ledger/logs` with `activity_type: "bioprocess"`);
there is no POST on this router.

### 4.4 Bioprocess tests by name

`backend/tests/test_bioprocess_service.py` — 11 tests:

```
test_fixture_a_maize_with_process_loss
test_fixture_b_rice_clean_balance
test_fixture_c_page_fit_exact_recovery
test_page_fit_insufficient_readings_returns_none
test_page_fit_drops_out_of_range_readings
test_basis_conversion_roundtrip
test_safe_storage_known_crops
test_safe_storage_unknown_crop_is_none_never_false
test_process_loss_warning_flag
test_compute_metrics_with_readings_and_unknown_crop
test_fixture_f_water_removed_is_a_water_balance_not_a_mass_difference
```

`backend/tests/test_api.py` — 17 further tests exercising the bioprocess write
path, detail read and summary:

```
test_bioprocess_valid_payload_accepted
test_bioprocess_missing_payload_rejected
test_bioprocess_mass_out_exceeds_mass_in_rejected
test_bioprocess_final_moisture_not_below_initial_rejected
test_bioprocess_nonpositive_mass_rejected
test_bioprocess_moisture_out_of_range_rejected
test_bioprocess_readings_not_strictly_increasing_rejected
test_bioprocess_reading_outside_moisture_band_rejected
test_non_bioprocess_log_keeps_arbitrary_extra_data
test_bioprocess_create_zero_cost_still_pairs_transaction
test_bioprocess_detail_returns_params_and_metrics
test_bioprocess_detail_cross_farm_is_404
test_bioprocess_detail_non_bioprocess_log_is_404
test_bioprocess_detail_on_reversal_contra_is_404
test_bioprocess_summary_aggregates_per_crop
test_bioprocess_summary_excludes_reversed_run
test_bioprocess_summary_crop_filter
```

**28 bioprocess tests in the backend.** Frontend:
`src/features/farm-records/dryingParams.test.ts`, 10 tests over
`buildDryingParams` (payload construction and its eight rejection cases).

### 4.5 Frontend drying-parameters entry form

**It exists.** `frontend/src/features/farm-records/DryingFields.tsx`, exported at
line 24, rendered conditionally at
`frontend/src/features/farm-records/FarmRecordCreateForm.tsx:196`:

```tsx
{isDrying && <DryingFields value={drying} onChange={setDrying} label={label} field={field} />}
```

with `const isDrying = form.activity_type === 'bioprocess';` at line 72.

Fields collected: drying method (select — Sun drying / Solar dryer / Mechanical
dryer / Ambient-shade, lines 10–14), mass in (kg), mass out (kg), moisture in
(% wet basis), moisture out (% wet basis), drying time (hours), air temperature
(°C, marked optional).

**It does not collect intermediate time/moisture readings.** There is no
`readings` input anywhere in `DryingFields.tsx`. A run entered through the
interface therefore reaches the backend with no readings array, `page_fit`
returns `None`, and the result panel falls back to its hint
"Page fit needs 3+ intermediate readings" (`DryingRunResult.tsx:106`). The
readings on the two seeded runs came from the seed script, not the interface.

### 4.6 Is BIOPROCESS selectable in the frontend entry form today?

**Yes.** The code that determines the selectable options:

```tsx
frontend/src/features/farm-records/FarmRecordCreateForm.tsx:18-26
const CATEGORIES: { value: Category; label: string }[] = [
  { value: 'yield', label: 'Crop yield / sale' },
  { value: 'seed', label: 'Seed' },
  { value: 'fertilizer', label: 'Fertilizer' },
  { value: 'labour', label: 'Labour' },
  { value: 'mechanization', label: 'Mechanization' },
  { value: 'bioprocess', label: 'Post-harvest drying' },
  { value: 'other', label: 'Other' },
];
```

Rendered at lines 150–152:

```tsx
<select value={form.activity_type} onChange={(e) => setActivity(e.target.value as Category)} style={field}>
  {CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
</select>
```

The option is labelled "Post-harvest drying" rather than "Bioprocess", but its
value is `bioprocess` and it is present and selectable.

### 4.7 Drying-curve chart

**It does not exist.** No component under `frontend/src/` draws a drying curve;
searching the frontend source for `drying.curve` / `dryingCurve` returns no
component. The only readings-related frontend reference is the type declaration
at `frontend/src/types/domain.ts:282`.

Charting library in `frontend/package.json`: **`recharts` ^3.8.1** (runtime
dependency). It is used by three components only —
`features/dashboard/components/PnlChart.tsx`,
`features/dashboard/components/CostBreakdown.tsx` and, lazily,
`features/dashboard/DashboardPage.tsx`. `SensitivityTable.tsx:24` mentions it
only in a comment explaining the deliberate choice not to chart:

```
// recharts is already a dependency and drawing this as a chart would have been
```

---

## 5. Seed data and database contents

### 5.1 Seed scripts under `backend/scripts/`

```
backend/scripts/seed_bioprocess_demo.py
```

**One** seed script (the directory otherwise holds only `__pycache__`). There is
no other seeding entry point in `backend/scripts/`.

### 5.2 What the primary seed script creates

Read from `backend/scripts/seed_bioprocess_demo.py`. It posts through the real
API (`POST /api/v1/auth/register` or `/login`, then `POST /api/v1/equipment/` and
`POST /api/v1/ledger/logs`), so every log creates one paired financial
transaction. Every log carries a fixed `client_id`, making a re-run idempotent.

**Farm:** one — `"Demo Farm"`, user `demo-bioprocess-v2@test.example`, password
`demo-bioprocess-pw` (lines 67–68, 476).

**Crops:** five — maize, cassava, tomato, cowpea, sorghum.

**Equipment: two rows** (lines 85–104).

| Name | Model | Purchase price | Depreciation rate |
|---|---|---|---|
| Massey Ferguson 375 tractor | MF375 | ₦4,200,000.00 | 12.5 %/yr |
| Multi-crop thresher | IAR T-90 | ₦850,000.00 | `None` — unrated, deliberately |

**Operational logs: 28**, each with a paired financial transaction (so
**28 financial transactions**). By activity type: 4 SEED, 4 FERTILIZER,
6 LABOUR, 8 MECHANIZATION, 3 YIELD, 2 BIOPROCESS, 1 OTHER.

Every seeded log with its exact amount:

| # | Activity | Crop | Amount (₦) | Type | Payload of note |
|---|---|---|---|---|---|
| 1 | yield | maize | 45,000.00 | credit | quantity 100.0 kg |
| 2 | bioprocess | maize | 3,500.00 | debit | drying run (below) |
| 3 | seed | cassava | 8,400.00 | debit | — |
| 4 | fertilizer | cassava | 26,000.00 | debit | — |
| 5 | labour | cassava | 21,000.00 | debit | land clearing / ridging |
| 6 | labour | cassava | 24,000.00 | debit | weeding |
| 7 | labour | cassava | 15,000.00 | debit | harvesting / heaping |
| 8 | yield | cassava | 178,600.00 | credit | quantity 1,880.0 kg |
| 9 | seed | tomato | 6,800.00 | debit | — |
| 10 | fertilizer | tomato | 29,800.00 | debit | — |
| 11 | labour | tomato | 27,000.00 | debit | — |
| 12 | other | tomato | 11,700.00 | debit | insecticide |
| 13 | mechanization | tomato | 37,600.00 | debit | **no `extra_data`** → unclassified |
| 14 | seed | cowpea | 23,000.00 | debit | — |
| 15 | fertilizer | cowpea | 38,500.00 | debit | — |
| 16 | labour | cowpea | 33,000.00 | debit | — |
| 17 | mechanization | cowpea | 47,500.00 | debit | `FUEL`, `hours_used 6.0`, tractor |
| 18 | mechanization | cowpea | 19,200.00 | debit | `LUBRICANTS`, tractor |
| 19 | mechanization | cowpea | 26,500.00 | debit | `REPAIRS`, tractor |
| 20 | mechanization | cowpea | 27,000.00 | debit | `MACHINERY_HIRE`, `hours_used 3.0`, no equipment id |
| 21 | mechanization | cowpea | 18,000.00 | debit | `DEPRECIATION`, tractor — a *recorded* charge, not the overlay |
| 22 | mechanization | cowpea | 21,000.00 | debit | **no `extra_data`** → unclassified (legacy-shaped) |
| 23 | yield | cowpea | 624,950.00 | credit | quantity 480.0 kg |
| 24 | bioprocess | cowpea | 14,000.00 | debit | drying run (below) |
| 25 | seed | sorghum | 7,200.00 | debit | — |
| 26 | fertilizer | sorghum | 52,000.00 | debit | — |
| 27 | labour | sorghum | 42,000.00 | debit | — |
| 28 | mechanization | sorghum | 18,750.00 | debit | `FUEL`, `hours_used 4.5`, tractor |

**Drying runs: two.**

Maize (lines 117–133): `process_type DRYING`, `method SOLAR_DRYER`,
`mass_in_kg 100.0`, `mass_out_kg 84.0`, `moisture_initial_wb 25.0`,
`moisture_final_wb 13.0`, `drying_time_hours 10.0`, readings
`[(2.0, 21.0), (5.0, 17.0), (8.0, 14.5)]`.

Cowpea (lines 360–376): `process_type DRYING`, `method SOLAR_DRYER`,
`mass_in_kg 480.0`, `mass_out_kg 431.0`, `moisture_initial_wb 18.0`,
`moisture_final_wb 11.5`, `drying_time_hours 14.0`, readings
`[(3.0, 16.2), (6.0, 14.6), (10.0, 12.9)]`.

The script's docstring (lines 50–54) states that the maize figures — 100 kg,
84 kg, ₦3,500, ₦45,000 — are quoted in a defended chapter as ₦35.00/kg harvested
and ₦41.67/kg marketable and must not move.

### 5.3 Live database, per farm

Queried against the running `agrip-db-1` container
(`docker exec agrip-db-1 psql -U postgres -d agriprofit`). Reported exactly as
found; nothing was reseeded, migrated or cleaned.

The database holds **14 farms**, not one. The seeded demo farm is id 26; thirteen
other farms are present from earlier manual and exploratory use.

```
 id |       name        | logs | txns | equipment
----+-------------------+------+------+-----------
  1 | Legacy Farm       |   34 |   34 |         1
  3 | Madlabs Farm      |    4 |    4 |         0
  4 | Sunrise Farm      |    9 |    9 |         0
  5 | lead farm         |    0 |    0 |         0
 17 | Demo Farm         |    2 |    2 |         0
 19 | Zelle Farm        |    7 |    7 |         0
 20 | Dash Check Farm   |    3 |    3 |         0
 21 | Unit Check Farm   |    5 |    5 |         0
 22 | Empty Bucket Farm |    4 |    4 |         0
 23 | Sun Dry Farm      |    3 |    3 |         0
 24 | Beeper Farms      |    5 |    5 |         0
 25 | Break Even Farm   |    5 |    5 |         0
 26 | Demo Farm         |   28 |   28 |         2
 27 | London Farm       |    0 |    0 |         0
(14 rows)
```

There are **two** farms named "Demo Farm" (ids 17 and 26). Id 26 is the one the
current seed script targets; id 17 is a two-log remnant of an earlier seed.

Operational logs by activity type, per farm:

```
 id |       name        | activity_type | count
----+-------------------+---------------+-------
  1 | Legacy Farm       | SEED          |     6
  1 | Legacy Farm       | FERTILIZER    |     8
  1 | Legacy Farm       | LABOUR        |     6
  1 | Legacy Farm       | MECHANIZATION |     6
  1 | Legacy Farm       | YIELD         |     8
  3 | Madlabs Farm      | YIELD         |     4
  4 | Sunrise Farm      | SEED          |     3
  4 | Sunrise Farm      | YIELD         |     6
 17 | Demo Farm         | YIELD         |     1
 17 | Demo Farm         | BIOPROCESS    |     1
 19 | Zelle Farm        | FERTILIZER    |     2
 19 | Zelle Farm        | YIELD         |     5
 20 | Dash Check Farm   | FERTILIZER    |     2
 20 | Dash Check Farm   | YIELD         |     1
 21 | Unit Check Farm   | YIELD         |     5
 22 | Empty Bucket Farm | FERTILIZER    |     1
 22 | Empty Bucket Farm | YIELD         |     1
 22 | Empty Bucket Farm | OTHER         |     2
 23 | Sun Dry Farm      | BIOPROCESS    |     1
 23 | Sun Dry Farm      | OTHER         |     2
 24 | Beeper Farms      | FERTILIZER    |     3
 24 | Beeper Farms      | YIELD         |     1
 24 | Beeper Farms      | BIOPROCESS    |     1
 25 | Break Even Farm   | FERTILIZER    |     2
 25 | Break Even Farm   | YIELD         |     3
 26 | Demo Farm         | SEED          |     4
 26 | Demo Farm         | FERTILIZER    |     4
 26 | Demo Farm         | LABOUR        |     6
 26 | Demo Farm         | MECHANIZATION |     8
 26 | Demo Farm         | YIELD         |     3
 26 | Demo Farm         | BIOPROCESS    |     2
 26 | Demo Farm         | OTHER         |     1
(32 rows)
```

Farms 5 (`lead farm`) and 27 (`London Farm`) hold no logs and so do not appear
in this grouping. Equipment exists on two farms only — farm 1 (1 row) and farm 26
(2 rows), **3 rows in the whole database**.

### 5.4 Every distinct crop in the database

Revenue and expense totals across **all** farms:

```
  crop   | revenue | expenses
---------+---------+----------
 cassava |  178600 |    94400
 cowpea  |  624950 |   267700
 maize   |  371000 |   158000
 rice    |   73000 |        0
 sorghum |    3000 |   124950
 tomato  |       0 |   112900
         | 2093000 |  1213000
(7 rows)
```

The last row is logs with a NULL crop — ₦2,093,000 revenue and ₦1,213,000
expense, the largest bucket in the database by value and attributed to no crop
at all.

Yield quantity by crop and unit (YIELD logs with a non-null quantity):

```
  crop   |  unit  | qty  | count
---------+--------+------+-------
 cassava | kg     | 1880 |     1
 cowpea  | kg     |  480 |     1
 maize   | bags   |   36 |     3
 maize   | kg     |  700 |     7
 maize   | litres |    5 |     1
 rice    | bags   |    5 |     2
 rice    | kg     |  100 |     2
 rice    |  Kg    |   25 |     1
 sorghum | kg     |   40 |     1
 sorghum |        |   30 |     1
         | bags   |   12 |     1
         | unit   |    1 |     1
(12 rows)
```

Reported as found: maize carries three units across the database (`kg`, `bags`,
`litres`); rice carries `kg`, `bags` and a distinct ` Kg` with a leading space
and different capitalisation — three unit strings for what is presumably two
units; sorghum has one row with an empty unit. Tomato has no yield row, by
design. These are database-wide figures. Farm 26 alone is unit-clean, which is
why the DSS response in 6.1 shows one unit per crop.

### 5.5 Operational logs with a non-null, non-empty `extra_data`

**11 logs**, database-wide:

```
 activity_type | count
---------------+-------
 MECHANIZATION |     6
 BIOPROCESS    |     5
(2 rows)
```

No other activity type carries a payload. The query excluded SQL `NULL`, the
JSON literal `null`, `{}` and `""`.

### 5.6 Equipment depreciation rates

Across the three equipment rows in the database:

```
 bucket  | count
---------+-------
 null    |     1
 nonzero |     2
(2 rows)
```

- Non-zero rate: **2**
- Zero rate: **0**
- Null rate: **1**

Zero is absent by construction — the schema rejects it:

```
backend/app/schemas/schemas.py:213-215
    depreciation_rate: Optional[float] = Field(
        default=None, gt=0, le=100, description="Annual depreciation rate, percent per year"
    )
```

with the reasoning recorded in ADR-0002 and commit `0543cd9`.

### 5.7 Reversals

```
 reversal_logs | logs_reversed
---------------+---------------
             7 |             7
```

**7 reversal (contra) logs**, offsetting **7 distinct** original logs. Every
reversal points at a different target; nothing has been reversed twice.

---

## 6. Live endpoint output

The stack was running throughout (`docker ps`: `agrip-db-1` postgres:15,
`agrip-backend-1` on :8000, `agrip-frontend-1` on :5173, `agrip-frontend-prod-1`
on :4173). All responses below are verbatim, complete and unedited.

Authentication (used for every call in this section):

```
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo-bioprocess-v2@test.example","password":"demo-bioprocess-pw"}'
```

HTTP 200. The `access_token` from that response is held in `$T` below. The user
is id 25, `farm_id` 26 ("Demo Farm"), confirmed by
`SELECT id,email,farm_id FROM users WHERE email='demo-bioprocess-v2@test.example';`

### 6.1 DSS per-crop breakdown

```
curl -s -H "Authorization: Bearer $T" http://localhost:8000/api/v1/dss/decision-support
```

HTTP 200.

```json
{"crops":[{"crop":"cowpea","revenue":624950.0,"expenses":267700.0,"gross_margin":357250.0,"yield_quantity":480.0,"yield_unit":"kg","yield_by_unit":[{"unit":"kg","quantity":480.0}],"unit_cost_of_production":557.7083333333334,"marketable_mass_kg":431.0,"unit_cost_per_kg_marketable":621.1136890951276,"break_even_yield":205.6100488039043,"break_even_unit":"kg"},{"crop":"cassava","revenue":178600.0,"expenses":94400.0,"gross_margin":84200.0,"yield_quantity":1880.0,"yield_unit":"kg","yield_by_unit":[{"unit":"kg","quantity":1880.0}],"unit_cost_of_production":50.212765957446805,"marketable_mass_kg":null,"unit_cost_per_kg_marketable":null,"break_even_yield":993.6842105263158,"break_even_unit":"kg"},{"crop":"maize","revenue":45000.0,"expenses":3500.0,"gross_margin":41500.0,"yield_quantity":100.0,"yield_unit":"kg","yield_by_unit":[{"unit":"kg","quantity":100.0}],"unit_cost_of_production":35.0,"marketable_mass_kg":84.0,"unit_cost_per_kg_marketable":41.666666666666664,"break_even_yield":7.777777777777778,"break_even_unit":"kg"},{"crop":"tomato","revenue":0.0,"expenses":112900.0,"gross_margin":-112900.0,"yield_quantity":0.0,"yield_unit":null,"yield_by_unit":[],"unit_cost_of_production":null,"marketable_mass_kg":null,"unit_cost_per_kg_marketable":null,"break_even_yield":null,"break_even_unit":null},{"crop":"sorghum","revenue":0.0,"expenses":119950.0,"gross_margin":-119950.0,"yield_quantity":0.0,"yield_unit":null,"yield_by_unit":[],"unit_cost_of_production":null,"marketable_mass_kg":null,"unit_cost_per_kg_marketable":null,"break_even_yield":null,"break_even_unit":null}],"overall":{"revenue":848550.0,"expenses":598450.0,"gross_margin":250100.0}}
```

Crops are returned already ranked by descending gross margin, then by name —
`backend/app/services/dss_service.py:256`,
`crops.sort(key=lambda c: (-c["gross_margin"], c["crop"]))`.

### 6.2 DSS break-even endpoint, if separate

**N/A as a separate endpoint for the retrospective break-even YIELD.** There is
no dedicated route for it: `break_even_yield` / `break_even_unit` are fields on
the `/dss/decision-support` payload above (visible on cowpea, cassava and maize;
null on tomato and sorghum, which have no revenue). Computed at
`backend/app/services/dss_service.py:226-246`.

The separate break-even routes that do exist are the two conditional break-even
PRICES on `/dss/break-even-price`, reported under 6.6 below, since Section 3.4
found them registered as enterprise-economics routes.

### 6.3 Model-info / ML metrics endpoint

```
curl -s -H "Authorization: Bearer $T" http://localhost:8000/api/v1/dss/model
```

HTTP 200.

```json
{"trained":true,"features":["rainfall","fertilizer_used","soil_ph","crop"],"numeric_features":["rainfall","fertilizer_used","soil_ph"],"categorical_features":["crop"],"crops":["maize","rice","sorghum","soybean","cassava"],"target":"yield_t_ha","target_unit":"t/ha","bounds":{"rainfall":[300.0,2000.0],"fertilizer_used":[0.0,120.0],"soil_ph":[4.5,8.5]},"model":"Pipeline(OneHotEncoder + RandomForestRegressor)","n_estimators":200,"n_samples":6000,"metrics":{"r2":0.9762,"mae":0.2414},"feature_importances":{"crop":0.3445,"rainfall":0.2845,"fertilizer_used":0.1231,"soil_ph":0.2479},"trained_at":"2026-07-01T19:03:34.593275+00:00"}
```

### 6.4 `GET /bioprocess/summary` (all crops)

```
curl -s -H "Authorization: Bearer $T" http://localhost:8000/api/v1/bioprocess/summary
```

HTTP 200.

```json
{"crops":[{"crop":"cowpea","drying_runs":1,"total_mass_in_kg":480.0,"total_marketable_mass_kg":431.0,"total_water_removed_kg":36.83500000000001,"mean_drying_rate_kg_h":2.631071428571429,"mean_newton_k_by_method":{"SOLAR_DRYER":0.03745057337689937},"safe_storage_share":1.0},{"crop":"maize","drying_runs":1,"total_mass_in_kg":100.0,"total_marketable_mass_kg":84.0,"total_water_removed_kg":14.08,"mean_drying_rate_kg_h":1.408,"mean_newton_k_by_method":{"SOLAR_DRYER":0.08023464725249374},"safe_storage_share":1.0}]}
```

### 6.5 `GET /bioprocess/{id}` for the seeded maize drying run

The seeded maize drying run is log id **1049** (established by
`SELECT id,crop FROM operational_logs WHERE farm_id=26 AND activity_type='BIOPROCESS' ORDER BY id;`
→ `1049 | maize`, `1071 | cowpea`).

```
curl -s -H "Authorization: Bearer $T" http://localhost:8000/api/v1/bioprocess/1049
```

HTTP 200.

```json
{"id":1049,"crop":"maize","params":{"process_type":"DRYING","method":"SOLAR_DRYER","mass_in_kg":100.0,"mass_out_kg":84.0,"moisture_initial_wb":25.0,"moisture_final_wb":13.0,"drying_time_hours":10.0,"air_temperature_c":null,"readings":[{"time_hours":2.0,"moisture_wb":21.0},{"time_hours":5.0,"moisture_wb":17.0},{"time_hours":8.0,"moisture_wb":14.5}]},"metrics":{"dry_matter_kg":75.0,"mass_out_expected_kg":86.20689655172414,"process_loss_kg":2.2068965517241423,"process_loss_pct":2.560000000000005,"process_loss_warning":false,"water_removed_kg":14.08,"drying_rate_kg_h":1.408,"specific_drying_rate":0.018773333333333333,"moisture_initial_db":33.333333333333336,"moisture_final_db":14.942528735632184,"moisture_ratio_final":0.44827586206896547,"newton_k":0.08023464725249374,"page":{"n":0.7955759483894727,"k":0.13162235661616137,"r2_linear":0.99808005532865,"n_used":3,"n_dropped":0},"safe_storage":true,"safe_storage_threshold_wb":13.0}}
```

### 6.6 Every enterprise-economics endpoint found registered in 3.4

All five are registered and all five return HTTP 200.

**GET /dss/cost-structure**

```
curl -s -H "Authorization: Bearer $T" "http://localhost:8000/api/v1/dss/cost-structure?crop=maize"
```

HTTP 200.

```json
{"crops":[{"variable_cost":3500.0,"semi_variable_cost":0.0,"fixed_cost_recorded":0.0,"unclassified_cost":0.0,"total_recorded_cost":3500.0,"cash_cost":3500.0,"classification_coverage_pct":100.0,"revenue_ngn":45000.0,"cash_operating_cost_ngn":3500.0,"operating_expense_ratio_pct":7.777777777777778,"crop":"maize"}],"farm":{"variable_cost":483650.0,"semi_variable_cost":26500.0,"fixed_cost_recorded":18000.0,"unclassified_cost":70300.0,"total_recorded_cost":598450.0,"cash_cost":510150.0,"classification_coverage_pct":88.25298688278052,"revenue_ngn":848550.0,"cash_operating_cost_ngn":580450.0,"operating_expense_ratio_pct":68.40492605032114}}
```

**GET /dss/break-even-price**

```
curl -s -H "Authorization: Bearer $T" "http://localhost:8000/api/v1/dss/break-even-price?crop=maize"
```

HTTP 200.

```json
{"crops":[{"crop":"maize","break_even_price_cash_ngn_per_kg":41.666666666666664,"break_even_price_total_ngn_per_kg":42.36767852721509,"variable_and_semi_variable_cost_ngn":3500.0,"total_recorded_cost_ngn":3500.0,"allocated_fixed_ngn":58.884996286067775,"total_cost_ngn":3558.8849962860677,"marketable_mass_kg":84.0,"classification_coverage_pct":100.0}],"period_days":7.0,"period_source":"derived","period_fixed_cost_ngn":10068.493150684932,"equipment_count":2,"equipment_unrated_count":1,"total_direct_cost_all_crops":598450.0}
```

**GET /dss/sensitivity**

```
curl -s -H "Authorization: Bearer $T" "http://localhost:8000/api/v1/dss/sensitivity?crop=maize"
```

HTTP 200.

```json
{"crops":[{"crop":"maize","conditional":true,"baseline_marketable_mass_kg":84.0,"cash_cost_ngn":3500.0,"total_cost_ngn":3558.8849962860677,"rows":[{"percentage":75,"marketable_mass_kg":63.0,"break_even_price_cash_ngn_per_kg":55.55555555555556,"break_even_price_total_ngn_per_kg":56.49023803628679},{"percentage":90,"marketable_mass_kg":75.6,"break_even_price_cash_ngn_per_kg":46.2962962962963,"break_even_price_total_ngn_per_kg":47.075198363572326},{"percentage":100,"marketable_mass_kg":84.0,"break_even_price_cash_ngn_per_kg":41.666666666666664,"break_even_price_total_ngn_per_kg":42.36767852721509},{"percentage":110,"marketable_mass_kg":92.4,"break_even_price_cash_ngn_per_kg":37.878787878787875,"break_even_price_total_ngn_per_kg":38.516071388377355},{"percentage":125,"marketable_mass_kg":105.0,"break_even_price_cash_ngn_per_kg":33.333333333333336,"break_even_price_total_ngn_per_kg":33.89414282177207}]}],"period_days":7.0,"period_source":"derived"}
```

**POST /dss/partial-budget**

```
curl -s -X POST -H "Authorization: Bearer $T" -H 'Content-Type: application/json' \
  -d '{"added_revenue_ngn":120000,"reduced_cost_ngn":15000,"lost_revenue_ngn":0,"added_cost_ngn":90000}' \
  http://localhost:8000/api/v1/dss/partial-budget
```

HTTP 200.

```json
{"added_revenue_ngn":120000.0,"reduced_cost_ngn":15000.0,"lost_revenue_ngn":0.0,"added_cost_ngn":90000.0,"benefits_ngn":135000.0,"costs_ngn":90000.0,"net_change_ngn":45000.0}
```

(This route is stateless and takes no database session, so the call wrote
nothing. The four input values were chosen for the probe; they are not seeded
data.)

**GET /dss/yield-baseline**

```
curl -s -H "Authorization: Bearer $T" "http://localhost:8000/api/v1/dss/yield-baseline?crop=maize"
```

HTTP 200.

```json
{"crops":[{"crop":"maize","olympic_average_kg":null,"grand_average_kg":100.0,"n_seasons":1,"n_used":0,"n_discarded":0,"unit":"kg","reason":"An Olympic average needs at least 3 seasons; this crop has 1. The grand average is shown instead."}]}
```

### 6.7 Non-2xx responses

**None.** Every endpoint probed in 6.1–6.6 returned HTTP 200. There is nothing
to report under this item.

### 6.8 Maize unit cost figures as returned today

From the 6.1 response, the maize crop object:

| Basis | Field | Value as returned |
|---|---|---|
| Wet / harvest basis | `unit_cost_of_production` | `35.0` |
| Marketable basis | `unit_cost_per_kg_marketable` | `41.666666666666664` |

- **Wet basis: exact match.** `35.0` is ₦35.00/kg exactly — no difference.
- **Marketable basis: not an exact match, and cannot be.**
  `41.666666666666664` is the double-precision value of 3500 ÷ 84 = 41.6̄. The
  quoted ₦41.67/kg is that value rounded to two decimal places. The difference
  is `41.67 − 41.666666666666664 = 0.003333333333336` naira, i.e. about
  0.33 kobo, and it is a rounding artefact rather than a discrepancy: the API
  returns full float precision and the interface formats to two decimals
  (`nairaExact` at
  `frontend/src/features/dashboard/components/DecisionSupport.tsx:26-27`).

The same `41.666666666666664` appears as `break_even_price_cash_ngn_per_kg` in
6.6, since maize has no semi-variable, fixed or unclassified cost — its cash
cost and its total recorded cost are both ₦3,500.

---

## 7. Frontend — what a user can actually reach

### 7.1 Route definitions

The authenticated route table, verbatim:

```tsx
frontend/src/app/router.tsx:23-35
export const AppRoutes: FC<{ isOnline: boolean; pendingCount: number; onRecordChange: () => void }> = ({ isOnline, pendingCount, onRecordChange }) => (
  <Suspense fallback={<RouteFallback />}>
    <Routes>
      <Route path="/" element={<DashboardPage isOnline={isOnline} pendingCount={pendingCount} />} />
      <Route path="/records" element={<FarmRecordsPage isOnline={isOnline} onRecordChange={onRecordChange} />} />
      <Route path="/reports" element={<ReportsPage />} />
      <Route path="/equipment" element={<EquipmentPage />} />
      <Route path="/dss" element={<DSSPredictPage />} />
      <Route path="/investors" element={<InvestorsPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </Suspense>
);
```

One further route is handled outside this table, by a path match rather than a
`<Route>`, in `frontend/src/App.tsx:37-41`:

```tsx
// the existing AppShell/AppRoutes tree is left untouched (no nested <Routes>).
...
    return <PublicInvestorReport token={shareMatch.params.token} />;
```

matching `/investor/:token` — the unauthenticated public share view.

### 7.2 Top-level page component per route

| Route | Page component file |
|---|---|
| `/` | `frontend/src/features/dashboard/DashboardPage.tsx` |
| `/records` | `frontend/src/features/farm-records/FarmRecordsPage.tsx` |
| `/reports` | `frontend/src/features/reports/ReportsPage.tsx` |
| `/equipment` | `frontend/src/features/equipment/EquipmentPage.tsx` |
| `/dss` | `frontend/src/features/dss/DSSPredictPage.tsx` |
| `/investors` | `frontend/src/features/investors/InvestorsPage.tsx` |
| `*` | redirect to `/` (no component) |
| `/investor/:token` (public) | `frontend/src/features/investors/PublicInvestorReport.tsx` |

All six authenticated pages are lazy-loaded (`router.tsx:9-14`), so each is its
own bundle chunk — visible in the build output in 7.5.

### 7.3 Computed figures rendered per page

**`/` — DashboardPage.** Four headline metric cards plus two charts and the
decision-support panel:

```tsx
frontend/src/features/dashboard/DashboardPage.tsx:65  <MetricCard label="Net Profit" value={fmt(summary.gross_margin)} highlight />
frontend/src/features/dashboard/DashboardPage.tsx:66  <MetricCard label="Gross Revenue" value={fmt(summary.revenue)} />
frontend/src/features/dashboard/DashboardPage.tsx:67  <MetricCard label="Operating Cost" value={fmt(summary.expenses)} />
frontend/src/features/dashboard/DashboardPage.tsx:68  <MetricCard label="Profit Margin" value={`${marginPct.toFixed(1)}%`} />
```

plus `PnlChart` and `CostBreakdown` (recharts) and `DecisionSupport`.

**`/records` — FarmRecordsPage.** A ledger table of operational logs with
activity type, crop, quantity/unit, amount and timestamp; a create form
(`FarmRecordCreateForm`), reversal controls, and — after saving a drying run —
`DryingRunResult`. No aggregate figure is computed on this page.

**`/reports` — ReportsPage.** A P&L table over `report.categories`
(`ReportsPage.tsx:67-68`) formatted to two decimals (`ReportsPage.tsx:24`), with
a CSV download (`downloadPnlCsv.ts`).

**`/equipment` — EquipmentPage.** Per-asset purchase price
(`EquipmentPage.tsx:135`) and depreciation rate
(`EquipmentPage.tsx:141`, `Dep. rate {item.depreciation_rate ?? '—'}%/yr`), plus
`MaintenancePanel`. No derived economics.

**`/dss` — DSSPredictPage.** The Tier-2 prediction form and model-quality tiles,
then `EnterpriseEconomics` (line 236) mounting the four Tier-1 panels.

**`/investors` — InvestorsPage.** Share-link management (active/revoked status,
`InvestorsPage.tsx:142`). The investor-facing figures live in
`PublicInvestorReport.tsx`.

#### Item-by-item confirmation

| Figure | Verdict | Location |
|---|---|---|
| Per-crop gross margin table | **PRESENT** | `features/dashboard/components/DecisionSupport.tsx:56` — `<span …>{naira(c.gross_margin)}</span>`, labelled "Gross margin" at line 59; one `CropRow` per crop, mapped at line 152 |
| Crop ranking order | **PRESENT, but as ordering only** | The list is rendered in API order at `DecisionSupport.tsx:152` (`{crops.map((c) => <CropRow key={c.crop} c={c} />)}`), and the API sorts by descending gross margin at `backend/app/services/dss_service.py:256`. **No rank number, position label or "best/worst" marker is rendered** — the ranking is implicit in the order alone. |
| Unit cost on wet basis | **PRESENT** | `DecisionSupport.tsx:64` renders `{unitCostLine(c, cost)}`, whose figure is built at line 34: `` return `Unit cost ${nairaExact(cost)}/${c.yield_unit ?? 'unit'} harvested`; ``, with the denominator named at line 72 (`wet mass as weighed at harvest`) |
| Unit cost on marketable basis per kg | **PRESENT** | `DecisionSupport.tsx:85` — `Unit cost {nairaExact(marketableCost)}/kg marketable`, guarded at line 82 by `{marketableCost != null && (` |
| Retrospective break-even yield | **PRESENT** | `DecisionSupport.tsx:103` — ``Break-even yield was {c.break_even_yield.toLocaleString(undefined, { maximumFractionDigits: 1 })}``, followed at line 104 by the unit and "at the price you got"; guarded at line 100 |
| Either break-even price | **PRESENT — both** | `features/dss/components/BreakEvenPricePanel.tsx:66` — `value={cash == null ? DASH : nairaPerKg(cash)}` under the label "Break-even price to cover cash cost" (line 65); and line 72 — `value={total == null ? DASH : nairaPerKg(total)}` under "Break-even price to cover total cost" (line 71) |
| Classification coverage percentage | **PRESENT** | `features/dss/components/CostStructurePanel.tsx:94` — `<strong>{pct(coverage)}</strong> of this crop&rsquo;s recorded cost carries a cost subtype.`, with an explicit undefined branch at lines 88–91. Also restated on the break-even panel at `BreakEvenPricePanel.tsx:111` |
| Cost behaviour buckets | **PRESENT — all five lines** | `CostStructurePanel.tsx:51/53` Variable cost; `:56/58` Semi-variable cost; `:61/63` Unclassified cost; `:67/69` Allocated fixed cost; `:74/76` Recorded fixed cost (rendered only when non-zero, guarded at line 72); `:79` Total recorded cost |
| Sensitivity table | **PRESENT** | `features/dss/components/SensitivityTable.tsx:90-102` — one `<tr>` per row, `{r.percentage}% of what you recorded` at line 92, cash price at line 99, total price at line 102; the 100% row is highlighted as baseline at line 88 |
| ML model metrics, three display states | **PRESENT — all three** | Loading: `features/dss/DSSPredictPage.tsx:185-186` — `{model === null ? (<p …>Loading model details…</p>)`. Untrained: `:187-196` — `!model.trained || !model.metrics` → "The model has not been trained yet." (line 191). Trained: `:197-213` — R² at line 202 (`{model.metrics.r2.toFixed(4)}`) and MAE at line 209 (`{model.metrics.mae.toFixed(4)}` with `{model.target_unit ?? ''}`) |
| Reversal control and its confirmation dialogue | **PRESENT** | Control: `features/farm-records/FarmRecordsPage.tsx:185-191` — `<button onClick={() => { setReverseError(''); setPendingReversal(log); }} …><Undo2 size={12} /> Reverse</button>`, gated by `canReverse(log)` at line 184 (definition at line 52). Dialogue: mounted at `FarmRecordsPage.tsx:205-210`, component `features/farm-records/ReverseConfirmDialog.tsx` (Escape-to-cancel at line 24, cancel handlers at lines 46 and 85) |
| Offline pending-sync indicator | **PRESENT** | `app/layout/SyncStatus.tsx:45` — `⏳ {pendingCount} pending sync`, guarded at line 43 by `{pendingCount > 0 && (`; also an offline banner at line 40 and a failed-log block at line 48. Mounted at `app/layout/Sidebar.tsx:63` |
| Drying run entry form | **PRESENT** | `features/farm-records/DryingFields.tsx` (export line 24), rendered at `features/farm-records/FarmRecordCreateForm.tsx:196` — `{isDrying && <DryingFields … />}`. **Collects no intermediate readings** (see 4.5) |
| Drying run result panel — water removed, drying rate, process loss, safe-storage verdict | **PRESENT — all four** | `features/farm-records/DryingRunResult.tsx:84` water removed; `:85` drying rate (`${m.drying_rate_kg_h.toFixed(3)} kg/h`); `:86-90` process loss with its predicted-outlet hint; `:78` safe-storage verdict (`<SafeStorageChip safe={m.safe_storage} threshold={m.safe_storage_threshold_wb} />`, three-state at lines 26–30). Mounted at `FarmRecordCreateForm.tsx:138` |
| Drying curve chart | **ABSENT** | No such component exists anywhere under `frontend/src/` (see 4.7) |

### 7.4 Components rendering a figure the API does not return, or hard-coding a value

Two, both reported and neither changed.

**1. A hard-coded 5% threshold in the process-loss warning copy.**

```tsx
frontend/src/features/farm-records/DryingRunResult.tsx:96
          Process loss is over 5% of the predicted outlet mass. Check the weights and moisture readings — this is usually a measurement problem, not lost grain.
```

The *flag* comes from the API (`process_loss_warning`, computed against
`PROCESS_LOSS_WARN_PCT = 5.0` at
`backend/app/services/bioprocess_service.py:41`). The **number 5 in the sentence
is literal frontend text** and is not derived from any field the API returns —
the threshold is not in the response payload at all (see the 6.5 body). If the
backend constant moved, this sentence would silently state the wrong figure.

**2. A hard-coded crop list in the entry form.**

```tsx
frontend/src/features/farm-records/FarmRecordCreateForm.tsx:31
const CROPS = ['maize', 'rice', 'sorghum', 'soybean', 'cassava'];
```

This mirrors the ML model's crop list (returned by `GET /dss/model` as
`"crops":["maize","rice","sorghum","soybean","cassava"]`) but is not fetched
from it. The consequence is visible in the live data: **cowpea and tomato are
seeded crops with full records, and neither can be selected in the entry form**,
because neither appears in this literal. A user cannot today record a cowpea or
tomato log through the interface, though the API accepts both and the DSS
reports on both (6.1). Reported only.

For completeness, the `naira`/`nairaExact` formatters (`DecisionSupport.tsx:14-27`,
`ReportsPage.tsx:24`) round for display but derive every value from the API.
`Dep. rate {item.depreciation_rate ?? '—'}%/yr` (`EquipmentPage.tsx:141`) renders
the stored value, not a default; `EquipmentPage.tsx:16-19` records that a former
hard-coded default rate was removed.

### 7.5 Production bundle

Command:

```
cd frontend && npm run build
```

(`"build": "tsc -b && vite build"` — TypeScript project build then Vite. Exit
clean; one advisory `[PLUGIN_TIMINGS]` note about `rolldown:vite-resolve`.)

Vite's own report:

```
dist/registerSW.js                          0.13 kB
dist/manifest.webmanifest                   0.38 kB
dist/index.html                             0.58 kB │ gzip:   0.34 kB
dist/assets/index-BTa7PcTv.css              2.56 kB │ gzip:   0.92 kB
dist/assets/EmptyState-CIVMO15j.js          0.77 kB │ gzip:   0.44 kB
dist/assets/SectionHeader-DkfKSPgQ.js       0.87 kB │ gzip:   0.41 kB
dist/assets/ReportsPage-DoQkClIS.js         3.63 kB │ gzip:   1.25 kB
dist/assets/InvestorsPage-CjsEXmPs.js       5.93 kB │ gzip:   2.11 kB
dist/assets/DashboardPage-DUNW8Tni.js       8.65 kB │ gzip:   3.00 kB
dist/assets/EquipmentPage-x38yIEdl.js      10.57 kB │ gzip:   3.07 kB
dist/assets/FarmRecordsPage-cUdoHPLr.js    22.20 kB │ gzip:   6.65 kB
dist/assets/CostBreakdown-uJJ4WqhQ.js      29.89 kB │ gzip:   8.86 kB
dist/assets/DSSPredictPage-D1gXQUuV.js     31.03 kB │ gzip:   8.32 kB
dist/assets/PnlChart-D9Ipw8Cj.js           67.85 kB │ gzip:  18.06 kB
dist/assets/CategoricalChart-BQYEvhdc.js  262.00 kB │ gzip:  82.01 kB
dist/assets/index-B-brS2RV.js             406.94 kB │ gzip: 132.28 kB

PWA v1.3.0
mode      generateSW
precache  16 entries (833.66 KiB)
files generated
  dist/sw.js
  dist/workbox-1320db52.js
```

**The main entry bundle is `dist/assets/index-B-brS2RV.js`.** Byte sizes measured
directly with `stat -c%s` and `gzip -9 -c … | wc -c`:

| Asset | Ungzipped (bytes) | Gzipped (bytes) |
|---|---|---|
| **`index-B-brS2RV.js` (entry)** | **406,941** | **130,365** |
| `CategoricalChart-BQYEvhdc.js` | 262,003 | 80,885 |
| `PnlChart-D9Ipw8Cj.js` | 67,857 | 17,864 |
| `DSSPredictPage-D1gXQUuV.js` | 31,039 | 8,313 |
| `CostBreakdown-uJJ4WqhQ.js` | 29,894 | 8,811 |
| `FarmRecordsPage-cUdoHPLr.js` | 22,208 | 6,664 |
| `EquipmentPage-x38yIEdl.js` | 10,571 | 3,076 |
| `DashboardPage-DUNW8Tni.js` | 8,651 | 3,042 |
| `InvestorsPage-CjsEXmPs.js` | 5,932 | 2,141 |
| `ReportsPage-DoQkClIS.js` | 3,635 | 1,280 |
| `index-BTa7PcTv.css` | 2,565 | 954 |
| `SectionHeader-DkfKSPgQ.js` | 876 | 440 |
| `EmptyState-CIVMO15j.js` | 777 | 462 |

Whole `dist/` directory: **892,710 bytes** (`du -sb frontend/dist`).

Note the two gzip figures differ slightly for the entry bundle — Vite reports
132.28 kB, `gzip -9` gives 130,365 bytes. They use different compression
settings; both are stated rather than one being presented as the figure.
`frontend/dist` is git-ignored, so this build changed no tracked file.

---

## 8. Documentation and decision-record state

### 8.1 Every file under `docs/`

```
docs/EVIDENCE.md
docs/adr/0001-bioprocess-drying-parameters-in-extra-data.md
docs/adr/0002-derived-fixed-cost-overlay-and-temporary-domain-assumptions.md
docs/agents/domain.md
docs/agents/issue-tracker.md
docs/agents/triage-labels.md
docs/ch4-data/DATA_PACK.md
docs/ch4-data/bioprocess_summary.json
docs/ch4-data/dss_break_even.json
docs/ch4-data/dss_per_crop.json
docs/ch4-data/model_info.json
docs/ch4-data/screenshot-runsheet.md
docs/perf/2026-08-15/flow-iter1.json
docs/perf/2026-08-15/flow-iter2.json
docs/perf/2026-08-15/flow-iter3.json
docs/perf/2026-08-15/lh-4g-run1.report.html
docs/perf/2026-08-15/lh-4g-run1.report.json
docs/perf/2026-08-15/lh-4g-run2.report.html
docs/perf/2026-08-15/lh-4g-run2.report.json
docs/perf/2026-08-15/lh-4g-run3.report.html
docs/perf/2026-08-15/lh-4g-run3.report.json
docs/perf/2026-08-15/lh-4g-run4.report.html
docs/perf/2026-08-15/lh-4g-run4.report.json
docs/perf/2026-08-15/lh-4g-run5.report.html
docs/perf/2026-08-15/lh-4g-run5.report.json
docs/perf/2026-08-15/lh-slow3g-run1.report.html
docs/perf/2026-08-15/lh-slow3g-run1.report.json
docs/perf/2026-08-15/lh-slow3g-run2.report.html
docs/perf/2026-08-15/lh-slow3g-run2.report.json
docs/perf/2026-08-15/lh-slow3g-run3.report.html
docs/perf/2026-08-15/lh-slow3g-run3.report.json
docs/perf/2026-08-15/lh-slow3g-run4.report.html
docs/perf/2026-08-15/lh-slow3g-run4.report.json
docs/perf/2026-08-15/lh-slow3g-run5.report.html
docs/perf/2026-08-15/lh-slow3g-run5.report.json
docs/perf/README.md
docs/perf/flow-iter1.json
docs/perf/flow-iter2.json
docs/perf/flow-iter3.json
docs/perf/flow.mjs
docs/perf/lh-4g-run1.report.html
docs/perf/lh-4g-run1.report.json
docs/perf/lh-4g-run2.report.html
docs/perf/lh-4g-run2.report.json
docs/perf/lh-4g-run3.report.html
docs/perf/lh-4g-run3.report.json
docs/perf/lh-4g-run4.report.html
docs/perf/lh-4g-run4.report.json
docs/perf/lh-4g-run5.report.html
docs/perf/lh-4g-run5.report.json
docs/perf/lh-slow3g-run1.report.html
docs/perf/lh-slow3g-run1.report.json
docs/perf/lh-slow3g-run2.report.html
docs/perf/lh-slow3g-run2.report.json
docs/perf/lh-slow3g-run3.report.html
docs/perf/lh-slow3g-run3.report.json
docs/perf/lh-slow3g-run4.report.html
docs/perf/lh-slow3g-run4.report.json
docs/perf/lh-slow3g-run5.report.html
docs/perf/lh-slow3g-run5.report.json
docs/print/Thesis_Ch1-3.docx
docs/print/Thesis_Ch1-3.pdf
```

`docs/print/` is untracked (Section 1.3). This report itself,
`docs/STATE_REPORT_2026-08-25.md`, is the only file created by this run.

### 8.2 Every ADR

| Number | Title | Status |
|---|---|---|
| 0001 | Bioprocess drying parameters in `extra_data`, not a new table | Accepted |
| 0002 | Derived fixed-cost overlay, and three temporary domain assumptions | Accepted |

Two ADRs. Numbers 0003 onward do not exist.

### 8.3 `docs/EVIDENCE.md`

It exists. Full contents, verbatim (fenced at four backticks because the file
contains its own triple-backtick blocks):

````markdown
# Evidence — the read-cache invalidation tests actually test the cache

This file records how the Phase 6b/6c cache-invalidation tests were verified to
be **load-bearing**, and how to repeat that verification. It exists because the
strongest claim this work makes — *these tests fail if the purge stops working* —
is not visible in the test output when everything passes, and was until now only
demonstrated in a transcript.

Everything below is a procedure to re-run, not a result to take on trust.

## Provenance

| | |
|---|---|
| **Subject** | `frontend/src/lib/cacheInvalidation.test.tsx` — five tests, one per farm-scoped write path |
| **Under test** | `purgeApiReadCache()` in `frontend/src/lib/apiCache.ts`, and the call sites that invoke it |
| **Runner** | Vitest **4.1.10**, `win32-x64`, `node v24.15.0` |
| **Working directory** | `frontend/` |
| **Commit at time of run** | Phase 6c working tree, on `feat/enterprise-economics` (parent `d82419d`) |
| **Date of run** | 2026-08-25 |

## Why a mutation test and not a spy

`expect(purgeApiReadCache).toHaveBeenCalled()` proves a function ran. It passes
just as happily when the purge deletes nothing, which is the exact bug class
these tests exist to close. So each test instead seeds a **real** cache entry
through a stand-in service worker, performs the write, and re-reads — asserting
on the **value** that comes back.

The verification below confirms that: with the purge neutered, every one of the
five fails on a value or on rendered text, and none fails on a call count.

## The edit

Replace the body of `purgeApiReadCache` in `frontend/src/lib/apiCache.ts` with a
no-op. The signature and the export are unchanged, so every call site still
resolves and still awaits — only the deletion stops happening:

```ts
export async function purgeApiReadCache(): Promise<void> {
  void API_READ_CACHE;
  return;
}
```

For reference, the real body it replaces:

```ts
export async function purgeApiReadCache(): Promise<void> {
  if (typeof caches === 'undefined') return; // no Cache Storage (e.g. dev/SSR)
  try {
    await caches.delete(API_READ_CACHE);
  } catch {
    // Best-effort: a failure here must never block login/logout.
  }
}
```

`void API_READ_CACHE;` is there only to keep the now-unused import from failing
lint during the experiment. **Revert the file afterwards** — the no-op must not
be committed.

## The command

```
cd frontend
npx vitest run src/lib/cacheInvalidation.test.tsx
```

## Expected result: 5 failed, 0 passed

```
 ❯ src/lib/cacheInvalidation.test.tsx (5 tests | 5 failed)
```

Each failure, with the value asserted and where the stale value comes from:

| # | Write path | Failure message | Asserted | Received (stale) | Why the stale value is that |
|---|---|---|---|---|---|
| 1 | Online log save (`saveOperationalLog` → `ledgerService.createLog`) | `AssertionError: expected +0 to be 3500 // Object.is equality` | `3500` | `0` | The DSS read cached before the ₦3,500 fertiliser log was written |
| 2 | Offline queue flush (`flushPendingLogs`) | `AssertionError: expected +0 to be 5500 // Object.is equality` | `5500` | `0` | The DSS read cached before either queued log (₦3,500 + ₦2,000) was flushed |
| 3 | Equipment create (`EquipmentPage`) | `AssertionError: expected ' Enterprise economicsEverything below…' to contain '2 of your 3 assets have no depreciati…'` | rendered text `2 of your 3 assets have no depreciation rate recorded` | the panel still renders `1 of your 2 assets has no depreciation rate recorded` | The break-even read cached before the third, unrated asset was added |
| 4 | Maintenance log (`MaintenancePanel`) | `AssertionError: expected +0 to be 12000 // Object.is equality` | `12000` | `0` | The cost-structure read cached before the ₦12,000 gearbox service |
| 5 | Reversal (`ledgerService.reverseLog`) | `AssertionError: expected 5500 to be 2000 // Object.is equality` | `2000` | `5500` | The DSS read cached before the ₦3,500 log was reversed; ₦2,000 survives it |

Note the shape of #5: unlike #1, #2 and #4 its stale value is **not** zero. The
two logs (₦3,500 and ₦2,000) are both written before the seeding read, so the
cached figure is ₦5,500 and the correct figure is ₦2,000. A cache that survived
the reversal reads ₦5,500; a ledger that lost the second log would read ₦0.
Only a purge plus a correctly-netted contra produces ₦2,000.

Note also the shape of #3: it fails on rendered text rather than on a number,
because the thing that goes stale for a user there is a sentence.

## What this does and does not establish

**Does:** that all five tests depend on `purgeApiReadCache` doing real work, and
that each one's assertion moves when the cache is stale.

**Does not:** anything about the background-revalidation half of
StaleWhileRevalidate. The harness models only the serve half (a cache hit wins).
The revalidation race is written up beside the `runtimeCaching` block in
`frontend/vite.config.ts` — it is reasoned from the handler's ordering, has not
been observed, and is not addressed by these tests.

## Where the purge lives (Phase 6c)

The invariant, for anyone re-running the above and wondering why a component no
longer purges: **mutating `ledgerService` methods purge; components do not.**
`createLog` and `reverseLog` each purge on 2xx and on the status codes that mean
the server's state already moved (409 for both; 404 additionally for
`reverseLog`).

Two declared exceptions, because they do not route through the ledger client and
call `purgeApiReadCache` directly:

| File | Line |
|---|---|
| `frontend/src/features/equipment/EquipmentPage.tsx` | `51` |
| `frontend/src/features/equipment/components/MaintenancePanel.tsx` | `53` |

(Import lines are `4` in both files. Verify with
`grep -n "purgeApiReadCache" frontend/src/features/equipment/EquipmentPage.tsx frontend/src/features/equipment/components/MaintenancePanel.tsx`.)

---

# Evidence — the partial-budget parity fixture actually fails when it should

`frontend/src/features/dss/partialBudget.ts` is a second implementation of
`backend/app/services/enterprise_service.partial_budget`. Both files asserted in
prose that they must agree and nothing executed both and compared; the two
suites shared seven cases and not one input tuple. A term added to one
implementation left both suites green.

`frontend/src/fixtures/partial_budget_parity.json` (cases **PB-1..PB-8**, all
values hand-computed and never regenerated from either implementation) is now
read verbatim by both `backend/tests/test_enterprise_service.py` and
`frontend/src/features/dss/partialBudget.test.ts`. Both implementations agreed
with all eight on the first run — no divergence was found.

Note that **A-H and PB-1..PB-8 are two disjoint sets**, not two names for one
set: A-G are the enterprise-economics fixtures in `test_enterprise_service.py`,
H is the rejection/isolation set in `test_api.py`, and PB-1..PB-8 are the parity
cases. (Register finding P1-04.)

## Why the failure runs exist

A parity test that skips, catches, or defaults when it cannot find its input is
indistinguishable from no parity test at all — the exact condition the fixture
exists to end. So the fixture read is uncaught in both suites, and that claim is
verified rather than asserted: three ways of breaking the fixture, each run
against both suites, six runs. **The fixture is restored and unmodified in the
commit** (md5 `68b2549054fb6f06325fcd15c18c6f3b` before and after).

## The commands

The backend suite needs **no `DATABASE_URL`, no Docker and no Postgres**. Every
database-touching fixture in `backend/tests/conftest.py` is function-scoped and
`Base.metadata.create_all` runs only inside `db`; these cases request none of
them. Run from the repository root:

```
python -m pytest backend/tests/test_enterprise_service.py -q
cd frontend && npx vitest run src/features/dss/partialBudget.test.ts
```

Green baseline: **40 passed** (backend, 29 pre-existing + 11 new) and
**15 passed** (frontend, 4 pre-existing + 11 new).

## The six runs

| # | Break | Suite | Failure |
|---|---|---|---|
| 1a | `mv …/partial_budget_parity.json …/partial_budget_parity.json.renamed` | backend | `FileNotFoundError: [Errno 2] No such file or directory: 'C:\Users\DELL\Desktop\Agri P\frontend\src\fixtures\partial_budget_parity.json'` — collection error, `Interrupted: 1 error during collection` |
| 1b | same | frontend | Vite fails to resolve the import at transform time: `Failed to resolve import "../../fixtures/partial_budget_parity.json"`, pointing at line 3 of `partialBudget.test.ts`. `Test Files 1 failed (1) / Tests no tests` |
| 2a | truncate to the first 400 bytes (invalid JSON) | backend | `json.decoder.JSONDecodeError: Unterminated string starting at: line 7 column 13 (char 277)` — collection error |
| 2b | same | frontend | `Error: EOF while parsing a string at line 7 column 135`. `Test Files 1 failed (1) / Tests no tests` |
| 3a | `"case_count": 8` → `9`, cases left at 8 | backend | `AssertionError: partial_budget_parity.json: case_count is 9 but cases has 8 entries` / `assert 9 == 8` in `test_parity_fixture_is_internally_consistent`. `1 failed, 39 passed` |
| 3b | same | frontend | `AssertionError: partial_budget_parity.json: case_count is 9 but cases has 8 entries: expected 9 to be 8 // Object.is equality`. `Tests 1 failed \| 14 passed (15)` |

Runs 1 and 2 fail at **import/collection** time in both suites, before any test
body executes — which is the point: there is no code path in which a missing or
malformed fixture yields a green run. Run 3 is the truncated-but-parseable case,
which import-time failure cannot catch, so it is caught by comparing the file's
own `case_count` against `len(cases)` and both against a constant declared in
each test file.

## What this does and does not establish

**Does:** that both implementations of the partial budget produce the same net
change for eight hand-computed tuples, including a negative result (PB-1, sign
asserted separately from magnitude), an exact zero that is not negative zero
(PB-3), kobo precision at `rel=1e-9` (PB-7), and a cross-pair transposition trap
(PB-8). And that the fixture cannot go missing, malformed, or silently shrink
without failing both suites.

**Does not:** anything about the endpoint layer, serialisation, or the offline
substitution logic that decides *which* implementation runs. It compares two
pure functions. It also cannot establish that both are wrong in the same way —
only that hand-computed expectations, which no implementation generated,
disagree with neither.

## Two findings recorded here, deliberately NOT changed by this ticket

1. **`conftest.py` imports the database module at collection time.**
   `backend/tests/conftest.py:8-9` imports `backend.app.main`, which reaches
   `backend/app/models/database.py:5`, `engine = create_engine(settings.database_url)`,
   evaluated at import for every test in the directory. It only parses the URL
   and imports the driver — it does not connect — so the default
   `postgresql://…@localhost/agriprofit` plus an installed psycopg2 is enough
   and pure numeric tests run with no database. But it does mean a pure test
   cannot be collected without a parseable URL and an importable driver. Out of
   scope here.
2. **The `run-backend-tests-locally` note is stale.** It says a SQLite
   `DATABASE_URL` must be set or psycopg2 fails to import. Both halves are wrong
   on this machine: psycopg2 2.9.12 is installed, and
   `env -u DATABASE_URL python -m pytest backend/tests/test_enterprise_service.py -q`
   passes, while `DATABASE_URL=sqlite` *breaks* the run with
   `sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from given URL
   string`. Correcting that note is not in this ticket.

---

# Evidence — the command behind every figure quoted for the branch

Run from the repository root unless stated. No `DATABASE_URL` is required (see
the finding above). Figures are as of 2026-08-25 on `feat/partial-budget-parity`.

## Test and coverage figures

| Figure | Command |
|---|---|
| Fixtures A–G: **11 passed, 29 deselected** | `python -m pytest backend/tests/test_enterprise_service.py -v -k "fixture_a or fixture_b or fixture_c or fixture_d or fixture_e or fixture_f or fixture_g"` |
| Fixture H (endpoint layer): **32 passed, 96 deselected** | `python -m pytest backend/tests/test_api.py -q -k "enterprise or mechanis"` |
| Full backend suite: **179 passed** | `python -m pytest backend/tests -q` |
| `enterprise_service.py` **72 stmts, 0 miss, 100%** | `python -m pytest backend/tests --cov=backend/app --cov-report=term` |
| Overall backend coverage **TOTAL 1285 stmts, 98 miss, 92%** | same command as above |
| Full frontend suite: **41 passed, 6 files** | `cd frontend && npx vitest run` |
| Parity block alone: **40 passed** backend / **15 passed** frontend | `python -m pytest backend/tests/test_enterprise_service.py -q` · `cd frontend && npx vitest run src/features/dss/partialBudget.test.ts` |
| Type check clean (exit 0) | `cd frontend && npx tsc -b` |
| Lint clean (exit 0) | `cd frontend && npx eslint .` |

## Scope figures

| Figure | Command |
|---|---|
| No Alembic migration on the branch | `git diff --stat main...HEAD -- backend/alembic/versions/ alembic/versions/` (empty) |
| Nothing under `backend/app/ml/` modified | `git diff --stat main...HEAD -- backend/app/ml/` (empty) |
| `backend/tests/` additions **2194 insertions, 4 deletions** | `git diff --stat main...HEAD -- backend/tests/` |
| The 4 deletions are an HS256 comment rewrite, not enterprise economics | `git log --oneline -S "Flip the final signature character" main...HEAD -- backend/tests/` → `8690289 fix(bioprocess): water_removed_kg is a water balance…` |
| **No dependency added by the enterprise-economics work** | `git diff --stat 502dced..94e554a -- backend/requirements.txt frontend/package.json frontend/package-lock.json` (empty) |
| Dependency changes on the branch as a whole: `pytest-cov`, `@vitest/coverage-v8` | `git diff main...HEAD -- backend/requirements.txt frontend/package.json` · attributed by `git log --oneline main...HEAD -- backend/requirements.txt frontend/package.json` → `ec00162`, `0046b43` |
| Parity commit adds no dependency, migration or `ml/` change | `git show --stat 330f1d9 -- backend/requirements.txt frontend/package.json backend/app/ml/ backend/alembic/` (empty) |

### On the baseline for "no new dependency"

The enterprise-economics DoD item **"No new Python or JavaScript dependency"**
is read against that ticket's own commit range, `502dced..94e554a` (eleven
commits), where it is clean — not against `main`, where the branch does add
`pytest-cov` and `@vitest/coverage-v8`.

That is not a loosening. The two packages **predate** the range: `pytest-cov`
arrives in `0046b43` (bioprocess phase 3) and `@vitest/coverage-v8` in `ec00162`
(frontend coverage), each closed under its own ticket. And they are load-bearing
for two other items in the same DoD — without `pytest-cov` the coverage figures
cannot be produced at all:

```
$ python -m pytest backend/tests/test_enterprise_service.py -p no:cov --cov=backend/app
ERROR: python -m pytest: error: unrecognized arguments: --cov=backend/app
```

`main` carries neither package (`requirements.txt` ends `pytest / httpx`;
`package.json` has no `test:coverage` script), so coverage is not measurable on
`main` at all. Read against `main`, the DoD's items "enterprise_service.py at
100% coverage", "overall backend coverage not below the current 91%" and "no new
dependency" cannot all hold at once. The DoD settles its own intent by saying
**"the current 91%"** — a figure that could only have been measured with
`pytest-cov` already installed. The tooling is assumed present, not forbidden.

## Seed idempotency — the maize figures are bit-identical

The maize figures **₦35.00/kg harvested** and **₦41.67/kg marketable** are quoted
in a defended chapter, so the multi-crop seed must not move them. With the stack
up (`docker compose up -d`, containers `agrip-backend-1` and `agrip-db-1`),
captured before and after a re-run of the seed:

```
python backend/scripts/seed_bioprocess_demo.py
```

Read back with `GET /api/v1/dss/decision-support` as
`demo-bioprocess-v2@test.example`, selecting the maize crop object:

```json
{ "crop": "maize", "expenses": 3500.0, "revenue": 45000.0,
  "gross_margin": 41500.0, "yield_quantity": 100.0,
  "marketable_mass_kg": 84.0,
  "unit_cost_of_production": 35.0,
  "unit_cost_per_kg_marketable": 41.666666666666664,
  "break_even_yield": 7.777777777777778 }
```

Byte-identical before and after (md5 `1850df22069facec23e86032275c659f` on both
captures; `diff` reports no differences). The seed reported
`28 operational logs, 28 financial transactions, 2 equipment` with every log
returning **HTTP 200** rather than 201 — the ledger's `client_id` idempotency
returning existing rows instead of duplicating them.

## Where the marketable unit cost is visible

`frontend/src/features/dashboard/components/DecisionSupport.tsx:85` renders
`Unit cost {nairaExact(marketableCost)}/kg marketable` beside the harvest-unit
figure, guarded at line 82 so a crop with no drying run (and therefore no
marketable mass) falls back rather than rendering a null. The two break-even
prices carry the same `/kg marketable` suffix at
`frontend/src/features/dss/components/BreakEvenPricePanel.tsx:29`.

````

### 8.4 Terms defined in `CONTEXT.md`, by heading

Names only, in file order.

**`### Operations`** (line 7): Operational Log · Physical Input · Activity
Category · Yield · Mechanization · Bioprocess · Drying Run · Moisture Content ·
Marketable Mass · Process Loss — **10 terms**

**`### Finance`** (line 49): Financial Transaction · Reversal · Gross Margin ·
Tax Category · Depreciation — **5 terms**

**`### Equipment`** (line 71): Equipment · Maintenance Log — **2 terms**

**`### Cost structure`** (line 81): Cost Subtype · Cost Behaviour ·
Classification Coverage · Break-even Price to Cover Cash Cost · Break-even Price
to Cover Total Cost · Allocated Fixed Cost · Operating Expense Ratio ·
Reporting Period · Season · Partial Budget · Olympic Average Yield —
**11 terms**

**`### Intelligence`** (line 127): Predictive DSS — **1 term**

29 terms across five headings, all under the top-level `## Language` (line 5).
The enterprise-economics ticket's definition of done asked for "the eight new
terms"; the `Cost structure` heading carries eleven.

### 8.5 `docs/perf/` — Lighthouse reports

Present. One subdirectory, plus a current set at the top level.

| Directory | Files | Contents |
|---|---|---|
| `docs/perf/` (top level) | **26** | `README.md`, `flow.mjs`, `offline-probe.mjs`, `flow-iter1..3.json`, and 20 Lighthouse reports — `lh-4g-run1..5` and `lh-slow3g-run1..5`, each as `.report.html` + `.report.json` |
| `docs/perf/2026-08-15/` | **23** | `flow-iter1..3.json` plus the same 20 Lighthouse report files |

`docs/perf/2026-08-15/` is the superseded set (commit `13f95a6`, "re-measure
against the c16924e build, supersede the 15 Aug set"); the top-level files are
the current measurement, dated 17 August by commit `d63d0ca`. The top-level set
therefore predates every commit from `c16924e` onward — including all of the
enterprise-economics work and the code-splitting in `59554cc`.

### 8.6 Usability session artifacts

**No completed usability session artifacts exist anywhere in the repository.**

What does exist is the *instrument*, blank:

- `usabilitysessionrunsheet.md` at the repository root — a facilitator script
  for a dry run and evaluator sessions, referencing "the Usability Evaluation
  Pack (Section 3.8.4)". It contains instructions, not results.
- `AgriProfit_Evaluation_Pack.docx` at the root — noted by filename only, not
  opened (chapter/DOCX files are excluded as evidence by the rules of this
  report). Whether it contains blank forms or completed ones is therefore
  **CANNOT DETERMINE FROM REPOSITORY** by this method.

Searched for and **not found**: completed SUS forms or SUS score tabulations,
filled heuristic-evaluation checklists, session notes or transcripts,
participant records, scans or photographs. A repository-wide search for image
and document files outside `node_modules`, `frontend/dist` and `frontend/public`
returns only:

```
./backend/app/ml/data/crop_yield.csv
./docs/print/Thesis_Ch1-3.pdf
./frontend/src/assets/hero.png
./Updated B.Tech Final Project Guideline for 2025_2026_v1.pdf
```

None of these is a usability artifact. There is no `docs/usability/`, no
`evaluation/` directory, and no per-participant file of any kind.

`LIMITATIONS.md` §8 is consistent with this (see 8.7): it describes the
evaluation as not yet carried out.

### 8.7 `LIMITATIONS.md` — section headings and first sentences

| Heading | First sentence |
|---|---|
| `## 1. Scope and Deployment` | **Local-only deployment.** The application runs as a Docker Compose stack |
| `## 2. Identity, Authentication, and Access Control` | **No token revocation within its lifetime.** Access is granted by a stateless |
| `## 3. Data Integrity and the Ledger Model` | **Single-entry, not double-entry.** The ledger records each transaction once, |
| `## 4. Decision Support System` | **The forecast tier is trained on synthetic data.** The Tier-2 RandomForest |
| `## 5. Offline and Connectivity Behaviour` | **Offline writes cover the quick-capture path only.** The offline-first queue |
| `## 6. Alternative Channels` | **USSD, SMS, and WhatsApp entry are simulated.** The PRD envisions low-end |
| `## 7. Performance and Scale` | None of the following was optimised; the figures are descriptive, measured |
| `## 8. Verification and Assurance` | Automated backend coverage is **88%** across 42 tests, concentrated on the |
| `## Future Work` | The limitations above map onto a concrete, prioritised programme of work. The |

(First sentences are reproduced as the first line of each section's opening
paragraph, which is where each sentence begins; line wrapping in the source file
means some run on beyond the text shown.)

**Reported, not fixed:** §8 states "**88%** across **42 tests**". Section 2 of
this report measures **92%** across **179 tests**. That heading is stale by a
wide margin.

### 8.8 Trained ML model artifact and metrics file

**Present on disk, and NOT committed.**

| | |
|---|---|
| Model artifact | `backend/app/ml/models/latest_model.joblib` |
| Size | 60,375,114 bytes (~57.6 MiB) |
| Modification date | **2026-07-02 04:03** |
| Metrics/metadata file | `backend/app/ml/models/model_meta.json` |
| Size | 916 bytes |
| Modification date | **2026-07-02 04:03** |
| Tracked by git? | **No** — `git ls-files` matches neither path |

Both files also exist inside the running backend container at
`/code/app/ml/models/`. Paths are defined at
`backend/app/ml/train.py:29-31` and mirrored at `backend/app/ml/predict.py:19-20`.

`model_meta.json`, full contents:

```json
{
  "features": [
    "rainfall",
    "fertilizer_used",
    "soil_ph",
    "crop"
  ],
  "numeric_features": [
    "rainfall",
    "fertilizer_used",
    "soil_ph"
  ],
  "categorical_features": [
    "crop"
  ],
  "crops": [
    "maize",
    "rice",
    "sorghum",
    "soybean",
    "cassava"
  ],
  "target": "yield_t_ha",
  "target_unit": "t/ha",
  "bounds": {
    "rainfall": [
      300.0,
      2000.0
    ],
    "fertilizer_used": [
      0.0,
      120.0
    ],
    "soil_ph": [
      4.5,
      8.5
    ]
  },
  "model": "Pipeline(OneHotEncoder + RandomForestRegressor)",
  "n_estimators": 200,
  "n_samples": 6000,
  "metrics": {
    "r2": 0.9762,
    "mae": 0.2414
  },
  "feature_importances": {
    "crop": 0.3445,
    "rainfall": 0.2845,
    "fertilizer_used": 0.1231,
    "soil_ph": 0.2479
  },
  "trained_at": "2026-07-01T19:03:34.593275+00:00"
}
```

It records **R² and MAE**. It records **no RMSE** — there is no RMSE figure
anywhere in the metrics file or the `/dss/model` response.

Note the dates: the model was trained 2026-07-01/02, seven weeks before this
report, and has not been retrained since. It is not in version control, so it
cannot be reproduced from the repository alone — only regenerated by running
`backend/app/ml/train.py`, which would produce different figures (the training
data is synthesised).

---

## 9. Documentation-versus-code discrepancies

Only the claims listed in the prompt were checked.

### 9.1 "87 tests, all passing"

**CONTRADICTED.** The backend suite collects and passes **179** tests
(Section 2.1–2.2), not 87. The "all passing" half is correct: 179 passed,
0 failed, 0 skipped, 0 errored. Adding the 41 frontend tests gives 220 in total.

### 9.2 "90% overall backend statement coverage, 1,040 statements, 102 missed"

**CONTRADICTED** on all three figures. Measured today (Section 2.3–2.4):
**92%**, **1,285** statements, **98** missed. The measurement is statement
coverage, so the basis matches; the numbers do not.

### 9.3 "8 modules at 100% coverage" and the named list

**CONTRADICTED** on the count; **CANNOT DETERMINE** on the list.

The count: **17** modules with executable statements are at 100%, plus 8 empty
`__init__.py` files that coverage.py also reports as 100% — 25 rows in total
(Section 2.5). Neither figure is 8 in the sense a reader would take it. (The
coincidence that exactly 8 *empty* modules read 100% is worth noting, because it
is the only way "8" arises from today's table, and those eight contain no code.)

The named list cannot be checked: the prompt refers to it without supplying it,
and no file in the repository states a list of eight 100%-covered modules. To
verify it I would need the list itself, or the document that carries it.

### 9.4 "`bioprocess_service.py` at 100% coverage"

**VERIFIED.** `backend\app\services\bioprocess_service.py  68  0  100%`
(Section 2.3).

### 9.5 "The repository contains one seed script, which creates a single-crop maize demonstration"

**Half VERIFIED, half CONTRADICTED.**

- *One seed script* — **VERIFIED.** `backend/scripts/seed_bioprocess_demo.py` is
  the only one (Section 5.1).
- *Single-crop maize demonstration* — **CONTRADICTED.** That script creates
  **five** crops — maize, cassava, tomato, cowpea and sorghum — plus two
  equipment rows, across 28 logs and 28 paired transactions (Section 5.2). The
  maize lot is one of five, and cowpea, not maize, is the crop the
  enterprise-economics figures are legible on (per the script's own docstring,
  lines 24–31). The description matches a state that commits `b1987f5` and
  `6f926a5` moved past.

### 9.6 "Break-even yield of 7.8 kg for the seeded maize record"

**VERIFIED, as a rounded figure.** The live API returns
`"break_even_yield":7.777777777777778,"break_even_unit":"kg"` (Section 6.1),
which is 7.8 kg to one decimal place — and one decimal is exactly what the
interface renders (`maximumFractionDigits: 1` at
`frontend/src/features/dashboard/components/DecisionSupport.tsx:103`). Anyone
quoting 7.8 kg should say it is rounded from 7.7̄.

### 9.7 "Unit cost ₦35.00/kg wet and ₦41.67/kg marketable"

**VERIFIED**, with the same rounding caveat on the second figure (Section 6.8).
`unit_cost_of_production` is `35.0` exactly. `unit_cost_per_kg_marketable` is
`41.666666666666664`, which is ₦41.67 to two decimals — the precision the
interface displays. The residual difference is 0.0033 naira and is a rounding
artefact, not a discrepancy.

### 9.8 "R² 0.9762, MAE 0.2414 t/ha, 6,000 synthetic training samples"

**VERIFIED.** All three appear identically in the on-disk metrics file
(`backend/app/ml/models/model_meta.json`, Section 8.8) and in the live
`GET /dss/model` response (Section 6.3): `"metrics":{"r2":0.9762,"mae":0.2414}`,
`"n_samples":6000`, `"target_unit":"t/ha"`. That the data is synthetic is
established by `backend/app/ml/dataset.py` being the generator and by
`LIMITATIONS.md` §4. Caveat for the write-up: the artifact is dated 2026-07-02,
is untracked by git, and would produce different figures if retrained.

### 9.9 "Bundle is 243,724 bytes"

**CONTRADICTED.** Today's entry bundle,
`frontend/dist/assets/index-B-brS2RV.js`, is **406,941 bytes** ungzipped and
**130,365 bytes** gzipped; the whole `dist/` directory is 892,710 bytes
(Section 7.5). 243,724 matches none of these. Nothing in the current build
output is that size, and the filename hash in any earlier record will not match
the current one either.

### 9.10 "The bioprocess option was removed from the entry form"

**CONTRADICTED.** `bioprocess` is present and selectable, labelled
"Post-harvest drying", at
`frontend/src/features/farm-records/FarmRecordCreateForm.tsx:24` within the
`CATEGORIES` array rendered into the Activity `<select>` at lines 150–152
(Section 4.6). The comment block immediately above the array (lines 15–17)
records that the option and its fields ship together.

### 9.11 "No automated test covers the model-info endpoint"

**CONTRADICTED.** Three tests in `backend/tests/test_api.py` cover
`GET /api/v1/dss/model`, added in commit `dd8ebac`:

```
test_dss_model_requires_authentication          (test_api.py:1472 — asserts 401 when anonymous)
test_dss_model_reports_metrics_when_trained     (test_api.py:1482)
test_dss_model_reports_untrained_without_zero_metrics  (test_api.py:1508)
```

The endpoint module `backend/app/api/endpoints/dss.py` sits at 93% coverage with
only lines 45–47 missed (which are in `trigger_training`, not `model_info`).

### 9.12 "No automated test covers the offline write queue flush"

**CONTRADICTED.** `frontend/src/lib/sync.test.ts` contains eight tests, five of
them directly on the flush path (Section 2.7):

```
flushPendingLogs > posts a queued log and clears it from the queue
flushPendingLogs > keeps the rest of the queue moving when one log fails
flushPendingLogs > runs one pass at a time when connectivity fires several flushes at once
flushPendingLogs > gives up after exactly three failed attempts
registerSyncListener > flushes the queue when the browser reports the connection back
registerSyncListener > does not flush on load when the browser is already offline
retryFailedLogs > requeues a failed log and flushes it once the server is back
retryFailedLogs > restarts the three-strike count instead of failing again immediately
```

Added in commits `d2f45af` and `ec00162`. A sixth test in
`src/lib/cacheInvalidation.test.tsx` also exercises the flush ("an offline queue
flush invalidates the cached derived reads").

### 9.13 "The offline write queue is not identity-scoped and is not cleared on logout"

**Still true — VERIFIED, both halves.**

*Not identity-scoped.* The Dexie schema carries no farm or user column:

```ts
frontend/src/lib/db.ts:4-21
export interface PendingLog {
  id?: number;
  clientId: string;
  payload: OperationalLogCreate;
  status: 'pending' | 'failed';
  failCount: number;
  createdAt: number;
}

class AgriProfitDB extends Dexie {
  pendingLogs!: Table<PendingLog>;

  constructor() {
    super('agriprofit');
    this.version(1).stores({
      pendingLogs: '++id, clientId, status, createdAt',
    });
  }
}
```

Nothing ties a queued log to the account that created it. `flushPendingLogs`
(`frontend/src/lib/sync.ts:15`) reads every row with `status === 'pending'` and
posts it under whatever token is current — so a log queued by one account is
flushed into whichever farm is logged in when connectivity returns.

*Not cleared on logout.* The logout path clears only the token and the read
cache:

```ts
frontend/src/features/auth/AuthProvider.tsx:23-28
  const logout = useCallback(() => {
    // Clear this farm's cached reads so they can't be served to the next account.
    void purgeApiReadCache();
    clearToken();
    setTokenState(null);
  }, []);
```

`purgeApiReadCache` deletes the Cache Storage entry only
(`caches.delete(API_READ_CACHE)`); it does not touch IndexedDB. Every reference
to `db.pendingLogs` in non-test source is in `SyncStatus.tsx:17`,
`usePendingSync.ts:11`, `db.ts`, `logs.ts:30` and `sync.ts:15/21/24/39/41` — a
count, a count, the schema, an add, and the flush/retry paths. **No call site
anywhere clears the queue on logout or login.** The two `AuthProvider` tests
that do exist assert the *read cache* is purged, not the write queue.

### 9.14 "client_id uniqueness is global while idempotency is farm-scoped, producing a 500 on cross-farm collision"

**Still true — VERIFIED by code inspection.** Established at three points.

The constraint is global — no farm in the uniqueness:

```python
backend/app/models/models.py:83
    client_id = Column(String, unique=True, nullable=True, index=True)
```

The idempotency lookup is farm-scoped:

```python
backend/app/services/ledger_service.py:9-15
def _find_by_client_id(db: Session, farm_id: int, client_id: str):
    # Scoped by farm: a client_id is only an idempotency match within the same
    # tenant, so one farm's offline key can never surface another farm's row.
    return db.query(models.OperationalLog).filter(
        models.OperationalLog.farm_id == farm_id,
        models.OperationalLog.client_id == client_id,
    ).first()
```

And the `IntegrityError` handler re-raises when the farm-scoped lookup finds
nothing — which is exactly the cross-farm case:

```python
backend/app/services/ledger_service.py:55-68
    try:
        db.commit()
    except IntegrityError:
        # A concurrent request with the same client_id won the race and the
        # unique index rejected this insert. Treat it as the same idempotent
        # outcome and return the row the winner created (200, not 500).
        db.rollback()
        if log.client_id:
            existing = _find_by_client_id(db, farm_id, log.client_id)
            if existing:
                return existing, False
        raise
    db.refresh(db_log)
    return db_log, True
```

Farm B posting a `client_id` that farm A already used: the insert violates the
global unique index → `IntegrityError` → rollback → `_find_by_client_id(db,
farm_B, client_id)` returns `None` (the row belongs to farm A) → bare `raise`.
Nothing between there and the ASGI boundary catches `IntegrityError` — there is
no such handler in `backend/app/api/endpoints/ledger.py`, `core/exceptions.py`
or `main.py` — so it lands on the catch-all:

```python
backend/app/main.py:67-71
@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    """Last-resort handler: log the traceback, return a generic 500 (no leak)."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
```

→ **HTTP 500**. The same-farm race is handled correctly (200); only the
cross-farm collision falls through. This was established by reading the code
rather than by provoking it live, because provoking it would have written a row
to the database, which this report is forbidden to do. No automated test covers
the cross-farm collision path — `ledger_service.py` lines 57–66 (the entire
`except IntegrityError` block) are among the 8 statements it misses in
Section 2.3.

---

## 10. Three closing lists

### 10.1 IMPLEMENTED AND VERIFIED

Exists in code **and** covered by a passing automated test.

| Functionality | Evidence | Covering test(s) |
|---|---|---|
| Cost structure by behaviour, with classification coverage | §3.1, §3.2, §6.6 | `test_fixture_a_classification_and_coverage`; `test_enterprise_cost_structure_matches_fixture_a`; `test_zero_total_cost_has_undefined_coverage` |
| Unclassified cost never defaults into a bucket | §3.2, §3.3 | `test_unclassified_categories_never_default_into_a_bucket`; `test_enterprise_cost_structure_reads_subtype_only_for_mechanization` |
| Conditional MECHANIZATION schema validation, absence accepted | §3.3 | `test_mechanization_without_extra_data_accepted_and_unclassified`; `test_mechanization_unrecognised_cost_subtype_rejected`; `test_mechanization_hours_used_out_of_range_rejected` |
| Depreciation overlay, straight-line, with unrated count | §3.5, §6.6 | `test_fixture_b_depreciation_overlay`; `test_zero_rate_equipment_counts_as_unrated_not_as_a_zero_charge`; `test_equipment_with_no_purchase_value_is_unrated` |
| Proportional fixed-cost allocation, undefined at zero base | §3.1, §6.6 | `test_fixture_b_proportional_allocation`; `test_allocation_with_no_base_is_undefined_not_an_even_split` |
| Dual break-even price, cash strictly below total | §3.6, §6.6 | `test_fixture_c_dual_break_even_price`; `test_cash_price_is_strictly_lower_even_with_full_coverage_and_no_overlay`; `test_enterprise_break_even_prices_with_marketable_mass_never_collapse` |
| Break-even price undefined without marketable mass | §3.6, §6.6 | `test_break_even_price_is_undefined_without_marketable_mass[0.0]` / `[None]`; `test_enterprise_break_even_prices_null_without_marketable_mass` |
| Yield sensitivity matrix, labelled conditional | §3.1, §6.6 | `test_fixture_d_yield_sensitivity_matrix`; `test_enterprise_sensitivity_matrix_is_labelled_conditional`; `test_sensitivity_over_zero_baseline_yields_undefined_prices` |
| Operating expense ratio, excluding the overlay | §3.1, §6.6 | `test_fixture_e_operating_expense_ratio`; `test_operating_expense_ratio_excludes_the_depreciation_overlay`; `test_enterprise_operating_expense_ratio_excludes_recorded_depreciation` |
| Partial budget, signed and unclamped | §3.1, §6.6 | `test_fixture_f_partial_budget_solar_dryer_is_worth_it`; `test_fixture_f_negative_partial_budget_is_returned_signed`; `test_enterprise_partial_budget_returns_a_negative_net_change` |
| Backend/frontend partial-budget parity over PB-1..PB-8 | §3.8, §2.7 | `test_parity_partial_budget_matches_hand_computed_expectation[PB-1..PB-8]`; frontend `partialBudgetLocal parity with enterprise_service.partial_budget > 'PB-1'..'PB-8'`; `test_parity_fixture_is_internally_consistent` |
| Olympic average yield, single-instance tie rule | §3.1, §6.6 | `test_fixture_g_olympic_average_discards_one_instance_not_all_ties`; `test_fixture_g_two_seasons_is_undefined_never_a_two_value_mean`; `test_three_identical_seasons_survive_the_single_instance_rule` |
| Yield baseline endpoint, season count in every branch | §3.4, §6.6 | `test_enterprise_yield_baseline_needs_three_seasons`; `test_enterprise_yield_baseline_season_count_distinguishes_two_kinds_of_null`; `test_enterprise_yield_baseline_mixed_units_is_null_with_a_reason` |
| Depreciation window pinning and reproducibility | §3.4, §6.6 | `test_enterprise_period_defaults_to_the_derived_ledger_span`; `test_enterprise_pinned_period_is_reproducible_when_a_new_log_widens_the_span`; `test_enterprise_period_days_is_bounded_at_the_edge[…]` (6 cases) |
| Farm scoping on all four enterprise read routes | §3.4 | `test_enterprise_routes_cross_farm_read_is_404[…]` (4 cases) |
| Drying metrics — water balance, process loss, Newton, Page | §4.1, §6.5 | `test_fixture_a_maize_with_process_loss`; `test_fixture_f_water_removed_is_a_water_balance_not_a_mass_difference`; `test_fixture_c_page_fit_exact_recovery`; `test_page_fit_insufficient_readings_returns_none` |
| Safe-storage verdict, unknown crop is None not False | §4.1, §6.5 | `test_safe_storage_known_crops`; `test_safe_storage_unknown_crop_is_none_never_false` |
| Bioprocess payload validation at the schema edge | §4.4 | `test_bioprocess_missing_payload_rejected`; `test_bioprocess_mass_out_exceeds_mass_in_rejected`; `test_bioprocess_readings_not_strictly_increasing_rejected` (+5 more) |
| Bioprocess detail and summary reads, reversal-aware | §4.3, §6.4, §6.5 | `test_bioprocess_detail_returns_params_and_metrics`; `test_bioprocess_summary_aggregates_per_crop`; `test_bioprocess_summary_excludes_reversed_run`; `test_bioprocess_detail_on_reversal_contra_is_404` |
| Retrospective break-even yield, with its null cases | §3.6, §6.1 | `test_dss_break_even_yield_normal_case`; `test_dss_break_even_null_on_mixed_units`; `test_dss_break_even_null_on_zero_revenue`; `test_dss_break_even_reflects_reversal` |
| Model-info endpoint, trained and untrained states | §6.3 | `test_dss_model_requires_authentication`; `test_dss_model_reports_metrics_when_trained`; `test_dss_model_reports_untrained_without_zero_metrics` |
| Equipment depreciation rate — nullable, percent unit, converted once | §5.6 | `test_equipment_accepts_a_null_depreciation_rate`; `test_depreciation_rate_is_converted_to_a_fraction_exactly_once` |
| Offline write queue — flush, three-strike, retry, single-pass | §2.7 | `flushPendingLogs > posts a queued log and clears it from the queue`; `> gives up after exactly three failed attempts`; `> runs one pass at a time when connectivity fires several flushes at once`; `retryFailedLogs > restarts the three-strike count instead of failing again immediately` |
| Drying payload construction and its rejections (client-side) | §4.5 | `buildDryingParams > builds the DRYING payload from a physically consistent run` + 9 rejection cases |
| Read-cache purge on every farm-scoped write | §8.3 | `a log write invalidates the cached derived reads`; `an offline queue flush invalidates…`; `creating equipment invalidates…`; `logging maintenance invalidates…`; `a reversal invalidates…`; `purgeApiReadCache > deletes exactly the shared offline-read cache` |
| Read-cache purge on login and logout | §9.13 | `AuthProvider purges the offline-read cache on auth changes > purges on login` / `> purges on logout` |

### 10.2 IMPLEMENTED BUT NOT VERIFIED

Exists in code, with no automated test covering it. Evidence that does exist is
stated for each.

| Functionality | Where | Evidence that exists |
|---|---|---|
| Every enterprise-economics **frontend panel** — `CostStructurePanel`, `BreakEvenPricePanel`, `SensitivityTable`, `PartialBudgetForm`, `EnterpriseEconomics` | §3.9, §7.3 | Code inspection only. No component test renders any of them. The one indirect touch is `cacheInvalidation.test.tsx`, which asserts on text rendered by the break-even panel while testing the cache, not the panel. The pure helper `partialBudget.ts` behind the form **is** tested; the form itself is not. |
| **Marketable unit-cost line, break-even yield line and gross-margin rows** in `DecisionSupport.tsx` | §7.3 | Code inspection plus the live API response (§6.1) that feeds them. No test mounts `DecisionSupport`. |
| **Model-quality tiles and their three display states** on `DSSPredictPage` | §7.3 | Code inspection (`DSSPredictPage.tsx:185-213`) plus the live `/dss/model` response (§6.3). The endpoint is tested; the three rendered states are not. |
| **Reversal control and confirmation dialogue** | §7.3 | Code inspection (`FarmRecordsPage.tsx:184-191`, `:205-210`; `ReverseConfirmDialog.tsx`). The reversal *API* is covered (`test_dss_break_even_reflects_reversal`, `test_bioprocess_summary_excludes_reversed_run`) and the client-side cache purge on reversal is covered; the dialogue is not. |
| **Offline pending-sync indicator** (`SyncStatus.tsx`) | §7.3 | Code inspection. The queue logic beneath it is tested; the indicator component is not rendered by any test. |
| **Drying run result panel** (`DryingRunResult.tsx`) | §7.3 | Code inspection plus the live `/bioprocess/1049` response (§6.5) supplying every field it renders. Not mounted by any test. |
| **Dashboard metric cards, P&L chart, cost-breakdown donut** | §7.3 | Code inspection. `reports_service.py` sits at 94% with lines 90–91, 109, 112 missed. |
| **Equipment page and maintenance panel UI** | §7.2 | Code inspection; `equipment_service.py` is at 100% but no frontend test renders the page. |
| **Investor share links and the public report view** | §7.2 | Code inspection; `share_service.py` at 100% backend-side, no frontend test. |
| **`/dss/yield-baseline` has no user-reachable surface at all** | §3.9, §7.3 | The endpoint is implemented and well tested (§10.1), but no component fetches it — grep finds no frontend reference. It cannot be screenshotted. |
| **The cross-farm `client_id` collision path** | §9.14 | Code inspection only, and it is a *defect* rather than a feature: `ledger_service.py:57-66` is uncovered (8 missed statements), and reaching it returns HTTP 500. Not probed live, because probing it would write to the database. |
| **Maize unit-cost figures ₦35.00 / ₦41.67 and break-even 7.8 kg as end-to-end outputs** | §6.1, §6.8 | Live endpoint response, captured today. The arithmetic behind them is unit-tested; these specific seeded figures are asserted by no test — they are reproduced from the running system and from `docs/EVIDENCE.md`'s recorded md5 comparison. |
| **`backend/app/ml/train.py` and `dataset.py`** | §2.6 | 42% and 36% covered. The trained artifact exists (§8.8) and `/dss/model` serves its metadata, but the training and generation paths are largely unexercised. |
| **`backend/app/models/database.py`** | §2.6 | 64% covered; lines 11–15 (engine/session construction) are exercised only implicitly. |

### 10.3 SPECIFIED BUT NOT IMPLEMENTED

| Item | Where it is specified | What is missing |
|---|---|---|
| `MechanizationParams.equipment_id` | Schema field, `backend/app/schemas/schemas.py:106`; populated by the seed on five logs (§5.2) | **Nothing reads it.** A repository-wide search for `equipment_id` outside `schemas.py` finds only the unrelated `Equipment`/`MaintenanceLog` foreign key. No cost figure, no report and no overlay is attributed to a named asset. The data is validated, stored and never used. |
| `MechanizationParams.hours_used` | Schema field, `backend/app/schemas/schemas.py:107`; populated by the seed on three logs (§5.2) | Same: validated (`0 < h ≤ 1000`, and `test_mechanization_hours_used_out_of_range_rejected` proves the bound) and stored, but consumed by no service. There is no cost-per-hour, utilisation or machine-rate figure anywhere. |
| A frontend surface for the yield baseline | `CONTEXT.md` defines **Olympic Average Yield** and **Season**; ADR-0002 §3; route registered at `dss.py:160` (§3.4) | No component fetches `/dss/yield-baseline`. The Olympic average is computed, tested and served, and no user can see it. |
| Cowpea and tomato as selectable crops | Both are seeded crops with full ledgers and both appear in `/dss/decision-support` (§6.1) | `frontend/src/features/farm-records/FarmRecordCreateForm.tsx:31` hard-codes `CROPS = ['maize','rice','sorghum','soybean','cassava']`. Neither cowpea nor tomato can be entered through the interface. |
| Drying-curve chart, and intermediate readings capture | `DryingParams.readings` is a schema field; `page_fit` (`bioprocess_service.py:159`) exists solely to consume it; `docs/ch4-data/screenshot-runsheet.md` exists as a screenshot plan | No chart component (§4.7), and `DryingFields.tsx` collects no readings (§4.5). The Page model can only ever be fitted on seed-script data, never on a run a user entered. |
| Citation for the cost-behaviour taxonomy | `TODO(cite)` at `backend/app/schemas/schemas.py:110-113` — "an examiner will ask" | Unresolved. No citation anywhere in the repository. |
| Citation for the safe-storage moisture ceilings | `TODO(cite)` at `backend/app/services/bioprocess_service.py:25-26` — FAO / NSPRI / IITA | Unresolved. The nine thresholds carry no source. |
| Equipment update path | `LIMITATIONS.md` §3; noted in the seed script's `ensure_equipment` docstring (lines 434–437) | No PUT/PATCH on the equipment router; a mis-entered asset cannot be corrected through the API. |
| USSD, SMS and WhatsApp entry | `LIMITATIONS.md` §6, which says "the current build presents these as interface simulations" | **Contradicted in both directions.** `PRD.md` contains no mention of USSD, SMS or WhatsApp, so the claim that "the PRD envisions" them is unsupported by the PRD as it stands; and the simulations no longer exist either — `frontend/src/app/navigation.tsx:15-16` records that the ACCESS section was removed (commit `b6e2ddb`). Neither the integration nor the simulation is present. |
| Usability evaluation results | `usabilitysessionrunsheet.md` (a full facilitator script); `LIMITATIONS.md` §8 | No completed SUS forms, no heuristic checklists, no session notes, no participant records, no scans (§8.6). Only the blank instrument exists. |
| RMSE as a model metric | Named in the claim under check at §9.8 | `model_meta.json` records `r2` and `mae` only; no RMSE is computed, stored or served (§8.8). |
| Recorded-`DEPRECIATION` subtype vs derived overlay kept apart in the interface | ADR-0002 §1 ("The two are never added together") | Backend honours it (`fixed_cost_recorded` vs `allocated_fixed_ngn`, both live in §6.6) and `CostStructurePanel.tsx:67-76` renders both lines — so this is **implemented**; listed here only to record that the "Recorded fixed cost" line is conditionally rendered (`line 72`, only when non-zero), which means the distinction is invisible on any crop without a recorded charge. |

---

## CANNOT DETERMINE FROM REPOSITORY

| Question | Why | What would be needed |
|---|---|---|
| **1.8** — which commit corresponds to the state defended on 19 August 2026 | There are no git tags, and no commit message, file or document identifies a defence, viva or presentation. Twelve commits carry that author date; nothing distinguishes one as *the* defended state. | A tag on the commit, a release note, or the user's own record of which build was demonstrated. |
| **9.3** — the *named list* of "8 modules at 100% coverage" | The prompt refers to the list without supplying it, and no file in the repository states such a list. The count itself is answerable and is contradicted (17 modules with code, or 25 rows including empty `__init__` files). | The list itself, or the document that carries it. |
| **8.6** (partial) — whether `AgriProfit_Evaluation_Pack.docx` contains blank instruments or completed session data | The rules of this report forbid reading `.docx` chapter and pack files as evidence, so its contents were not inspected. Nothing outside it in the repository carries session results. | Permission to open the DOCX, or the session artifacts exported to the repository as files. |
| **3.10** — which reading of "the eight specified phases" is intended | The ticket defines a Phase 0 plus Phases 1–6, not eight; the eight numbered items 4.1–4.8 sit inside Phase 3. Both readings were answered in full rather than one being guessed. | Confirmation of which numbering the question refers to. |
| **Phase 0 of the enterprise-economics ticket** (within 3.10) | It is a reading-and-reporting step. It leaves no artifact, and nothing in the repository records that the required summary was produced. | The summary itself, or a record that it was delivered. |
| **9.14 confirmed by live observation** | Established by code inspection across three files rather than by provoking the failure, because provoking it would have written a row to the live database — which Rules 1 and 3 of this report forbid. The code path is unambiguous, but the 500 was not observed. | A throwaway database, or authorisation to write a colliding row. |

---

*End of report.*
