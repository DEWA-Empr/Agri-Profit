import { lazy, Suspense, useEffect, useState } from 'react';
import type { FC } from 'react';
import { ledgerService } from '../../lib/apiClient';
import type { Summary } from '../../types/domain';
import { MetricCard } from './components/MetricCard';
import { colors } from '../../styles/theme';
import { DecisionSupport } from './components/DecisionSupport';
import { DashboardOnboarding } from './components/DashboardOnboarding';
import { NoAccess } from '../../components/NoAccess';
import { isForbidden } from '../../lib/accessError';

// The two charts are the only recharts consumers in the app (~360 kB of the
// bundle). Loading them lazily lets the KPI row and decision-support table
// paint immediately on a slow rural link, with the charts filling in after.
const PnlChart = lazy(() => import('./components/PnlChart').then((m) => ({ default: m.PnlChart })));
const CostBreakdown = lazy(() => import('./components/CostBreakdown').then((m) => ({ default: m.CostBreakdown })));

// Reserves the chart's footprint while its chunk loads so the page below it
// does not jump when the charts arrive.
const ChartPlaceholder = () => (
  <div style={{
    background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`,
    padding: '20px', minHeight: '260px', fontSize: '12px', color: colors.labelText,
  }}>
    Loading chart…
  </div>
);

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
  const [loaded, setLoaded] = useState(false);
  // Distinguished from "no data": a refused summary must not fall through to
  // the zeros below, because zeros here read as a statement about the farm.
  const [denied, setDenied] = useState(false);

  useEffect(() => {
    ledgerService.getSummary()
      .then((res) => setSummary(res.data))
      .catch((err) => {
        if (isForbidden(err)) setDenied(true);
        else console.error(err);
      })
      .finally(() => setLoaded(true));
  }, []);

  const marginPct = summary.revenue > 0 ? (summary.gross_margin / summary.revenue) * 100 : 0;

  // Checked BEFORE the empty-state branch. A refused summary is all-zero, so
  // without this a worker who reached this page would be shown the first-run
  // onboarding — told their farm has no records when in fact it has records
  // they may not see.
  //
  // In normal use the route guard redirects such a caller to /records before
  // this renders. This is the answer for the case the guard cannot cover: a
  // role changed in another tab, or finance access withdrawn mid-session.
  if (denied) {
    return <NoAccess what="the farm's financial summary" />;
  }

  // First run: nothing in the ledger yet. Show onboarding rather than a wall of
  // zeros and illustrative cards. Wait until the summary has loaded so we don't
  // flash the onboarding before real figures arrive.
  const isEmpty = summary.revenue === 0 && summary.expenses === 0 && summary.gross_margin === 0;
  if (loaded && isEmpty) {
    return <DashboardOnboarding />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      {/* KPI ROW — every tile is a figure from /ledger/summary. No YoY deltas or
          sparklines: there is no prior-year data and no per-tile history source,
          so any trend shown here would be invented. */}
      <div className="kpi-row">
        <MetricCard label="Net Profit" value={fmt(summary.gross_margin)} highlight />
        <MetricCard label="Gross Revenue" value={fmt(summary.revenue)} />
        <MetricCard label="Operating Cost" value={fmt(summary.expenses)} />
        <MetricCard label="Profit Margin" value={`${marginPct.toFixed(1)}%`} />
      </div>

      {/* TREND + COST */}
      <div className="split-row">
        <Suspense fallback={<ChartPlaceholder />}>
          <PnlChart />
        </Suspense>
        <Suspense fallback={<ChartPlaceholder />}>
          <CostBreakdown />
        </Suspense>
      </div>

      {/* DECISIONS — per-crop metrics from the real ledger. (The former "Field
          performance" table was removed: the model has no field entity.) */}
      <DecisionSupport />
    </div>
  );
};

export default DashboardPage;
