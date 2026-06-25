import { colors, cardShadow } from '../../../styles/theme';

type DeltaTone = 'up' | 'down' | 'neutral';

interface MetricCardProps {
  label: string;
  value: string;
  delta?: string;
  deltaTone?: DeltaTone;
  /** Tiny trend series rendered as a sparkline in the card corner. */
  spark?: number[];
  /** Highlight the primary metric with a green-tinted surface. */
  highlight?: boolean;
}

const toneColor: Record<DeltaTone, string> = {
  up: colors.primaryDark,
  down: colors.danger,
  neutral: colors.textMuted,
};

const toneBg: Record<DeltaTone, string> = {
  up: 'rgba(99,153,34,0.12)',
  down: 'rgba(192,57,43,0.10)',
  neutral: 'rgba(0,0,0,0.05)',
};

// A small inline-SVG sparkline (no chart library needed for ~6 points). The
// line is tinted by the metric's delta tone so a falling cost reads red.
const Sparkline = ({ points, color }: { points: number[]; color: string }) => {
  const w = 72;
  const h = 26;
  const min = Math.min(...points);
  const max = Math.max(...points);
  const span = max - min || 1;
  const coords = points.map((p, i) => {
    const x = (i / (points.length - 1)) * w;
    const y = h - ((p - min) / span) * h;
    return [x, y] as const;
  });
  const line = coords.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ');
  const area = `0,${h} ${line} ${w},${h}`;
  const gradId = `spark-${color.replace('#', '')}`;
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ display: 'block' }} aria-hidden>
      <defs>
        <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.18} />
          <stop offset="100%" stopColor={color} stopOpacity={0} />
        </linearGradient>
      </defs>
      <polygon points={area} fill={`url(#${gradId})`} />
      <polyline points={line} fill="none" stroke={color} strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

// Single KPI tile in the dashboard metric row: a tiny tracked label, a large
// number, an optional signed delta chip, and a corner sparkline (#04 "Native"
// style, refined per the reviewed standalone mockup).
export const MetricCard = ({ label, value, delta, deltaTone = 'up', spark, highlight }: MetricCardProps) => (
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
    <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: '8px' }}>
      {delta ? (
        <span style={{
          fontSize: '10px', fontWeight: 700, padding: '2px 7px', borderRadius: '6px',
          color: toneColor[deltaTone], backgroundColor: toneBg[deltaTone],
        }}>
          {delta}
        </span>
      ) : <span />}
      {spark && spark.length > 1 && <Sparkline points={spark} color={toneColor[deltaTone]} />}
    </div>
  </div>
);
