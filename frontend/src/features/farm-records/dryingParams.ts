import type { DryingMethod, DryingParams } from '../../types/domain';

// Form state and validation for a drying run, kept apart from the fields
// component so the rules can be unit-tested (and so the component file exports
// only components — react-refresh/only-export-components).

// One intermediate measurement, held as strings while it is being typed. A row
// with both boxes empty is a blank line the farmer has not filled in yet and is
// dropped; a half-filled one is an error, because silently discarding a typed
// number is how a reading goes missing without anybody noticing.
export interface DryingReadingForm {
  time_hours: string;
  moisture_wb: string;
}

export interface DryingForm {
  method: DryingMethod;
  mass_in_kg: string;
  mass_out_kg: string;
  moisture_initial_wb: string;
  moisture_final_wb: string;
  drying_time_hours: string;
  air_temperature_c: string;
  // Optional. Three or more usable readings unlock the Page-model fit and the
  // drying curve; with none, the run still saves and reports every other metric.
  readings: DryingReadingForm[];
}

export const emptyDryingReading: DryingReadingForm = { time_hours: '', moisture_wb: '' };

export const emptyDryingForm: DryingForm = {
  method: 'SUN',
  mass_in_kg: '',
  mass_out_kg: '',
  moisture_initial_wb: '',
  moisture_final_wb: '',
  drying_time_hours: '',
  air_temperature_c: '',
  readings: [],
};

// Mirrors backend schemas.DryingParams — the Field bounds AND the
// _check_physical_consistency model validator. Deliberately duplicated on the
// client for one reason: an invalid payload saved while offline would sit in
// IndexedDB re-failing on every flush until it exhausted its retries. Catching
// it here means nothing unsendable is ever queued.
//
// Returns the validated payload, or an error message to show the user.
export function buildDryingParams(f: DryingForm): { params: DryingParams } | { error: string } {
  const num = (v: string) => (v.trim() === '' ? NaN : Number(v));
  const massIn = num(f.mass_in_kg);
  const massOut = num(f.mass_out_kg);
  const mI = num(f.moisture_initial_wb);
  const mF = num(f.moisture_final_wb);
  const hours = num(f.drying_time_hours);
  const temp = f.air_temperature_c.trim() === '' ? null : num(f.air_temperature_c);

  if ([massIn, massOut, mI, mF, hours].some(Number.isNaN)) {
    return { error: 'Fill in mass in/out, moisture in/out and drying time.' };
  }
  if (massIn <= 0 || massIn > 100_000) return { error: 'Mass in must be between 0 and 100,000 kg.' };
  if (massOut <= 0) return { error: 'Mass out must be greater than 0 kg.' };
  if (massOut > massIn) return { error: 'Mass out cannot exceed mass in — drying removes water, it cannot add mass.' };
  if (mI <= 0 || mI >= 100) return { error: 'Starting moisture must be between 0 and 100 %.' };
  if (mF <= 0 || mF >= 100) return { error: 'Final moisture must be between 0 and 100 %.' };
  if (mF >= mI) return { error: 'Final moisture must be below starting moisture — otherwise this is wetting, not drying.' };
  if (hours <= 0 || hours > 720) return { error: 'Drying time must be between 0 and 720 hours.' };
  if (temp !== null && (Number.isNaN(temp) || temp < -10 || temp > 150)) {
    return { error: 'Air temperature must be between -10 and 150 °C.' };
  }

  // Intermediate readings, mirroring DryingReading's bounds and the three
  // readings-related clauses of _check_physical_consistency. Same reason as the
  // rest of this function: a 422 that only the server can see becomes a queued
  // record that can never sync.
  const rows = f.readings ?? [];
  const readings: { time_hours: number; moisture_wb: number }[] = [];
  let prevT: number | null = null;
  for (const row of rows) {
    const blankT = row.time_hours.trim() === '';
    const blankM = row.moisture_wb.trim() === '';
    if (blankT && blankM) continue;  // an untouched row, not an omission
    if (blankT || blankM) {
      return { error: 'Every reading needs both a time and a moisture — fill the row in or clear it.' };
    }
    const t = num(row.time_hours);
    const m = num(row.moisture_wb);
    if (Number.isNaN(t) || Number.isNaN(m)) {
      return { error: 'Readings must be numbers.' };
    }
    if (t <= 0 || t > 720) return { error: 'Each reading time must be between 0 and 720 hours.' };
    if (m <= 0 || m >= 100) return { error: 'Each reading moisture must be between 0 and 100 %.' };
    if (prevT !== null && t <= prevT) {
      return { error: 'Readings must go forward in time — each one later than the one above it.' };
    }
    // The band is the run's own start and end moisture. A reading outside it
    // describes a different run, not this one.
    if (m < mF || m > mI) {
      return { error: `Each reading moisture must sit between ${mF} and ${mI} % — the run's own end and start.` };
    }
    prevT = t;
    readings.push({ time_hours: t, moisture_wb: m });
  }

  return {
    params: {
      process_type: 'DRYING',
      method: f.method,
      mass_in_kg: massIn,
      mass_out_kg: massOut,
      moisture_initial_wb: mI,
      moisture_final_wb: mF,
      drying_time_hours: hours,
      ...(temp !== null ? { air_temperature_c: temp } : {}),
      // Omitted entirely when there are none: the backend defaults it to [], and
      // sending an empty array would be a difference without a distinction.
      ...(readings.length > 0 ? { readings } : {}),
    },
  };
}
