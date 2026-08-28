import { colors, cardShadow } from '../../../styles/theme';

interface MetricCardProps {
  label: string;
  value: string;
  /** Highlight the primary metric with a green-tinted surface. */
  highlight?: boolean;
}

// Single KPI tile in the dashboard metric row: a tiny tracked label and a large
// number, both derived from the farm's ledger.
//
// The tile deliberately carries no delta chip and no sparkline. Both were
// removed with the mock data they displayed: there is no prior-period history
// in the model to compute a YoY delta from, and no per-tile series behind a
// sparkline. A trend drawn here would be decoration, not measurement.
export const MetricCard = ({ label, value, highlight }: MetricCardProps) => (
  <div className="card-interactive" style={{
    backgroundColor: highlight ? colors.primarySurface : colors.surface,
    borderRadius: '12px',
    padding: '15px 16px',
    border: highlight ? `0.5px solid ${colors.primaryBorderTint}` : `0.5px solid ${colors.border}`,
    boxShadow: cardShadow,
    display: 'flex',
    flexDirection: 'column',
    gap: '9px',
    flex: 1,
    minWidth: 0,
  }}>
    <span style={{ fontSize: '9.5px', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: colors.textMuted }}>
      {label}
    </span>
    <span style={{ fontSize: '23px', fontWeight: 600, letterSpacing: '-0.5px', color: highlight ? colors.primaryDarker : colors.textStrong, lineHeight: 1 }}>
      {value}
    </span>
  </div>
);
