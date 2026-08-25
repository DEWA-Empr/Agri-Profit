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

// --- Intermediate readings -------------------------------------------------
//
// The backend has accepted `readings` since ticket 08, and until now nothing in
// the interface could produce one (docs/STATE_REPORT_2026-08-25.md Sections 4.5
// and 10.3): the Page-model fit could only ever be exercised by the seed
// script. These mirror the three readings clauses of
// _check_physical_consistency plus DryingReading's own bounds, for the same
// reason as everything above — a 422 only the server can see becomes a queued
// record that never syncs.

const reading = (time_hours: string, moisture_wb: string) => ({ time_hours, moisture_wb })

describe('buildDryingParams readings', () => {
  it('carries valid readings through in order', () => {
    const result = buildDryingParams({
      ...valid,
      readings: [reading('2', '21'), reading('5', '17'), reading('8', '14.5')],
    })
    expect('params' in result && result.params.readings).toEqual([
      { time_hours: 2, moisture_wb: 21 },
      { time_hours: 5, moisture_wb: 17 },
      { time_hours: 8, moisture_wb: 14.5 },
    ])
  })

  it('omits readings entirely when none were entered', () => {
    // The backend defaults the field to []; sending an empty array would be a
    // difference without a distinction, and the run must still save.
    const result = buildDryingParams({ ...valid, readings: [] })
    expect('params' in result && 'readings' in result.params).toBe(false)
  })

  it('drops rows the farmer added but never filled in', () => {
    // Clicking "Add a reading" and changing your mind must not fail the save.
    const result = buildDryingParams({
      ...valid,
      readings: [reading('2', '21'), reading('', ''), reading('5', '17')],
    })
    expect('params' in result && result.params.readings).toEqual([
      { time_hours: 2, moisture_wb: 21 },
      { time_hours: 5, moisture_wb: 17 },
    ])
  })

  it('rejects a half-filled row rather than silently discarding the number typed', () => {
    expect(buildDryingParams({ ...valid, readings: [reading('2', '')] })).toHaveProperty('error')
    expect(buildDryingParams({ ...valid, readings: [reading('', '21')] })).toHaveProperty('error')
  })

  it('rejects readings that do not go forward in time', () => {
    expect(buildDryingParams({
      ...valid, readings: [reading('5', '19'), reading('2', '17')],
    })).toHaveProperty('error')
  })

  it('rejects two readings at the same hour', () => {
    // The backend requires STRICTLY increasing time; equal timestamps are the
    // boundary case a >= check would let through.
    expect(buildDryingParams({
      ...valid, readings: [reading('5', '19'), reading('5', '17')],
    })).toHaveProperty('error')
  })

  it('rejects a reading outside the run\'s own moisture band', () => {
    // Above the start moisture...
    expect(buildDryingParams({ ...valid, readings: [reading('2', '26')] })).toHaveProperty('error')
    // ...and below the final one.
    expect(buildDryingParams({ ...valid, readings: [reading('2', '12')] })).toHaveProperty('error')
  })

  it('accepts a reading exactly on either edge of the band', () => {
    // The backend band is inclusive: [moisture_final_wb, moisture_initial_wb].
    expect(buildDryingParams({ ...valid, readings: [reading('2', '25')] })).not.toHaveProperty('error')
    expect(buildDryingParams({ ...valid, readings: [reading('2', '13')] })).not.toHaveProperty('error')
  })

  it('rejects a reading time beyond 720 h or at zero', () => {
    expect(buildDryingParams({ ...valid, readings: [reading('0', '21')] })).toHaveProperty('error')
    expect(buildDryingParams({ ...valid, readings: [reading('721', '21')] })).toHaveProperty('error')
  })

  it('rejects a non-numeric reading', () => {
    expect(buildDryingParams({ ...valid, readings: [reading('two', '21')] })).toHaveProperty('error')
  })
})
