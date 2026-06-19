import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Wallet, ClipboardList } from 'lucide-react';
import { ledgerService } from '../../lib/apiClient';
import type { Summary, OperationalLog } from '../../types/domain';
import { MetricCard } from './components/MetricCard';
import { PnlChart } from './components/PnlChart';
import { RecentActivities } from './components/RecentActivities';
import { HealthScore } from './components/HealthScore';
import { QuickLogForm } from './components/QuickLogForm';

const DashboardPage: React.FC<{ isOnline: boolean; pendingCount: number }> = ({ isOnline, pendingCount }) => {
  const [summary, setSummary] = useState<Summary>({ revenue: 0, expenses: 0, gross_margin: 0 });
  const [logs, setLogs] = useState<OperationalLog[]>([]);

  const fetchData = async () => {
    try {
      const [sRes, lRes] = await Promise.all([
        ledgerService.getSummary(),
        ledgerService.getLogs(),
      ]);
      setSummary(sRes.data);
      setLogs(lRes.data);
    } catch (err) { console.error(err); }
  };

  useEffect(() => { fetchData(); }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>

      {/* METRIC GRID */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '11px' }}>
        <MetricCard
          label="Total Revenue" value={`₦${summary.revenue.toLocaleString()}`}
          trend="↑ 12%" icon={<TrendingUp />}
          iconBg="#dff0c4" iconColor="#3B6D11" trendBg="#e8f5d4" trendColor="#3B6D11" isRevenue
        />
        <MetricCard
          label="Total Expenses" value={`₦${summary.expenses.toLocaleString()}`}
          trend="↑ 4%" icon={<TrendingDown />}
          iconBg="#fde8e8" iconColor="#b33333" trendBg="#fde8e8" trendColor="#b33333"
        />
        <MetricCard
          label="Gross Margin" value={`₦${summary.gross_margin.toLocaleString()}`}
          trend="50% rate" icon={<Wallet />}
          iconBg="#ddeeff" iconColor="#185FA5" trendBg="#e8f5d4" trendColor="#3B6D11"
        />
        <MetricCard
          label="Total Activities" value={logs.length > 0 ? logs.length.toString() : '24'}
          trend="+6 this wk" icon={<ClipboardList />}
          iconBg="#fef3d8" iconColor="#a05c00" trendBg="#fff3e0" trendColor="#a05c00"
        />
      </div>

      <div style={{ display: 'flex', gap: '22px' }}>
        {/* LEFT COLUMN */}
        <div style={{ flex: 1.2, display: 'flex', flexDirection: 'column', gap: '22px' }}>
          <PnlChart />
          <RecentActivities logs={logs} />
        </div>

        {/* RIGHT COLUMN */}
        <div style={{ flex: 0.8, display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <HealthScore />
          <QuickLogForm isOnline={isOnline} pendingCount={pendingCount} onSaved={fetchData} />
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
