import { describe, it, expect } from 'vitest'
import { partialBudgetLocal } from './partialBudget'
import parityFixture from '../../fixtures/partial_budget_parity.json'

// The offline fallback has to agree with enterprise_service.partial_budget
// exactly, because the user cannot tell which one produced the number they are
// looking at beyond a small label. The cases below mirror the backend's own,
// and the PB-1..PB-8 block at the foot of this file no longer asks you to take
// that agreement on trust: it reads
// frontend/src/fixtures/partial_budget_parity.json, the same file read by
// backend/tests/test_enterprise_service.py, so both implementations are
// executed against one set of hand-computed expectations.

describe('partialBudgetLocal', () => {
  it('nets benefits against costs', () => {
    expect(partialBudgetLocal({
      added_revenue_ngn: 96000,
      reduced_cost_ngn: 21000,
      lost_revenue_ngn: 0,
      added_cost_ngn: 138500,
    })).toEqual({
      added_revenue_ngn: 96000,
      reduced_cost_ngn: 21000,
      lost_revenue_ngn: 0,
      added_cost_ngn: 138500,
      benefits_ngn: 117000,
      costs_ngn: 138500,
      net_change_ngn: -21500,
    })
  })

  it('returns a NEGATIVE net change signed and unclamped', () => {
    // The case the whole form exists for: a change that is not worth making.
    // Clamping this to zero would turn "do not do this" into "no difference".
    const result = partialBudgetLocal({
      added_revenue_ngn: 0,
      reduced_cost_ngn: 0,
      lost_revenue_ngn: 40000,
      added_cost_ngn: 12500,
    })
    expect(result.net_change_ngn).toBe(-52500)
  })

  it('echoes all four inputs back so the working can be shown', () => {
    const input = {
      added_revenue_ngn: 1,
      reduced_cost_ngn: 2,
      lost_revenue_ngn: 3,
      added_cost_ngn: 4,
    }
    expect(partialBudgetLocal(input)).toMatchObject(input)
  })

  it('treats an all-zero appraisal as zero, not as undefined', () => {
    // Four zeros is a legitimate statement — the change costs nothing and
    // gains nothing — and differs from having entered nothing at all, which
    // the form guards before it ever reaches this function.
    const result = partialBudgetLocal({
      added_revenue_ngn: 0,
      reduced_cost_ngn: 0,
      lost_revenue_ngn: 0,
      added_cost_ngn: 0,
    })
    expect(result.net_change_ngn).toBe(0)
  })
})

// --- PB-1..PB-8: cross-implementation parity -------------------------------
//
// Fixture: frontend/src/fixtures/partial_budget_parity.json
//
// The twin of this block is in backend/tests/test_enterprise_service.py. Both
// read the SAME file, so a term added to one implementation of the partial
// budget and not the other turns one of the two suites red instead of leaving
// both green.
//
// The expected values are HAND-COMPUTED and must never be regenerated from
// either implementation. A generated expectation makes its source
// definitionally correct: the test would then detect divergence but could never
// detect that both sides are wrong in the same way. If an implementation
// disagrees with a case here, the implementation is wrong, not the fixture.
//
// The import below is deliberately unguarded. There is no skip, no try/catch,
// and no fallback value: a parity test that quietly passes when it cannot find
// its input is indistinguishable from no parity test at all, which is the exact
// condition this fixture exists to end. A missing file fails resolution at
// import time and a malformed one fails to parse, both before any test runs.

// Declared here as well as in the file, so that silently shrinking the fixture
// fails this suite rather than passing quietly with fewer cases.
const EXPECTED_PARITY_CASE_COUNT = 8

const parityCases = parityFixture.cases

describe('partialBudgetLocal parity with enterprise_service.partial_budget', () => {
  it('reads a fixture whose declared count matches its contents', () => {
    // The fixture carries its own count. A truncated-but-parseable file must
    // fail here rather than silently running fewer cases than it claims.
    const declared = parityFixture.case_count
    const actual = parityCases.length
    expect(declared, `partial_budget_parity.json: case_count is ${declared} but cases has ${actual} entries`).toBe(actual)
    expect(actual, `partial_budget_parity.json: expected ${EXPECTED_PARITY_CASE_COUNT} cases but found ${actual}`).toBe(EXPECTED_PARITY_CASE_COUNT)
    expect(parityCases.map((c) => c.id)).toEqual(
      Array.from({ length: EXPECTED_PARITY_CASE_COUNT }, (_, i) => `PB-${i + 1}`),
    )
    // field_mapping is executed documentation, not a comment that happens to be
    // JSON: its values are the input keys every case must actually use.
    const mapped = Object.values(parityFixture.field_mapping).sort()
    for (const c of parityCases) {
      expect(Object.keys(c.inputs).sort(), c.id).toEqual(mapped)
    }
  })

  it.each(parityCases)('$id matches its hand-computed expectation', ({ inputs, expected, arithmetic }) => {
    const result = partialBudgetLocal(inputs).net_change_ngn
    // PB-7 is the precision case, so the comparison is to 9 significant places
    // rather than exact — the vitest equivalent of pytest.approx(rel=1e-9).
    // Everything else is exact in binary floating point and compared with toBe,
    // which uses Object.is and so also rejects a negative zero.
    if (Number.isInteger(expected)) {
      expect(result, arithmetic).toBe(expected)
    } else {
      expect(result, arithmetic).toBeCloseTo(expected, 9)
    }
  })

  it('PB-1 has the right SIGN, asserted separately from its magnitude', () => {
    // A test that compared only absolute values would pass a reversed
    // implementation, so the sign is asserted on its own.
    const pb1 = parityCases.find((c) => c.id === 'PB-1')!
    const result = partialBudgetLocal(pb1.inputs).net_change_ngn
    expect(result).toBeLessThan(0)
    expect(Math.abs(result)).toBe(21500)
    expect(result).toBe(-21500)
  })

  it('PB-3 is exactly zero and NOT negative zero', () => {
    // The boundary between better off and worse off. A negative zero rendering
    // as "-NGN 0.00" would tell a farmer they are worse off when they are
    // exactly even. Object.is distinguishes the two; == does not.
    const pb3 = parityCases.find((c) => c.id === 'PB-3')!
    const result = partialBudgetLocal(pb3.inputs).net_change_ngn
    expect(result).toBe(0)
    expect(Object.is(result, -0)).toBe(false)
  })
})
