import { useEffect, useState } from 'react';
import { TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import { AreaChart, Area, XAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { reportsService } from '../../../lib/apiClient';
import type { MonthlyPnlPoint } from '../../../types/domain';
import { colors, cardShadow } from '../../../styles/theme';
import { SectionHeader } from './SectionHeader';

const naira = (n: number) => `₦${Number(n).toLocaleString()}`;

interface Point { month: string; net: number; }

// Monthly net profit (revenue − expenses) from GET /reports/pnl/monthly, drawn
// as a smooth gradient area with a dot per month and the peak called out — the
// reviewed standalone "Net profit trend" pattern (replaces the earlier bars).
export const PnlChart = () => {
  const [data, setData] = useState<Point[]>([]);

  useEffect(() => {
    reportsService.getMonthlyPnl()
      .then((res) => setData(res.data.map((p: MonthlyPnlPoint) => ({ month: p.month, net: p.revenue - p.expenses }))))
      .catch((err) => console.error(err));
  }, []);

  const peak = data.reduce<Point | null>((best, p) => (!best || p.net > best.net ? p : best), null);

  return (
    <div style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, boxShadow: cardShadow, padding: '20px' }}>
      <SectionHeader
        icon={<TrendingUp size={15} color={colors.primary} />}
        title="Net profit trend"
        subtitle="Monthly · net of costs"
        action={
          <>
            {peak && peak.net > 0 && (
              <span style={{ fontSize: '10px', fontWeight: 700, color: colors.primaryDark, background: colors.primarySurface, padding: '3px 9px', borderRadius: '6px', whiteSpace: 'nowrap' }}>
                Peak {naira(peak.net)} · {peak.month}
              </span>
            )}
            <Link to="/reports" style={{ fontSize: '11px', color: colors.primary, fontWeight: 700, textDecoration: 'none', whiteSpace: 'nowrap' }}>Full report →</Link>
          </>
        }
      />

      <div style={{ height: '200px', width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 6, right: 6, bottom: 0, left: 6 }}>
            <defs>
              <linearGradient id="netFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={colors.primary} stopOpacity={0.22} />
                <stop offset="100%" stopColor={colors.primary} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} stroke="#f2f2f2" />
            <XAxis dataKey="month" tick={{ fontSize: 10, fill: colors.textFaint }} axisLine={false} tickLine={false} />
            <Tooltip
              cursor={{ stroke: colors.primaryTint, strokeWidth: 1 }}
              formatter={(value) => [naira(Number(value)), 'Net profit']}
              contentStyle={{ fontSize: '11px', borderRadius: '8px', border: `0.5px solid ${colors.border}`, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}
            />
            <Area
              type="monotone"
              dataKey="net"
              stroke={colors.primary}
              strokeWidth={2.5}
              fill="url(#netFill)"
              dot={{ r: 3, fill: colors.surface, stroke: colors.primary, strokeWidth: 2 }}
              activeDot={{ r: 5, fill: colors.primaryDark, stroke: colors.surface, strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
