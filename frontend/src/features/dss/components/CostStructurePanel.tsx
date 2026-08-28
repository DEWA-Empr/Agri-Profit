import { Layers } from 'lucide-react';
import { colors } from '../../../styles/theme';
import { naira, pct, DASH } from '../format';
import type { CropCostStructure, CropBreakEvenPrice } from '../../../types/domain';

// Cost structure for one crop: the four behaviour lines, and the classification
// coverage that qualifies every one of them.
//
// COVERAGE IS TEXT, NOT A GAUGE, and that is a deliberate refusal rather than a
// styling shortcut. A gauge — a dial, a progress bar, a ring — implies a target
// and a shortfall, and there is no target here. 100% classified cost is not a
// goal the platform sets or the farmer is failing to meet; coverage is a
// property of what happens to be recorded, and its only job is to tell the
// reader how much of the figure below it rests on classified cost. A bar at 92%
// invites "get it to 100"; a sentence saying which share is classified invites
// reading the number correctly, which is all that is wanted.

const LINE_LABEL = '10px';

const Line = ({ label, value, note, strong, muted }: {
  label: string; value: string; note?: string; strong?: boolean; muted?: boolean;
}) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '12px', padding: '7px 0', borderBottom: `0.5px solid ${colors.dividerLight}` }}>
    <div style={{ minWidth: 0 }}>
      <span style={{ fontSize: '11.5px', fontWeight: strong ? 700 : 500, color: muted ? colors.textMuted : colors.textBody }}>{label}</span>
      {note && <span style={{ display: 'block', fontSize: '10px', color: colors.textFaint, marginTop: '1px', lineHeight: 1.45 }}>{note}</span>}
    </div>
    <span style={{ fontSize: '12px', fontWeight: strong ? 800 : 600, color: muted ? colors.textMuted : colors.text, whiteSpace: 'nowrap' }}>{value}</span>
  </div>
);

export const CostStructurePanel = ({ structure, breakEven, card }: {
  structure: CropCostStructure;
  // The allocated fixed line lives on the break-even response, not the cost
  // structure, because it is a derived overlay rather than anything recorded.
  // It is shown here anyway — the four lines only add up to a decision when the
  // reader can see all four together — and it is labelled as not-recorded.
  breakEven?: CropBreakEvenPrice;
  card: React.CSSProperties;
}) => {
  const coverage = structure.classification_coverage_pct;
  const allocated = breakEven?.allocated_fixed_ngn;

  return (
    <div style={card}>
      <h3 style={{ fontSize: '12px', fontWeight: 700, color: colors.text, display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '0.5px solid #eee', paddingBottom: '10px', marginBottom: '10px' }}>
        <Layers size={15} color={colors.primary} /> Cost structure
      </h3>

      <Line
        label="Variable cost"
        note="Scales with what you produce — seed, fertiliser, labour, fuel, hire"
        value={naira(structure.variable_cost)}
      />
      <Line
        label="Semi-variable cost"
        note="Part fixed, part scaling — repairs. Counted as cash, shown apart"
        value={naira(structure.semi_variable_cost)}
      />
      <Line
        label="Unclassified cost"
        note="Recorded spending carrying no cost subtype. Not assumed variable"
        value={naira(structure.unclassified_cost)}
        muted={structure.unclassified_cost === 0}
      />
      <Line
        label="Allocated fixed cost"
        note="Depreciation worked out at read time, not a ledger entry"
        value={allocated == null ? DASH : naira(allocated)}
        muted={allocated == null}
      />
      {structure.fixed_cost_recorded > 0 && (
        <Line
          label="Recorded fixed cost"
          note="A depreciation charge you entered yourself — separate from the allocation above, never added to it"
          value={naira(structure.fixed_cost_recorded)}
        />
      )}
      <Line label="Total recorded cost" value={naira(structure.total_recorded_cost)} strong />

      {/* COVERAGE, AS A SENTENCE. See the note at the top of this file for why
          there is no bar here. */}
      <div style={{ marginTop: '12px', background: colors.surfaceMuted, borderRadius: '8px', padding: '11px 13px' }}>
        <p style={{ fontSize: LINE_LABEL, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: colors.textMuted }}>
          Classification coverage
        </p>
        {coverage == null ? (
          <p style={{ fontSize: '11.5px', color: colors.textBody, marginTop: '5px', lineHeight: 1.6 }}>
            No cost is recorded for this crop, so there is no coverage to report. This is not 0% — there is
            nothing yet to classify.
          </p>
        ) : (
          <p style={{ fontSize: '11.5px', color: colors.textBody, marginTop: '5px', lineHeight: 1.6 }}>
            <strong>{pct(coverage)}</strong> of this crop&rsquo;s recorded cost carries a cost subtype.
            {coverage < 100
              ? ' The rest is spending you recorded without saying what kind it was, so it sits inside the total cost figure and outside the cash one. Read the prices below against that.'
              : ' Every recorded naira is classified, so both prices below rest on the full cost.'}
          </p>
        )}
      </div>

      {/* The operating expense ratio. It is a naira-over-naira cash measure, so
          it sits here with the cost structure rather than beside the two
          per-kilogram prices, where it would read as a third price. */}
      <div style={{ marginTop: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '12px' }}>
        <div>
          <span style={{ fontSize: '11.5px', fontWeight: 600, color: colors.textBody }}>Operating expense ratio</span>
          <span style={{ display: 'block', fontSize: '10px', color: colors.textFaint, marginTop: '1px', lineHeight: 1.45 }}>
            {structure.operating_expense_ratio_pct == null
              ? 'No revenue recorded, so there is nothing for the cost to be a share of'
              : `Cash operating cost ${naira(structure.cash_operating_cost_ngn)} against revenue ${naira(structure.revenue_ngn)}`}
          </span>
        </div>
        <span style={{ fontSize: '12px', fontWeight: 800, color: structure.operating_expense_ratio_pct == null ? colors.textMuted : colors.text, whiteSpace: 'nowrap' }}>
          {structure.operating_expense_ratio_pct == null ? DASH : pct(structure.operating_expense_ratio_pct)}
        </span>
      </div>
    </div>
  );
};
