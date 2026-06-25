import { useEffect, useState } from 'react';
import { PieChart as PieIcon } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { reportsService } from '../../../lib/apiClient';
import type { PnlReport } from '../../../types/domain';
import { colors, categoryColors, cardShadow } from '../../../styles/theme';
import { SectionHeader } from './SectionHeader';

const naira = (n: number) => `₦${n.toLocaleString()}`;
// Compact ₦ for the donut centre + legend amounts (₦132K, ₦1.2M).
const nairaShort = (n: number) => {
  if (n >= 1_000_000) return `₦${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `₦${Math.round(n / 1_000)}K`;
  return `₦${n}`;
};

interface Segment { category: string; expenses: number; share: number; color: string; }

// "Cost breakdown" — share of operating cost (total expenses) per activity
// category, drawn as a donut with the total in the centre and a legend giving
// each category's amount and percentage. Real data from GET /reports/pnl.
export const CostBreakdown = () => {
  const [report, setReport] = useState<PnlReport | null>(null);

  useEffect(() => {
    reportsService.getPnl().then((res) => setReport(res.data)).catch((err) => console.error(err));
  }, []);

  const totalExpenses = report?.expenses ?? 0;
  const segments: Segment[] = (report?.categories ?? [])
    .filter((c) => c.expenses > 0)
    .sort((a, b) => b.expenses - a.expenses)
    .map((c, i) => ({
      category: c.category,
      expenses: c.expenses,
      share: totalExpenses > 0 ? c.expenses / totalExpenses : 0,
      color: categoryColors[i % categoryColors.length],
    }));

  return (
    <div style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, boxShadow: cardShadow, padding: '20px', display: 'flex', flexDirection: 'column' }}>
      <SectionHeader
        icon={<PieIcon size={15} color={colors.primary} />}
        title="Cost breakdown"
        subtitle={`Share of ${naira(totalExpenses)} op. cost`}
      />

      {segments.length === 0 ? (
        <p style={{ fontSize: '12px', color: colors.textMuted }}>No costs recorded yet.</p>
      ) : (
        <>
          <div style={{ position: 'relative', height: '150px', width: '100%', marginBottom: '16px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={segments}
                  dataKey="expenses"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  innerRadius={48}
                  outerRadius={70}
                  paddingAngle={2}
                  startAngle={90}
                  endAngle={-270}
                  stroke="none"
                >
                  {segments.map((s) => <Cell key={s.category} fill={s.color} />)}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            {/* Centre label overlaid on the donut hole. */}
            <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', pointerEvents: 'none' }}>
              <span style={{ fontSize: '18px', fontWeight: 700, color: colors.textStrong, letterSpacing: '-0.5px' }}>{nairaShort(totalExpenses)}</span>
              <span style={{ fontSize: '8.5px', fontWeight: 700, letterSpacing: '0.1em', color: colors.textFaint, textTransform: 'uppercase' }}>Total</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '11px' }}>
            {segments.map((s) => (
              <div key={s.category} style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
                <span style={{ width: '9px', height: '9px', borderRadius: '3px', background: s.color, flexShrink: 0 }} />
                <span style={{ fontSize: '12px', color: colors.textBody, textTransform: 'capitalize', flex: 1 }}>{s.category}</span>
                <span style={{ fontSize: '11px', color: colors.textMuted, fontVariantNumeric: 'tabular-nums', marginRight: '10px' }}>{nairaShort(s.expenses)}</span>
                <span style={{ fontSize: '12px', fontWeight: 700, color: colors.textStrong, fontVariantNumeric: 'tabular-nums', width: '34px', textAlign: 'right' }}>{Math.round(s.share * 100)}%</span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};
