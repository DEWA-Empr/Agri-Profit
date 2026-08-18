import type { CSSProperties } from 'react';
import type { DryingMethod } from '../../types/domain';
import type { DryingForm } from './dryingParams';

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
    </div>
  );
};
