import type { CSSProperties } from 'react';
import { Plus, X } from 'lucide-react';
import type { DryingMethod } from '../../types/domain';
import { emptyDryingReading, type DryingForm } from './dryingParams';
import { colors } from '../../styles/theme';

// The drying-parameter block of the create form, shown only when the activity
// is "Post-harvest drying". A bioprocess log is rejected by the backend (422)
// unless extra_data validates as schemas.DryingParams, so these fields are the
// difference between the option working and it poisoning the offline queue.

const METHODS: { value: DryingMethod; label: string }[] = [
  { value: 'SUN', label: 'Sun drying' },
  { value: 'SOLAR_DRYER', label: 'Solar dryer' },
  { value: 'MECHANICAL', label: 'Mechanical dryer' },
  { value: 'AMBIENT', label: 'Ambient / shade' },
];

interface Props {
  value: DryingForm;
  onChange: (next: DryingForm) => void;
  label: CSSProperties;
  field: CSSProperties;
}

export const DryingFields = ({ value, onChange, label, field }: Props) => {
  const set = (key: keyof DryingForm) => (v: string) => onChange({ ...value, [key]: v });

  const addReading = () => onChange({ ...value, readings: [...value.readings, { ...emptyDryingReading }] });
  const removeReading = (index: number) =>
    onChange({ ...value, readings: value.readings.filter((_, i) => i !== index) });
  const setReading = (index: number, key: keyof typeof emptyDryingReading, v: string) =>
    onChange({
      ...value,
      readings: value.readings.map((row, i) => (i === index ? { ...row, [key]: v } : row)),
    });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
      <div className="grid-3">
        <div>
          <label style={label}>Drying method</label>
          <select value={value.method} onChange={(e) => set('method')(e.target.value)} style={field}>
            {METHODS.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
          </select>
        </div>
        <div>
          <label style={label}>Mass in (kg)</label>
          <input type="number" min="0" step="any" placeholder="e.g. 100" value={value.mass_in_kg} onChange={(e) => set('mass_in_kg')(e.target.value)} style={field} />
        </div>
        <div>
          <label style={label}>Mass out (kg)</label>
          <input type="number" min="0" step="any" placeholder="e.g. 84" value={value.mass_out_kg} onChange={(e) => set('mass_out_kg')(e.target.value)} style={field} />
        </div>
      </div>

      <div className="grid-3">
        <div>
          {/* Wet basis throughout: it is what a field moisture meter reads. The
              dry-basis conversion the kinetics need happens on the backend. */}
          <label style={label}>Moisture in (% wet basis)</label>
          <input type="number" min="0" max="100" step="any" placeholder="e.g. 25" value={value.moisture_initial_wb} onChange={(e) => set('moisture_initial_wb')(e.target.value)} style={field} />
        </div>
        <div>
          <label style={label}>Moisture out (% wet basis)</label>
          <input type="number" min="0" max="100" step="any" placeholder="e.g. 13" value={value.moisture_final_wb} onChange={(e) => set('moisture_final_wb')(e.target.value)} style={field} />
        </div>
        <div>
          <label style={label}>Drying time (hours)</label>
          <input type="number" min="0" step="any" placeholder="e.g. 10" value={value.drying_time_hours} onChange={(e) => set('drying_time_hours')(e.target.value)} style={field} />
        </div>
      </div>

      <div>
        <label style={label}>Air temperature (°C) <span style={{ fontWeight: 400 }}>(optional)</span></label>
        <input type="number" step="any" placeholder="e.g. 32" value={value.air_temperature_c} onChange={(e) => set('air_temperature_c')(e.target.value)} style={field} />
      </div>

      {/* Intermediate readings. Optional, and the run saves without them — but
          they are the only input that unlocks the drying curve and the Page-model
          fit, which is why the count is stated rather than left to be discovered.
          The backend has accepted this array since ticket 08 (schemas.DryingParams
          .readings); until now nothing in the interface could produce one, so the
          Page fit could only ever be exercised by the seed script. */}
      <div>
        <label style={label}>
          Moisture readings during the run <span style={{ fontWeight: 400 }}>(optional)</span>
        </label>
        <p style={{ fontSize: '10px', color: colors.textMuted, margin: '0 0 8px', lineHeight: 1.5 }}>
          Add a row each time you check the meter. Three or more give you the drying curve and the Page-model fit;
          fewer still save fine, and you just get the headline metrics.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {value.readings.map((row, i) => (
            <div key={i} style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <input
                type="number" min="0" step="any" placeholder={`Hour (e.g. ${(i + 1) * 2})`}
                value={row.time_hours}
                onChange={(e) => setReading(i, 'time_hours', e.target.value)}
                style={{ ...field, flex: 1 }}
                aria-label={`Reading ${i + 1} time in hours`}
              />
              <input
                type="number" min="0" max="100" step="any" placeholder="Moisture % wb"
                value={row.moisture_wb}
                onChange={(e) => setReading(i, 'moisture_wb', e.target.value)}
                style={{ ...field, flex: 1 }}
                aria-label={`Reading ${i + 1} moisture, per cent wet basis`}
              />
              <button
                type="button"
                onClick={() => removeReading(i)}
                aria-label={`Remove reading ${i + 1}`}
                title="Remove this reading"
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'center', flex: '0 0 auto',
                  width: '30px', height: '30px', borderRadius: '7px', cursor: 'pointer',
                  background: 'transparent', border: `1px solid ${colors.borderInput}`, color: colors.textMuted,
                }}
              >
                <X size={13} />
              </button>
            </div>
          ))}
        </div>

        <button
          type="button"
          onClick={addReading}
          style={{
            display: 'inline-flex', alignItems: 'center', gap: '6px', marginTop: value.readings.length ? '8px' : 0,
            background: 'transparent', border: `0.5px solid ${colors.borderInput}`, borderRadius: '7px',
            padding: '6px 11px', fontSize: '11px', fontWeight: 600, color: colors.textBody, cursor: 'pointer',
          }}
        >
          <Plus size={12} /> Add a reading
        </button>
      </div>
    </div>
  );
};
