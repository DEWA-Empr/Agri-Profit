import { Scale } from 'lucide-react';
import { colors } from '../../../styles/theme';
import { naira, nairaPerKg, pct, DASH } from '../format';
import type { CropBreakEvenPrice, BreakEvenPriceResponse } from '../../../types/domain';

// The two conditional break-even prices, side by side.
//
// NAMING. Neither figure is ever called "break-even" on its own anywhere in
// this file. The platform already shows a RETROSPECTIVE break-even YIELD on the
// dashboard ("what tonnage would have covered your costs at the price you got"),
// and these two are CONDITIONAL break-even PRICES answering a different
// question in the opposite direction. Three distinct metrics, one careless
// word: register finding P1-04 is exactly this failure — the same model
// carrying two tier numbers in one document — and the full names are the whole
// defence against repeating it. "Break-even price to cover cash cost" and
// "Break-even price to cover total cost", in full, every time.

const PriceTile = ({ label, value, reading, accent }: {
  label: string; value: string; reading: string; accent: string;
}) => (
  <div style={{ background: colors.surfaceMuted, border: `0.5px solid ${colors.border}`, borderRadius: '9px', padding: '13px' }}>
    {/* The label wraps to two or three lines and is allowed to. Truncating it
        to fit a tile would produce the bare word this panel exists to avoid. */}
    <p style={{ fontSize: '10px', fontWeight: 700, letterSpacing: '0.04em', textTransform: 'uppercase', color: accent, lineHeight: 1.4 }}>
      {label}
    </p>
    <p style={{ fontSize: '19px', fontWeight: 800, color: colors.text, marginTop: '6px' }}>
      {value}
      {value !== DASH && <span style={{ fontSize: '11px', fontWeight: 700, color: colors.textMuted }}> /kg marketable</span>}
    </p>
    <p style={{ fontSize: '10.5px', color: colors.textFaint, marginTop: '6px', lineHeight: 1.55 }}>{reading}</p>
  </div>
);

export const BreakEvenPricePanel = ({ crop, meta, card }: {
  crop: CropBreakEvenPrice;
  meta: BreakEvenPriceResponse;
  card: React.CSSProperties;
}) => {
  const cash = crop.break_even_price_cash_ngn_per_kg;
  const total = crop.break_even_price_total_ngn_per_kg;
  const coverage = crop.classification_coverage_pct;

  return (
    <div style={card}>
      <h3 style={{ fontSize: '12px', fontWeight: 700, color: colors.text, display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '0.5px solid #eee', paddingBottom: '10px', marginBottom: '12px' }}>
        <Scale size={15} color={colors.primary} /> Break-even prices to cover cash and total cost
      </h3>

      {crop.marketable_mass_kg == null ? (
        /* Undefined, and said so in words. Both prices divide by marketable
           mass, and this crop has no drying run to supply one. A zero here
           would be a fabricated answer to a question that has none. */
        <div style={{ background: colors.surfaceMuted, borderRadius: '8px', padding: '13px' }}>
          <p style={{ fontSize: '11.5px', color: colors.textBody, lineHeight: 1.6 }}>
            Neither price can be worked out for this crop. Both are a price <em>per kilogram marketable</em>, and
            marketable mass comes from a recorded drying run — this crop has none. A crop sold fresh at the farm gate
            has no marketable mass to divide by, so the figures are undefined rather than zero.
          </p>
        </div>
      ) : (
        <>
          <div className="grid-2" style={{ gap: '11px' }}>
            <PriceTile
              label="Break-even price to cover cash cost"
              value={cash == null ? DASH : nairaPerKg(cash)}
              reading="Below this, every extra kilogram you sell loses money on the spot. It counts only what you have already paid out — the variable and semi-variable cost."
              accent={colors.warnAccent}
            />
            <PriceTile
              label="Break-even price to cover total cost"
              value={total == null ? DASH : nairaPerKg(total)}
              reading="The price that also pays for the machine wearing out. It counts every recorded cost plus this crop's share of depreciation."
              accent={colors.primaryDark}
            />
          </div>

          {/* The four cost lines behind the two prices, kept apart rather than
              collapsed into two, because unclassified cost sits inside the
              total figure and outside the cash one — so it widens the gap
              between them without belonging to either argument. */}
          <div style={{ marginTop: '13px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {[
              ['Variable and semi-variable cost', naira(crop.variable_and_semi_variable_cost_ngn), 'the cash figure divides this'],
              ['Total recorded cost', naira(crop.total_recorded_cost_ngn), 'includes unclassified spending'],
              ['Allocated fixed cost', crop.allocated_fixed_ngn == null ? DASH : naira(crop.allocated_fixed_ngn), 'this crop’s share of depreciation'],
              ['Total cost', naira(crop.total_cost_ngn), 'the total figure divides this'],
            ].map(([label, value, note]) => (
              <div key={label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '10px' }}>
                <span style={{ fontSize: '11px', color: colors.textMuted }}>
                  {label} <span style={{ color: colors.textFaint }}>— {note}</span>
                </span>
                <span style={{ fontSize: '11px', fontWeight: 700, color: colors.textBody, whiteSpace: 'nowrap' }}>{value}</span>
              </div>
            ))}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '10px', marginTop: '2px' }}>
              <span style={{ fontSize: '11px', color: colors.textMuted }}>Marketable mass</span>
              <span style={{ fontSize: '11px', fontWeight: 700, color: colors.textBody }}>
                {crop.marketable_mass_kg.toLocaleString(undefined, { maximumFractionDigits: 2 })} kg
              </span>
            </div>
          </div>
        </>
      )}

      {/* Coverage travels with both prices, as text. It is repeated here rather
          than left on the cost-structure panel alone because a price read
          without it is a stronger claim than the data supports. */}
      {coverage != null && coverage < 100 && (
        <p style={{ fontSize: '10.5px', color: colors.warn, marginTop: '12px', lineHeight: 1.6 }}>
          Only {pct(coverage)} of this crop&rsquo;s cost is classified. The unclassified remainder is inside the
          break-even price to cover total cost and outside the break-even price to cover cash cost, so the gap
          between the two figures is wider than the classified cost alone would make it.
        </p>
      )}

      {/* The overlay's own qualifications: which window, and how much of the
          farm's equipment the charge could actually be computed over. */}
      <p style={{ fontSize: '10px', color: colors.textFaint, marginTop: '10px', lineHeight: 1.6, borderTop: `0.5px solid ${colors.dividerLight}`, paddingTop: '9px' }}>
        Depreciation of {naira(meta.period_fixed_cost_ngn)} over {meta.period_days.toLocaleString(undefined, { maximumFractionDigits: 0 })} days
        {meta.period_source === 'derived'
          ? ', taken from the span of your records — it widens as you enter more, so this price moves with it.'
          : ', over the period you specified.'}
        {meta.equipment_unrated_count > 0 && (
          <>
            {' '}
            <span style={{ color: colors.warn }}>
              {meta.equipment_unrated_count} of your {meta.equipment_count} assets {meta.equipment_unrated_count === 1 ? 'has' : 'have'} no
              depreciation rate recorded, so {meta.equipment_unrated_count === 1 ? 'it is' : 'they are'} left out of this charge
              rather than counted as costing nothing.
            </span>
          </>
        )}
      </p>
    </div>
  );
};
