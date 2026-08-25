import { TableProperties } from 'lucide-react';
import { colors } from '../../../styles/theme';
import { nairaPerKg, DASH } from '../format';
import type { CropSensitivity, SensitivityResponse } from '../../../types/domain';

// Yield sensitivity — A TABLE, AND DELIBERATELY NOT A CHART.
//
// This is the single feature on the platform most likely to break its own
// strongest reporting convention, which is that nothing here ever implies a
// price forecast. The existing break-even YIELD is retrospective on purpose —
// "what tonnage would have covered your costs at the price you actually got" —
// specifically so that no screen can be read as predicting a price.
//
// Plot these same five rows as a line and the convention is gone. A line
// sloping down and to the right reads as a trajectory, an expectation, a thing
// the farm is heading towards; the eye extrapolates past the last point without
// being asked to, and the reader leaves believing the platform told them what
// the price will be. It told them no such thing. Every row is a conditional
// with its own independent antecedent: IF the harvest comes in at this mass,
// THEN this is the price that covers the cost. The rows are five separate
// questions, not five samples of one trend, and a table is the only form that
// says so — you read a table one row at a time, which is exactly right here.
//
// recharts is already a dependency and drawing this as a chart would have been
// less code. It is a table because it should be.

const th: React.CSSProperties = {
  fontSize: '9.5px', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase',
  color: colors.textMuted, textAlign: 'right', padding: '7px 8px', borderBottom: `1px solid ${colors.border}`,
  whiteSpace: 'nowrap',
};
const thLeft: React.CSSProperties = { ...th, textAlign: 'left' };
const td: React.CSSProperties = {
  fontSize: '11.5px', color: colors.textBody, textAlign: 'right', padding: '8px',
  borderBottom: `0.5px solid ${colors.dividerLight}`, whiteSpace: 'nowrap',
};
const tdLeft: React.CSSProperties = { ...td, textAlign: 'left' };

export const SensitivityTable = ({ crop, meta, card }: {
  crop: CropSensitivity;
  meta: SensitivityResponse;
  card: React.CSSProperties;
}) => {
  if (crop.baseline_marketable_mass_kg == null) {
    return (
      <div style={card}>
        <h3 style={{ fontSize: '12px', fontWeight: 700, color: colors.text, display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '0.5px solid #eee', paddingBottom: '10px', marginBottom: '12px' }}>
          <TableProperties size={15} color={colors.primary} /> If you harvest this much, this is the price you would need
        </h3>
        <p style={{ fontSize: '11.5px', color: colors.textBody, lineHeight: 1.6 }}>
          There is nothing to vary. Every row of this table is a percentage of the crop&rsquo;s marketable mass, and
          this crop has no recorded drying run to take a baseline from.
        </p>
      </div>
    );
  }

  return (
    <div style={card}>
      {/* THE CONDITIONAL, IN THE HEADING ITSELF — not in a footnote, not in a
          tooltip, not in a badge beside it. A reader who reads only the heading
          and the numbers must still come away with the conditional. */}
      <h3 style={{ fontSize: '12px', fontWeight: 700, color: colors.text, display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '0.5px solid #eee', paddingBottom: '10px', marginBottom: '4px' }}>
        <TableProperties size={15} color={colors.primary} /> If you harvest this much, this is the price you would need
      </h3>
      <p style={{ fontSize: '10.5px', color: colors.textMuted, lineHeight: 1.6, margin: '8px 0 12px' }}>
        Each row is a separate question, not a step in a trend. This forecasts <strong>neither</strong> your harvest
        <strong> nor</strong> the price you will get — it says what price would cover your costs at each of five
        harvest sizes, so you can see how much the answer moves. The baseline is your recorded marketable mass
        of {crop.baseline_marketable_mass_kg.toLocaleString(undefined, { maximumFractionDigits: 2 })} kg.
      </p>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={thLeft}>If you harvest</th>
              <th style={th}>Marketable mass</th>
              <th style={th}>Break-even price<br />to cover cash cost</th>
              <th style={th}>Break-even price<br />to cover total cost</th>
            </tr>
          </thead>
          <tbody>
            {crop.rows.map((r) => {
              // The 100% row is the farm's actual recorded mass rather than a
              // hypothetical, so it is marked. Without the marker the reader
              // cannot tell which row is the one they are standing on.
              const isBaseline = r.percentage === 100;
              return (
                <tr key={r.percentage} style={isBaseline ? { background: colors.primarySurface } : undefined}>
                  <td style={{ ...tdLeft, fontWeight: isBaseline ? 700 : 500 }}>
                    {r.percentage}% of what you recorded
                    {isBaseline && <span style={{ color: colors.primaryDark, fontWeight: 700 }}> · what you recorded</span>}
                  </td>
                  <td style={td}>
                    {r.marketable_mass_kg == null ? DASH : `${r.marketable_mass_kg.toLocaleString(undefined, { maximumFractionDigits: 2 })} kg`}
                  </td>
                  <td style={{ ...td, fontWeight: 700 }}>
                    {r.break_even_price_cash_ngn_per_kg == null ? DASH : nairaPerKg(r.break_even_price_cash_ngn_per_kg)}
                  </td>
                  <td style={{ ...td, fontWeight: 700 }}>
                    {r.break_even_price_total_ngn_per_kg == null ? DASH : nairaPerKg(r.break_even_price_total_ngn_per_kg)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p style={{ fontSize: '10px', color: colors.textFaint, marginTop: '10px', lineHeight: 1.6 }}>
        Both columns move with the depreciation window
        {meta.period_source === 'derived'
          ? ` of ${meta.period_days.toLocaleString(undefined, { maximumFractionDigits: 0 })} days taken from the span of your records, which widens as you enter more.`
          : ` of ${meta.period_days.toLocaleString(undefined, { maximumFractionDigits: 0 })} days that you specified.`}
      </p>
    </div>
  );
};
