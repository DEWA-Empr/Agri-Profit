import { useEffect, useState, type CSSProperties } from 'react';
import { TrendingUp, TrendingDown, Wallet, ShieldCheck, Sprout } from 'lucide-react';
import { shareService } from '../../lib/apiClient';
import type { InvestorReport, DssCropMetrics } from '../../types/domain';
import { colors } from '../../styles/theme';

// The page an investor/lender opens from a shared link — public, read-only, no
// login. The token in the URL is the only credential; a revoked or invalid
// token comes back as 404 and we show a neutral "link no longer active" notice.
const naira = (n: number) => `₦${n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

// Yield as reported to a lender. Quantities in different units are listed
// separately, one per line — they are never added together, because a total
// across kg and bags is not a quantity anyone can verify.
const formatYield = (c: DssCropMetrics) => {
  const byUnit = c.yield_by_unit ?? [];
  if (byUnit.length === 0) return '—';
  return byUnit.map((y) => (
    <div key={y.unit ?? 'no-unit'}>
      {y.quantity.toLocaleString()}{y.unit ? ` ${y.unit}` : ''}
    </div>
  ));
};

// Marketable Mass: what actually left the dryer, and therefore the denominator
// of the cost-per-kg-marketable column standing immediately to its right. It is
// shown as a quantity in its own cell so a lender can read the division across
// the row instead of having to work backwards from the rate. Null — an em dash
// — wherever the crop has no recorded drying run.
const formatMarketableMass = (c: DssCropMetrics) =>
  c.marketable_mass_kg != null
    ? `${c.marketable_mass_kg.toLocaleString(undefined, { maximumFractionDigits: 2 })} kg`
    : '—';

const PublicInvestorReport = ({ token }: { token: string }) => {
  const [report, setReport] = useState<InvestorReport | null>(null);
  const [state, setState] = useState<'loading' | 'ok' | 'invalid'>('loading');

  useEffect(() => {
    shareService.getReport(token)
      .then((res) => { setReport(res.data); setState('ok'); })
      .catch(() => setState('invalid'));
  }, [token]);

  const th: CSSProperties = { textAlign: 'left', fontSize: '10px', fontWeight: 700, letterSpacing: '0.05em', color: colors.textMuted, textTransform: 'uppercase', padding: '10px 12px', borderBottom: `0.5px solid ${colors.border}` };
  const thRight: CSSProperties = { ...th, textAlign: 'right' };
  const td: CSSProperties = { fontSize: '12px', color: colors.textBody, padding: '11px 12px', borderBottom: `0.5px solid ${colors.dividerLight}` };
  const tdRight: CSSProperties = { ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums' };
  const card: CSSProperties = { background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, overflow: 'hidden' };

  const summaryCard = (labelText: string, value: number, icon: React.ReactNode, color: string) => (
    <div style={{ flex: 1, minWidth: '160px', background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, padding: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color }}>{icon}<span style={{ fontSize: '11px', color: colors.textMuted, fontWeight: 600 }}>{labelText}</span></div>
      <p style={{ fontSize: '22px', fontWeight: 500, color, marginTop: '10px', letterSpacing: '-0.5px' }}>{naira(value)}</p>
    </div>
  );

  return (
    // This page renders outside the AppShell, and index.css sets
    // `body { overflow: hidden }`, so the body never scrolls. We therefore make
    // this root its own scroll container: a full-viewport-height box with
    // overflow-y: auto, so long reports scroll at 100% zoom on desktop and
    // mobile. (100dvh tracks the *dynamic* viewport so mobile browser chrome
    // doesn't hide the bottom; height:100vh is the fallback for older engines.)
    <div
      className="scroll-container"
      style={{ height: '100vh', maxHeight: '100dvh', width: '100%', overflowY: 'auto', WebkitOverflowScrolling: 'touch', background: colors.appBg, padding: '28px 20px' }}
    >
      <div style={{ maxWidth: '860px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '18px' }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <h1 style={{ fontSize: '20px', fontWeight: 600, color: colors.primaryDark, letterSpacing: '-0.4px' }}>AgriProfit</h1>
            <p style={{ fontSize: '12px', color: colors.textMuted, marginTop: '2px' }}>Shared performance report</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: colors.textMuted, background: colors.surface, border: `0.5px solid ${colors.border}`, borderRadius: '8px', padding: '6px 10px' }}>
            <ShieldCheck size={13} color={colors.primaryDark} /> Read-only
          </div>
        </div>

        {state === 'loading' && <p style={{ fontSize: '12px', color: colors.textMuted }}>Loading report…</p>}

        {state === 'invalid' && (
          <div style={{ ...card, padding: '28px', textAlign: 'center' }}>
            <p style={{ fontSize: '14px', fontWeight: 600, color: colors.text }}>This link is no longer active</p>
            <p style={{ fontSize: '12px', color: colors.textMuted, marginTop: '6px' }}>
              The share link is invalid or has been revoked by the farm owner. Please ask them for a new link.
            </p>
          </div>
        )}

        {state === 'ok' && report && (
          <>
            <div style={{ ...card, padding: '16px 18px' }}>
              <p style={{ fontSize: '11px', color: colors.textMuted, fontWeight: 600 }}>FARM</p>
              <p style={{ fontSize: '18px', fontWeight: 600, color: colors.text, marginTop: '2px' }}>{report.farm_name}</p>
              <p style={{ fontSize: '11px', color: colors.textFaint, marginTop: '6px' }}>
                Generated {new Date(report.generated_at).toLocaleString()} · Currency in NGN (₦)
              </p>
            </div>

            {/* P&L summary */}
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              {summaryCard('Total Revenue', report.pnl.revenue, <TrendingUp size={16} />, colors.primaryDark)}
              {summaryCard('Total Expenses', report.pnl.expenses, <TrendingDown size={16} />, colors.dangerAlt)}
              {summaryCard('Gross Margin', report.pnl.gross_margin, <Wallet size={16} />, report.pnl.gross_margin >= 0 ? colors.info : colors.dangerAlt)}
            </div>

            {/* P&L by category */}
            <div style={card}>
              <div style={{ padding: '14px 16px', borderBottom: `0.5px solid ${colors.border}`, fontSize: '12px', fontWeight: 700, color: colors.text }}>Profit &amp; Loss by category</div>
              <div className="table-scroll"><table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr><th style={th}>Category</th><th style={thRight}>Revenue</th><th style={thRight}>Expenses</th><th style={thRight}>Net</th></tr>
                </thead>
                <tbody>
                  {report.pnl.categories.map((c) => (
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
                    <td style={{ ...tdRight, fontWeight: 700, borderTop: `1px solid ${colors.border}` }}>{naira(report.pnl.revenue)}</td>
                    <td style={{ ...tdRight, fontWeight: 700, borderTop: `1px solid ${colors.border}` }}>{naira(report.pnl.expenses)}</td>
                    <td style={{ ...tdRight, fontWeight: 700, borderTop: `1px solid ${colors.border}`, color: report.pnl.gross_margin >= 0 ? colors.primaryDark : colors.danger }}>{naira(report.pnl.gross_margin)}</td>
                  </tr>
                </tfoot>
              </table></div>
            </div>

            {/* Yield by crop */}
            <div style={card}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '14px 16px', borderBottom: `0.5px solid ${colors.border}`, fontSize: '12px', fontWeight: 700, color: colors.text }}>
                <Sprout size={15} color={colors.primaryDark} /> Yield by crop
              </div>
              {report.crops.length === 0 ? (
                <p style={{ fontSize: '12px', color: colors.textMuted, padding: '16px' }}>No crop yield recorded yet.</p>
              ) : (
                <div className="table-scroll"><table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    {/* Column order is mass, then the cost that divides by it,
                        then the second mass and the cost that divides by THAT.
                        The two masses are not interchangeable — harvested is
                        what came off the field, marketable is what survived the
                        dryer — and the two unit costs differ by exactly the
                        difference between them. Putting each denominator
                        immediately left of its rate lets a lender read the
                        division straight across the row rather than inferring
                        it, or worse, multiplying a per-kg-marketable rate by a
                        harvested mass. */}
                    <tr><th style={th}>Crop</th><th style={thRight}>Yield<br />as harvested</th><th style={thRight}>Unit cost<br />per harvested unit</th><th style={thRight}>Marketable mass<br />out of the dryer</th><th style={thRight}>Unit cost<br />per kg marketable</th><th style={thRight}>Gross margin</th></tr>
                  </thead>
                  <tbody>
                    {report.crops.map((c) => (
                      <tr key={c.crop}>
                        <td style={{ ...td, fontWeight: 600, textTransform: 'capitalize' }}>{c.crop}</td>
                        {/* Each unit on its own line. This is the figure a
                            lender reads, so mixed units are shown as the
                            separate quantities they are, never added up. */}
                        <td style={tdRight}>{formatYield(c)}</td>
                        <td style={tdRight}>{c.unit_cost_of_production != null ? naira(c.unit_cost_of_production) : '—'}</td>
                        {/* The marketable pair. Both cells are em dashes for a
                            crop sold fresh — no drying run means no marketable
                            mass and no rate to divide by it, and the row reads
                            exactly as it did before this column existed. The
                            mass is shown even in the rare case where the rate
                            is null (zero marketable mass, guarded backend-side)
                            because a recorded 0 kg out of the dryer is itself
                            worth seeing. */}
                        <td style={tdRight}>{formatMarketableMass(c)}</td>
                        <td style={tdRight}>
                          {c.marketable_mass_kg != null && c.unit_cost_per_kg_marketable != null
                            ? naira(c.unit_cost_per_kg_marketable)
                            : '—'}
                        </td>
                        <td style={{ ...tdRight, fontWeight: 600, color: c.gross_margin >= 0 ? colors.primaryDark : colors.danger }}>{naira(c.gross_margin)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table></div>
              )}
              {/* The assumption behind the marketable figure, stated wherever
                  the figure appears. It divides a crop's TOTAL expenses by the
                  marketable mass of its dried lots, so where only part of a
                  harvest was dried it overstates unit cost (docs/adr/0001,
                  "Known boundary"). The farm owner knows which of their
                  harvests went through the dryer; a third party reading this
                  link cannot tell, and cannot detect the overstatement from
                  the numbers on the page. So it is said out loud. */}
              {report.crops.some((c) => c.marketable_mass_kg != null && c.unit_cost_per_kg_marketable != null) && (
                <p style={{ fontSize: '10px', color: colors.textMuted, padding: '12px 16px', borderTop: `0.5px solid ${colors.dividerLight}`, lineHeight: 1.6 }}>
                  Cost per kg marketable divides the crop’s total recorded cost by the marketable mass
                  shown in the column beside it. It assumes the whole harvest was dried. Where only part
                  of a harvest went through the dryer, this figure overstates the true unit cost.
                </p>
              )}
            </div>

            <p style={{ fontSize: '10px', color: colors.textFaint, textAlign: 'center', marginTop: '4px' }}>
              Shared via AgriProfit · This is a read-only view. Figures are drawn from the farm’s own records.
            </p>
          </>
        )}
      </div>
    </div>
  );
};

export default PublicInvestorReport;
