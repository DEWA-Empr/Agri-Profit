import { useEffect, useState } from 'react';
import { Lightbulb } from 'lucide-react';
import { colors, accents, cardShadow } from '../../../styles/theme';
import { SectionHeader } from './SectionHeader';
import { EmptyState } from '../../../components/EmptyState';
import { dssService } from '../../../lib/apiClient';
import type { DssDecisionSupport, DssCropMetrics } from '../../../types/domain';

// Tier 1 deterministic decision support: per-crop unit cost of production and
// gross margin, computed on the backend from the farm's REAL ledger (no model,
// no synthetic numbers). Replaces the former hardcoded advice array — every
// figure here is derived from recorded operations and their paired financials.

const naira = (n: number): string => {
  const abs = Math.abs(n);
  const body =
    abs >= 1_000_000 ? `${(abs / 1_000_000).toFixed(2)}M`
    : abs >= 1_000 ? `${(abs / 1_000).toFixed(1)}K`
    : abs.toLocaleString(undefined, { maximumFractionDigits: 0 });
  return `${n < 0 ? '−' : ''}₦${body}`;
};

// What to say about unit cost, given the three states the backend distinguishes:
// a real figure, no yield at all, or yields spanning more than one unit.
const unitCostLine = (c: DssCropMetrics, cost?: number | null): string => {
  if (cost != null && c.yield_quantity != null && c.yield_quantity > 0) {
    return `Unit cost of production ${naira(cost)}/${c.yield_unit ?? 'unit'}`;
  }
  if ((c.yield_by_unit?.length ?? 0) > 1) {
    return 'Unit cost — needs one harvest unit';
  }
  return 'Unit cost — no yield recorded yet';
};

const CropRow = ({ c }: { c: DssCropMetrics }) => {
  // A profitable crop reads as an opportunity; a loss-making one as an alert.
  const a = c.gross_margin >= 0 ? accents.insight : accents.alert;
  const cost = c.unit_cost_of_production;
  const byUnit = c.yield_by_unit ?? [];
  const mixedUnits = byUnit.length > 1;
  return (
    <div style={{ background: a.bg, borderLeft: `3px solid ${a.bar}`, borderRadius: '7px', padding: '11px 13px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '10px' }}>
        <span style={{ fontSize: '12px', fontWeight: 700, color: colors.textStrong, textTransform: 'capitalize' }}>{c.crop}</span>
        <span style={{ fontSize: '12px', fontWeight: 800, color: a.fg }}>{naira(c.gross_margin)}</span>
      </div>
      <p style={{ fontSize: '10px', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: a.fg, marginTop: '2px' }}>
        Gross margin
      </p>
      <p style={{ fontSize: '11px', color: colors.textMuted, marginTop: '6px', lineHeight: 1.5 }}>
        Revenue {naira(c.revenue)} · Cost {naira(c.expenses)}
        <br />
        {unitCostLine(c, cost)}
        {/* With more than one harvest unit there is no single total to divide
            by, so we show the breakdown instead of a made-up figure. */}
        {mixedUnits && (
          <>
            <br />
            <span style={{ color: colors.warn }}>
              Yield recorded in {byUnit.map((y) => `${y.quantity.toLocaleString()} ${y.unit ?? 'no unit'}`).join(' + ')} — mixed units, so no single total
            </span>
          </>
        )}
      </p>
    </div>
  );
};

export const DecisionSupport = () => {
  const [data, setData] = useState<DssDecisionSupport | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    dssService.getDecisionSupport()
      .then((res) => setData(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoaded(true));
  }, []);

  const crops = data?.crops ?? [];

  return (
    <div style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, boxShadow: cardShadow, padding: '20px', display: 'flex', flexDirection: 'column' }}>
      <SectionHeader
        icon={<Lightbulb size={15} color={colors.primary} />}
        title="Decision support"
        subtitle={loaded ? `${crops.length} crop${crops.length === 1 ? '' : 's'} from your ledger` : 'Loading…'}
      />

      {loaded && crops.length === 0 ? (
        <EmptyState
          bare
          icon={<Lightbulb size={22} color={colors.primary} />}
          title="No crop metrics yet"
          description="Tag your operations with a crop and record their costs and sales. Unit cost of production and gross margin appear here as your ledger fills."
        />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {crops.map((c) => <CropRow key={c.crop} c={c} />)}
        </div>
      )}
    </div>
  );
};
