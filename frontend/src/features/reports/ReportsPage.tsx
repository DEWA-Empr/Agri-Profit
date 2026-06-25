import { useEffect, useState, type CSSProperties } from 'react';
import { Download, TrendingUp, TrendingDown, Wallet } from 'lucide-react';
import { reportsService } from '../../lib/apiClient';
import type { PnlReport } from '../../types/domain';
import { downloadPnlCsv } from './downloadPnlCsv';
import { colors } from '../../styles/theme';

const ReportsPage = () => {
  const [report, setReport] = useState<PnlReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reportsService.getPnl()
      .then((res) => setReport(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const th: CSSProperties = { textAlign: 'left', fontSize: '10px', fontWeight: 700, letterSpacing: '0.05em', color: colors.textMuted, textTransform: 'uppercase', padding: '10px 12px', borderBottom: `0.5px solid ${colors.border}` };
  const thRight: CSSProperties = { ...th, textAlign: 'right' };
  const td: CSSProperties = { fontSize: '12px', color: colors.textBody, padding: '11px 12px', borderBottom: `0.5px solid ${colors.dividerLight}` };
  const tdRight: CSSProperties = { ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums' };

  const naira = (n: number) => `₦${n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const summaryCard = (label: string, value: number, icon: React.ReactNode, color: string) => (
    <div style={{ flex: 1, background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, padding: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color }}>{icon}<span style={{ fontSize: '11px', color: colors.textMuted, fontWeight: 600 }}>{label}</span></div>
      <p style={{ fontSize: '22px', fontWeight: 500, color, marginTop: '10px', letterSpacing: '-0.5px' }}>{naira(value)}</p>
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
        <button
          onClick={downloadPnlCsv}
          style={{ display: 'flex', alignItems: 'center', gap: '8px', background: colors.primaryDark, color: colors.onPrimary, padding: '8px 14px', borderRadius: '8px', border: 'none', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
        >
          <Download size={16} /> Export CSV
        </button>
      </div>

      {loading ? (
        <p style={{ fontSize: '12px', color: colors.textMuted }}>Loading report…</p>
      ) : !report ? (
        <p style={{ fontSize: '12px', color: colors.danger }}>Could not load the report.</p>
      ) : (
        <>
          <div style={{ display: 'flex', gap: '12px' }}>
            {summaryCard('Total Revenue', report.revenue, <TrendingUp size={16} />, colors.primaryDark)}
            {summaryCard('Total Expenses', report.expenses, <TrendingDown size={16} />, colors.dangerAlt)}
            {summaryCard('Gross Margin', report.gross_margin, <Wallet size={16} />, report.gross_margin >= 0 ? colors.info : colors.dangerAlt)}
          </div>

          <div style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={th}>Category</th>
                  <th style={thRight}>Revenue</th>
                  <th style={thRight}>Expenses</th>
                  <th style={thRight}>Net</th>
                </tr>
              </thead>
              <tbody>
                {report.categories.map((c) => (
                  <tr key={c.category}>
                    <td style={{ ...td, fontWeight: 600, textTransform: 'capitalize' }}>{c.category}</td>
                    <td style={tdRight}>{naira(c.revenue)}</td>
                    <td style={tdRight}>{naira(c.expenses)}</td>
                    <td style={{ ...tdRight, fontWeight: 600, color: c.net >= 0 ? colors.primaryDark : colors.danger }}>{naira(c.net)}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr>
                  <td style={{ ...td, fontWeight: 700, borderTop: `1px solid ${colors.border}` }}>Total</td>
                  <td style={{ ...tdRight, fontWeight: 700, borderTop: `1px solid ${colors.border}` }}>{naira(report.revenue)}</td>
                  <td style={{ ...tdRight, fontWeight: 700, borderTop: `1px solid ${colors.border}` }}>{naira(report.expenses)}</td>
                  <td style={{ ...tdRight, fontWeight: 700, borderTop: `1px solid ${colors.border}`, color: report.gross_margin >= 0 ? colors.primaryDark : colors.danger }}>{naira(report.gross_margin)}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default ReportsPage;
