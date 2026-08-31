import { describe, it, expect } from 'vitest'
import { buildCropOptions, normaliseCrop } from './cropOptions'

// Regression for docs/STATE_REPORT_2026-08-25.md Sections 7.4 / 10.3: the entry
// form carried a literal crop list copied from the yield model, so cowpea and
// tomato — both seeded, both with full ledgers, both visible in
// /dss/decision-support — could not be selected in the form that files their
// records. The options are now built from the API instead, and this pins the
// merge rules.

describe('buildCropOptions', () => {
  it('offers a crop the farm has recorded even though the model never saw it', () => {
    // The exact reported failure. cowpea and tomato are in the ledger; the
    // predictor's five crops do not include them.
    const options = buildCropOptions(
      ['cowpea', 'tomato', 'maize'],
      ['maize', 'rice', 'sorghum', 'soybean', 'cassava'],
    )
    expect(options).toContain('cowpea')
    expect(options).toContain('tomato')
  })

  it('keeps the predictor crops too, so a forecastable crop stays selectable', () => {
    const options = buildCropOptions(['cowpea'], ['maize', 'rice'])
    expect(options).toEqual(['cowpea', 'maize', 'rice'])
  })

  it('dedupes a crop present in both sources', () => {
    expect(buildCropOptions(['maize'], ['maize'])).toEqual(['maize'])
  })

  it('normalises case and surrounding space before deduping', () => {
    // The units field shows what happens without this: the live database holds
    // rice yields under `kg`, `bags` AND a distinct ` Kg`. Crop grouping in the
    // DSS is an exact string match, so 'Maize' and 'maize' would be two crops.
    expect(buildCropOptions([' Maize ', 'MAIZE'], ['maize'])).toEqual(['maize'])
  })

  it('drops the no-crop filing bucket rather than offering it as a crop', () => {
    // decision-support NEVER returns a null crop: a log with no crop comes back
    // under the literal string 'Unspecified' (dss_service.UNSPECIFIED). The
    // guard used to test for null only, so the bucket normalised to
    // 'unspecified' and reached the selector — and a farmer who picked it filed
    // a real crop by that name, sitting as a second row beside the bucket on
    // every DSS panel. It is a filing category, not something a farmer grows.
    expect(buildCropOptions(['Unspecified', 'maize'], [])).toEqual(['maize'])
    expect(buildCropOptions([null, undefined, '', '   ', 'UNSPECIFIED'], [])).toEqual([])
  })

  it('falls back to whichever source survived when the other request failed', () => {
    expect(buildCropOptions([], ['maize', 'rice'])).toEqual(['maize', 'rice'])
    expect(buildCropOptions(['cowpea'], [])).toEqual(['cowpea'])
    expect(buildCropOptions()).toEqual([])
  })

  it('sorts, so the list does not reorder itself between loads', () => {
    expect(buildCropOptions(['tomato', 'cassava'], ['maize'])).toEqual(['cassava', 'maize', 'tomato'])
  })
})

describe('normaliseCrop', () => {
  it('trims and lower-cases', () => {
    expect(normaliseCrop('  CowPea ')).toBe('cowpea')
  })
})
