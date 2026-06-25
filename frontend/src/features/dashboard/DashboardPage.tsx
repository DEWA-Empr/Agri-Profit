import { useEffect, useState } from 'react';
import type { FC } from 'react';
import { ledgerService } from '../../lib/apiClient';
import type { Summary } from '../../types/domain';
import { MetricCard } from './components/MetricCard';
import { PnlChart } from './components/PnlChart';
import { CostBreakdown } from './components/CostBreakdown';
import { FieldPerformance } from './components/FieldPerformance';
import { DecisionSupport } from './components/DecisionSupport';

// Abbreviate large Naira figures the way the #04 mockup does (₦42.85M),
// falling back to full numbers for small values.
const fmt = (n: number): string => {
  const abs = Math.abs(n);
  if (abs >= 1_000_000) return `₦${(n / 1_000_000).toFixed(2)}M`;
  if (abs >= 1_000) return `₦${(n / 1_000).toFixed(1)}K`;
  return `₦${n.toLocaleString()}`;
};

// The DashboardPage still receives isOnline/pendingCount from the router; they
// are no longer used here (quick-logging moved to the Farm Records form).
const DashboardPage: FC<{ isOnline: boolean; pendingCount: number }> = () => {
  const [summary, setSummary] = useState<Summary>({ revenue: 0, expenses: 0, gross_margin: 0 });

  useEffect(() => {
    ledgerService.getSummary().then((res) => setSummary(res.data)).catch((err) => console.error(err));
  }, []);

  const marginPct = summary.revenue > 0 ? (summary.gross_margin / summary.revenue) * 100 : 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      {/* KPI ROW — first four are real (from /ledger/summary); avg yield is illustrative. */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '11px' }}>
        <MetricCard label="Net Profit" value={fmt(summary.gross_margin)} delta="↑ 12.4% YoY" deltaTone={summary.gross_margin >= 0 ? 'up' : 'down'} spark={[8, 11, 10, 14, 17, 22]} highlight />
        <MetricCard label="Gross Revenue" value={fmt(summary.revenue)} delta="↑ 8.1% YoY" deltaTone="up" spark={[30, 34, 33, 40, 44, 48]} />
        <MetricCard label="Operating Cost" value={fmt(summary.expenses)} delta="↑ 5.6% YoY" deltaTone="down" spark={[18, 20, 19, 24, 26, 28]} />
        <MetricCard label="Profit Margin" value={`${marginPct.toFixed(1)}%`} delta="↑ 2.0 pts" deltaTone="up" spark={[38, 40, 39, 41, 42, 43]} />
        <MetricCard label="Avg Yield" value="168 bu/ac" delta="↑ 4.3% YoY" deltaTone="up" spark={[150, 156, 154, 160, 164, 168]} />
      </div>

      {/* TREND + COST */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: '18px', alignItems: 'start' }}>
        <PnlChart />
        <CostBreakdown />
      </div>

      {/* FIELDS + DECISIONS */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: '18px', alignItems: 'start' }}>
        <FieldPerformance />
        <DecisionSupport />
      </div>
    </div>
  );
};

export default DashboardPage;
