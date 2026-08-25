import { describe, it, expect } from 'vitest'
import { partialBudgetLocal } from './partialBudget'

// The offline fallback has to agree with enterprise_service.partial_budget
// exactly, because the user cannot tell which one produced the number they are
// looking at beyond a small label. These cases mirror the backend's own.

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
