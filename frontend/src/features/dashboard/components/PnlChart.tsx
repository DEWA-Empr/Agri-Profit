import { useEffect, useState } from 'react';
import { BarChart3 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { BarChart, Bar, XAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { reportsService } from '../../../lib/apiClient';
import type { MonthlyPnlPoint } from '../../../types/domain';
import { colors } from '../../../styles/theme';

const naira = (n: number) => `₦${Number(n).toLocaleString()}`;

// Monthly revenue vs. expenses, from GET /reports/pnl/monthly (real ledger data).
export const PnlChart = () => {
  const [data, setData] = useState<MonthlyPnlPoint[]>([]);

  useEffect(() => {
    reportsService.getMonthlyPnl()
      .then((res) => setData(res.data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <div style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BarChart3 size={18} color={colors.primary} />
          <h3 style={{ fontSize: '12px', fontWeight: '600' }}>Monthly P&L overview</h3>
        </div>
        <Link to="/reports" style={{ fontSize: '11px', color: colors.primary, fontWeight: '700', textDecoration: 'none' }}>See full report →</Link>
      </div>

      <div style={{ height: '180px', width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} barGap={2} barCategoryGap="28%" margin={{ top: 6, right: 4, bottom: 0, left: 4 }}>
            <CartesianGrid vertical={false} stroke="#f2f2f2" />
            <XAxis dataKey="month" tick={{ fontSize: 10, fill: colors.textFaint }} axisLine={false} tickLine={false} />
            <Tooltip
              cursor={{ fill: 'rgba(99,153,34,0.06)' }}
              formatter={(value) => naira(Number(value))}
              contentStyle={{ fontSize: '11px', borderRadius: '8px', border: `0.5px solid ${colors.border}`, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}
            />
            <Bar dataKey="revenue" name="Revenue" fill={colors.primary} radius={[2, 2, 0, 0]} maxBarSize={14} />
            <Bar dataKey="expenses" name="Expenses" fill={colors.primaryTint} radius={[2, 2, 0, 0]} maxBarSize={14} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', marginTop: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '10px', color: colors.textMuted }}><div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: colors.primary }} /> Revenue</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '10px', color: colors.textMuted }}><div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: colors.primaryTint }} /> Expenses</div>
      </div>
    </div>
  );
};
