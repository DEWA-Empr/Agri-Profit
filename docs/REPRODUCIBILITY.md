# Reproducing the decision-support figures

What is claimed, under what conditions, and how to check it.

---

## 1. The claim, stated exactly

> The recorded environment + the recorded seeds + the same generator
> ⇒ the recorded metrics, within the recorded tolerance.

Nothing is claimed outside that. In particular, no claim is made that the yield
model predicts real Nigerian smallholder yields — the training data is
synthetic, generated from a parameterised agronomic response surface, so an R²
of 0.9762 measures how well a Random Forest recovers a relationship that was
constructed to be recoverable. It is evidence that the pipeline is correctly
implemented, and it is not evidence of field accuracy.

## 2. What is deterministic, and what that corrects

The pipeline is **seed-deterministic end to end**:

| Stage | Seed | Where |
|---|---|---|
| Synthetic draw | `np.random.default_rng(42)` | `backend/app/ml/dataset.py:generate` |
| Train/test split | `random_state=42` | `backend/app/ml/train.py:train_model` |
| Forest construction | `random_state=42` | `backend/app/ml/train.py:_build_estimator` |

This **supersedes** the statement in an earlier draft of Chapter 4 §4.9 that
"regenerating it by re-running the training script would produce different
figures, because the training data is synthesised afresh." The data is not
synthesised afresh in any meaningful sense — the seed is fixed, and a fresh
`generate()` is byte-identical to the cached CSV. That is asserted by
`test_the_cached_dataset_matches_a_fresh_draw`.

The genuine limitations are narrower, and both are real:

1. **The fitted artefact is not under version control.** `backend/app/ml/models/`
   and `backend/app/ml/data/` are gitignored, so the tagged commit does not
   carry the 60 MB `latest_model.joblib`. It is regenerated on first boot
   (`train.ensure_model`) or by the command in §4.
2. **The environment was not pinned.** `backend/requirements.txt` previously
   listed bare package names, so two installs from the same commit a month apart
   could resolve to different libraries. It now carries bounded ranges, with
   scikit-learn, numpy and pandas capped below the next *minor* because tree
   construction and RNG behaviour can move the reported metrics.

## 3. The recorded baseline

`backend/app/ml/model_baseline.json` is the artefact of record. It holds the
metrics, the seeds, the dataset fingerprint, the tolerance, and — the part that
makes it a reproducible result rather than three numbers — the environment they
were measured under.

| | |
|---|---|
| R² | **0.9762** |
| MAE | **0.2414** t/ha |
| RMSE | **0.4883** t/ha |
| Samples | 6,000 (synthetic) |
| Estimators | 200 |
| Test split | 0.2, `random_state=42` |
| Measured under | Python 3.14.5 · scikit-learn 1.9.0 · numpy 2.4.6 · pandas 3.0.3 |
| Tolerance | ±0.0005 absolute on each metric |

**RMSE was not previously reported.** Chapter 3 §3.8 names it as an available
complementary measure and Chapter 4 §4.9 records its absence as a gap. The value
above was measured by the command in §4, under the environment stated in the
same row. It should be re-derived before being quoted, in the environment the
thesis pins.

The dataset fingerprint is a SHA-256 over the float64 bytes of the numeric
columns plus the concatenated crop labels — deliberately **not** a hash of the
CSV text, because pandas' float formatting can change between versions and would
break the check for a reason unrelated to the data.

## 4. Re-deriving the figures

```bash
# Everything: determinism, the dataset fingerprint, and the recorded metrics.
python -m pytest backend/tests/test_reproducibility.py -v

# Just the metrics, printed.
cd backend && python -m app.ml.train
```

`test_the_metrics_match_the_baseline` **skips**, with the differing versions
named, when the running environment does not match the recorded one. That is
deliberate: asserting exact figures under an unknown scikit-learn would either
fail for the wrong reason or need a tolerance so wide it proved nothing. The
determinism tests still run, and still hold, in any environment.

## 5. If the environment moves

Re-record rather than widen the tolerance:

1. Install the environment you intend to pin.
2. Run `python -m pytest backend/tests/test_reproducibility.py`. The baseline
   test will skip and name the differences.
3. Regenerate `model_baseline.json` with the measured values **and the new
   environment block**.
4. Update the figures wherever the thesis quotes them, and say which environment
   they came from.

Do not edit the metrics without editing the environment beside them. A metric
whose conditions are stale is worse than no metric, because it looks checked.

## 6. Producing an exact lock for a deployment

The bounded ranges in `requirements.txt` are for development and CI. A
deployment that needs byte-identical installs should generate its own lock, from
the Python version it will actually run:

```bash
python -m venv .lockenv && . .lockenv/bin/activate     # Windows: .lockenv\Scripts\activate
pip install -r backend/requirements.txt
pip freeze --exclude-editable > backend/requirements-lock.txt
```

One is **not** committed here on purpose: a lock produced on one developer's
Python version is silently wrong for any other, and this project is run on at
least two (3.11 in CI, 3.14 locally). Generate it on the deployment target, keep
it beside the deployment, and regenerate it when you patch.

## 7. What is deterministic in the rest of the platform

Reproducibility is not only a machine-learning concern here. Two deterministic
reporting behaviours matter as much and are documented where they live:

- **The depreciation window.** A ledger-derived reporting period *widens* every
  time a log is entered, which silently moves the break-even price to cover
  total cost — so a figure reported last week cannot be re-derived. Pass
  `period_days` to pin it; every response says which was used in
  `period_source`. See `dss_service._equipment_overlay`.
- **Equipment corrections.** Correcting a depreciation rate moves the same
  chain. Since this cycle, a corrected asset carries `updated_at`, so a reader
  comparing two reports can tell whether the farm changed or the asset did.

Any figure quoted from this platform should travel with the reporting period it
was computed over, exactly as an ML metric travels with its environment.
