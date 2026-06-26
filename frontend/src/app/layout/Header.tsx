import type { FC } from 'react';
import { Download, Plus } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { downloadPnlCsv } from '../../features/reports/downloadPnlCsv';
import { colors } from '../../styles/theme';

// The header is the single, contextual page-title bar: its title and subtitle
// reflect the active route so they are never stale (previously every page read
// "Season Overview"). Each content page therefore no longer repeats its own
// title in-body — it just renders its primary action and content. Only the
// dashboard carries the global Export / Add Record actions; the other pages
// provide their own primary action (e.g. "Log activity", "Add Equipment").
const pageMeta: Record<string, { title: string; subtitle: string }> = {
  '/': { title: 'Season Overview', subtitle: 'Profit, fields and decisions • Currency in NGN (₦)' },
  '/records': { title: 'Farm Records', subtitle: 'All logged operational activities and their financial impact.' },
  '/reports': { title: 'P&L Report', subtitle: 'Profit & loss by activity category, from the financial ledger.' },
  '/equipment': { title: 'Equipment', subtitle: 'Machinery, acquisition cost, depreciation and maintenance.' },
  '/dss': { title: 'Predictive DSS', subtitle: 'Forecast crop yield from rainfall, fertilizer and soil pH.' },
  '/investors': { title: 'Investors', subtitle: 'Stakeholder reporting for investors and lenders.' },
  '/ussd': { title: 'USSD / SMS', subtitle: 'Low-bandwidth access from any phone, without the app.' },
  '/whatsapp': { title: 'WhatsApp', subtitle: 'Conversational logging and reports via WhatsApp.' },
};

export const Header: FC = () => {
  const { pathname } = useLocation();
  const meta = pageMeta[pathname] ?? pageMeta['/'];
  const isDashboard = pathname === '/';

  return (
    <header style={{ height: '60px', background: colors.surface, borderBottom: `0.5px solid ${colors.border}`, padding: '15px 22px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
      <div>
        <h2 style={{ fontSize: '17px', fontWeight: '500', color: colors.textStrong, letterSpacing: '-0.3px' }}>{meta.title}</h2>
        <p style={{ fontSize: '11px', color: colors.textMuted, marginTop: '2px' }}>{meta.subtitle}</p>
      </div>
      {isDashboard && (
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={downloadPnlCsv} style={{ padding: '7px 14px', border: `0.5px solid ${colors.borderInput}`, borderRadius: '8px', backgroundColor: colors.surface, color: '#444', fontSize: '12px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <Download size={14} /> Export
          </button>
          <Link to="/records" style={{ padding: '7px 14px', background: colors.primaryDark, color: colors.onPrimary, borderRadius: '8px', fontSize: '12px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', border: 'none', textDecoration: 'none' }}>
            <Plus size={14} /> Add Record
          </Link>
        </div>
      )}
    </header>
  );
};
