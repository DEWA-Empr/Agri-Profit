import type { CSSProperties } from 'react';
import { Sprout } from 'lucide-react';
import { colors, cropTints, cardShadow } from '../../../styles/theme';
import { SectionHeader } from './SectionHeader';

interface FieldRow { field: string; crop: string; acres: number; yieldBu: number; revenue: string; margin: number; }

// NOTE: illustrative content — per-field records aren't modelled in the backend
// yet. The table layout, crop pills and colour-coded margin are the real design.
const FIELDS: FieldRow[] = [
  { field: 'North Quarter', crop: 'Maize', acres: 320, yieldBu: 182, revenue: '₦40.0M', margin: 28 },
  { field: 'River Bend', crop: 'Soybean', acres: 280, yieldBu: 58, revenue: '₦39.0M', margin: 24 },
  { field: 'Hill Block', crop: 'Wheat', acres: 240, yieldBu: 71, revenue: '₦30.0M', margin: 19 },
  { field: 'South Flats', crop: 'Maize', acres: 220, yieldBu: 164, revenue: '₦33.0M', margin: 16 },
  { field: 'East Paddock', crop: 'Soybean', acres: 180, yieldBu: 52, revenue: '₦24.0M', margin: 11 },
];

const marginColor = (m: number) => (m >= 20 ? colors.primaryDark : m >= 15 ? colors.warn : colors.danger);

const CropPill = ({ crop }: { crop: string }) => {
  const tint = cropTints[crop.toLowerCase()] ?? cropTints.default;
  return (
    <span style={{ display: 'inline-block', fontSize: '10px', fontWeight: 700, padding: '2px 9px', borderRadius: '20px', background: tint.bg, color: tint.fg }}>
      {crop}
    </span>
  );
};

export const FieldPerformance = () => {
  const th: CSSProperties = { textAlign: 'left', fontSize: '9.5px', fontWeight: 700, letterSpacing: '0.06em', color: colors.textMuted, textTransform: 'uppercase', padding: '0 12px 10px' };
  const td: CSSProperties = { fontSize: '12px', color: colors.textBody, padding: '11px 12px', borderTop: `0.5px solid ${colors.dividerLight}` };

  return (
    <div style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, boxShadow: cardShadow, padding: '20px', display: 'flex', flexDirection: 'column' }}>
      <SectionHeader
        icon={<Sprout size={15} color={colors.primary} />}
        title="Field performance"
        subtitle="Ranked by revenue"
        action={<span style={{ fontSize: '11px', color: colors.primary, fontWeight: 700, cursor: 'pointer' }}>View all →</span>}
      />

      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={th}>Field</th>
            <th style={th}>Crop</th>
            <th style={{ ...th, textAlign: 'right' }}>Acres</th>
            <th style={{ ...th, textAlign: 'right' }}>Yield</th>
            <th style={{ ...th, textAlign: 'right' }}>Revenue</th>
            <th style={{ ...th, textAlign: 'right' }}>Margin</th>
          </tr>
        </thead>
        <tbody>
          {FIELDS.map((f) => (
            <tr key={f.field}>
              <td style={{ ...td, fontWeight: 600, color: colors.textStrong }}>{f.field}</td>
              <td style={td}><CropPill crop={f.crop} /></td>
              <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{f.acres}</td>
              <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums', color: colors.textMuted }}>{f.yieldBu} bu</td>
              <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{f.revenue}</td>
              <td style={{ ...td, textAlign: 'right', fontWeight: 700, fontVariantNumeric: 'tabular-nums', color: marginColor(f.margin) }}>{f.margin}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
