import { useEffect, useState, type CSSProperties } from 'react';
import { FileText, Download, TrendingUp, TrendingDown, Wallet } from 'lucide-react';
import { reportsService } from '../../lib/apiClient';
import type { PnlReport } from '../../types/domain';
import { downloadPnlCsv } from './downloadPnlCsv';

const ReportsPage = () => {
  const [report, setReport] = useState<PnlReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reportsService.getPnl()
      .then((res) => setReport(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const th: CSSProperties = { textAlign: 'left', fontSize: '10px', fontWeight: 700, letterSpacing: '0.05em', color: '#888', textTransform: 'uppercase', padding: '10px 12px', borderBottom: '0.5px solid #e8ede4' };
  const thRight: CSSProperties = { ...th, textAlign: 'right' };
  const td: CSSProperties = { fontSize: '12px', color: '#333', padding: '11px 12px', borderBottom: '0.5px solid #f5f5f5' };
  const tdRight: CSSProperties = { ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums' };

  const naira = (n: number) => `₦${n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const summaryCard = (label: string, value: number, icon: React.ReactNode, color: string) => (
    <div style={{ flex: 1, background: '#fff', borderRadius: '12px', border: '0.5px solid #e8ede4', padding: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color }}>{icon}<span style={{ fontSize: '11px', color: '#888', fontWeight: 600 }}>{label}</span></div>
      <p style={{ fontSize: '22px', fontWeight: 500, color, marginTop: '10px', letterSpacing: '-0.5px' }}>{naira(value)}</p>
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <FileText size={20} color="#639922" />
          <div>
            <h2 style={{ fontSize: '17px', fontWeight: 600, color: '#111' }}>P&L Report</h2>
            <p style={{ fontSize: '11px', color: '#888', marginTop: '2px' }}>Profit &amp; loss by activity category, from the financial ledger.</p>
          </div>
        </div>
        <button
          onClick={downloadPnlCsv}
          style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#3B6D11', color: '#EAF3DE', padding: '8px 14px', borderRadius: '8px', border: 'none', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
        >
          <Download size={16} /> Export CSV
        </button>
      </div>

      {loading ? (
        <p style={{ fontSize: '12px', color: '#888' }}>Loading report…</p>
      ) : !report ? (
        <p style={{ fontSize: '12px', color: '#c0392b' }}>Could not load the report.</p>
      ) : (
        <>
          <div style={{ display: 'flex', gap: '12px' }}>
            {summaryCard('Total Revenue', report.revenue, <TrendingUp size={16} />, '#3B6D11')}
            {summaryCard('Total Expenses', report.expenses, <TrendingDown size={16} />, '#b33333')}
            {summaryCard('Gross Margin', report.gross_margin, <Wallet size={16} />, report.gross_margin >= 0 ? '#185FA5' : '#b33333')}
          </div>

          <div style={{ background: '#fff', borderRadius: '12px', border: '0.5px solid #e8ede4', overflow: 'hidden' }}>
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
                    <td style={{ ...tdRight, fontWeight: 600, color: c.net >= 0 ? '#3B6D11' : '#c0392b' }}>{naira(c.net)}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr>
                  <td style={{ ...td, fontWeight: 700, borderTop: '1px solid #e8ede4' }}>Total</td>
                  <td style={{ ...tdRight, fontWeight: 700, borderTop: '1px solid #e8ede4' }}>{naira(report.revenue)}</td>
                  <td style={{ ...tdRight, fontWeight: 700, borderTop: '1px solid #e8ede4' }}>{naira(report.expenses)}</td>
                  <td style={{ ...tdRight, fontWeight: 700, borderTop: '1px solid #e8ede4', color: report.gross_margin >= 0 ? '#3B6D11' : '#c0392b' }}>{naira(report.gross_margin)}</td>
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
