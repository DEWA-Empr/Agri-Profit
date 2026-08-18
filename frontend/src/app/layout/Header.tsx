import type { FC } from 'react';
import { Download, Plus, LogOut, Menu } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { downloadPnlCsv } from '../../features/reports/downloadPnlCsv';
import { useAuth } from '../../features/auth/useAuth';
import { colors } from '../../styles/theme';

// The header is the single, contextual page-title bar: its title and subtitle
// reflect the active route so they are never stale (previously every page read
// "Season Overview"). Each content page therefore no longer repeats its own
// title in-body — it just renders its primary action and content. Only the
// dashboard carries the global Export / Add Record actions; the other pages
// provide their own primary action (e.g. "Log activity", "Add Equipment").
const pageMeta: Record<string, { title: string; subtitle: string }> = {
  // "Farm Overview", not "Season Overview": there is no season entity in the
  // model, so the figures below are all-time, not per-season.
  '/': { title: 'Farm Overview', subtitle: 'Profit, costs and decisions • Currency in NGN (₦)' },
  '/records': { title: 'Farm Records', subtitle: 'All logged operational activities and their financial impact.' },
  '/reports': { title: 'P&L Report', subtitle: 'Profit & loss by activity category, from the financial ledger.' },
  '/equipment': { title: 'Equipment', subtitle: 'Machinery, acquisition cost, depreciation and maintenance.' },
  '/dss': { title: 'Predictive DSS', subtitle: 'Forecast crop yield from rainfall, fertilizer and soil pH.' },
  '/investors': { title: 'Investors', subtitle: 'Stakeholder reporting for investors and lenders.' },
};

export const Header: FC<{ isMobile?: boolean; onOpenNav?: () => void }> = ({ isMobile = false, onOpenNav }) => {
  const { pathname } = useLocation();
  const { logout } = useAuth();
  const meta = pageMeta[pathname] ?? pageMeta['/'];
  const isDashboard = pathname === '/';

  // On a narrow screen the three actions keep their icons but drop their
  // labels, so all of them stay on the bar and reachable instead of the last
  // one being pushed off the edge. Each keeps an aria-label and title.
  const actionBase = {
    padding: isMobile ? '8px' : '7px 14px',
    borderRadius: '8px',
    fontSize: '12px',
    fontWeight: 500,
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    cursor: 'pointer',
    flexShrink: 0,
  } as const;

  return (
    <header style={{
      minHeight: '60px',
      background: colors.surface,
      borderBottom: `0.5px solid ${colors.border}`,
      padding: isMobile ? '10px 12px' : '15px 22px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '10px',
      flexShrink: 0,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
        {isMobile && (
          <button
            onClick={onOpenNav}
            aria-label="Open navigation"
            title="Menu"
            style={{ ...actionBase, background: 'transparent', border: `0.5px solid ${colors.borderInput}`, color: colors.textBody }}
          >
            <Menu size={18} />
          </button>
        )}
        <div style={{ minWidth: 0 }}>
          <h2 style={{
            fontSize: isMobile ? '15px' : '17px',
            fontWeight: 500,
            color: colors.textStrong,
            letterSpacing: '-0.3px',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}>{meta.title}</h2>
          {/* The subtitle is the first thing to go: at 360px it would wrap to
              three lines and push the content down for no added meaning. */}
          {!isMobile && (
            <p style={{ fontSize: '11px', color: colors.textMuted, marginTop: '2px' }}>{meta.subtitle}</p>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', gap: isMobile ? '6px' : '10px', alignItems: 'center', flexShrink: 0 }}>
        {isDashboard && (
          <>
            <button
              onClick={downloadPnlCsv}
              aria-label="Export P&L as CSV"
              title="Export"
              style={{ ...actionBase, border: `0.5px solid ${colors.borderInput}`, backgroundColor: colors.surface, color: '#444' }}
            >
              <Download size={14} /> {!isMobile && 'Export'}
            </button>
            <Link
              to="/records"
              aria-label="Add a record"
              title="Add Record"
              style={{ ...actionBase, background: colors.primaryDark, color: colors.onPrimary, border: 'none', textDecoration: 'none' }}
            >
              <Plus size={14} /> {!isMobile && 'Add Record'}
            </Link>
          </>
        )}
        <button
          onClick={logout}
          aria-label="Sign out"
          title="Sign out"
          style={{ ...actionBase, border: `0.5px solid ${colors.borderInput}`, backgroundColor: colors.surface, color: colors.textMuted }}
        >
          <LogOut size={14} /> {!isMobile && 'Sign out'}
        </button>
      </div>
    </header>
  );
};
