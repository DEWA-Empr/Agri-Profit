import { describe, it, expect } from 'vitest'
import { buildDryingParams, emptyDryingForm } from './dryingParams'

// Ticket 08 (Fixture D): every payload the backend answers with 422 must be
// caught here first. This is not belt-and-braces validation — saveOperationalLog
// cannot distinguish a permanent 422 from a dropped connection, so an invalid
// drying run that reaches the offline queue re-fails on every flush until its
// retries run out. The client-side rules must therefore mirror
// schemas.DryingParams (field bounds AND _check_physical_consistency) exactly.
const valid = {
  ...emptyDryingForm,
  mass_in_kg: '100',
  mass_out_kg: '84',
  moisture_initial_wb: '25',
  moisture_final_wb: '13',
  drying_time_hours: '10',
}

describe('buildDryingParams', () => {
  it('builds the DRYING payload from a physically consistent run', () => {
    const result = buildDryingParams({ ...valid, air_temperature_c: '32' })
    expect(result).toEqual({
      params: {
        process_type: 'DRYING',
        method: 'SUN',
        mass_in_kg: 100,
        mass_out_kg: 84,
        moisture_initial_wb: 25,
        moisture_final_wb: 13,
        drying_time_hours: 10,
        air_temperature_c: 32,
      },
    })
  })

  it('omits air temperature entirely when it is left blank', () => {
    const result = buildDryingParams(valid)
    expect(result).not.toHaveProperty('error')
    expect('params' in result && 'air_temperature_c' in result.params).toBe(false)
  })

  it.each([
    ['mass out above mass in', { ...valid, mass_out_kg: '110' }],
    ['final moisture at or above initial', { ...valid, moisture_final_wb: '25' }],
    ['negative mass in', { ...valid, mass_in_kg: '-5' }],
    ['moisture above 100%', { ...valid, moisture_initial_wb: '105' }],
    ['zero drying time', { ...valid, drying_time_hours: '0' }],
    ['drying time beyond 720 h', { ...valid, drying_time_hours: '721' }],
    ['air temperature out of range', { ...valid, air_temperature_c: '200' }],
    ['a missing required field', { ...valid, mass_out_kg: '' }],
  ])('rejects %s', (_label, form) => {
    const result = buildDryingParams(form)
    expect('error' in result).toBe(true)
  })
})
