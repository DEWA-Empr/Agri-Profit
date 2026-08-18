import { useEffect, useState, type FC } from 'react';
import { Leaf } from 'lucide-react';
import { NavItem } from './NavItem';
import { SyncStatus } from './SyncStatus';
import { navSections } from '../navigation';
import { authService } from '../../lib/apiClient';
import { colors } from '../../styles/theme';

// Left navigation rail: brand, nav (rendered from navSections), sync status,
// and the user profile footer.
//
// Most nav badges are static (declared in navSections); the Farm Records badge
// is live — it reflects the real record count so it can never contradict the
// "no records yet" empty state. A null count (not yet loaded) or zero hides it.
export const Sidebar: FC<{
  isOnline: boolean;
  pendingCount: number;
  recordCount: number | null;
  /** Called when a nav link is activated, so the mobile drawer can close. */
  onNavigate?: () => void;
}> = ({ isOnline, pendingCount, recordCount, onNavigate }) => {
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    authService.me()
      .then((res) => setEmail(res.data.email))
      .catch(() => setEmail(null));
  }, []);

  return (
  <aside style={{ width: '220px', maxWidth: '100%', height: '100%', backgroundColor: colors.sidebarBg, display: 'flex', flexDirection: 'column', flexShrink: 0, borderRight: '0.5px solid rgba(99, 153, 34, 0.15)' }}>

    {/* Logo Area */}
    <div style={{ padding: '22px 24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ width: '38px', height: '38px', backgroundColor: colors.primary, borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: colors.surface }}>
          <Leaf size={20} />
        </div>
        <div>
          <h1 style={{ color: colors.onPrimary, fontSize: '15px', fontWeight: '500', lineHeight: 1.1 }}>AgriProfit</h1>
          <p style={{ color: colors.primaryDark, fontSize: '9px', fontWeight: '500', letterSpacing: '0.12em', textTransform: 'uppercase', marginTop: '2px' }}>Farm Management</p>
        </div>
      </div>
    </div>

    {/* Nav */}
    <nav style={{ flex: 1, marginTop: '10px', overflowY: 'auto' }} className="scroll-container">
      {navSections.map((section) => (
        <div key={section.heading}>
          <p style={{ fontSize: '9px', color: colors.sidebarHeading, fontWeight: '800', letterSpacing: '0.1em', padding: '14px 18px 5px' }}>{section.heading}</p>
          {section.items.map((item) => {
            // Farm Records carries the live record count; others use their
            // static badge (if any).
            const badge = item.to === '/records'
              ? (recordCount ? String(recordCount) : undefined)
              : item.badge;
            return <NavItem key={item.to} icon={item.icon} label={item.label} to={item.to} badge={badge} onNavigate={onNavigate} />;
          })}
        </div>
      ))}
    </nav>

    <SyncStatus isOnline={isOnline} pendingCount={pendingCount} />

    {/* Profile — the signed-in user's real email from GET /auth/me. "Farm Owner"
        is accurate rather than decorative: registration is the only path that
        creates a user and it mints that user a farm of their own
        (auth_service.register), so there is no non-owner member today. */}
    <div style={{ padding: '18px', borderTop: '0.5px solid rgba(99, 153, 34, 0.12)', display: 'flex', alignItems: 'center', gap: '12px' }}>
      <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: colors.primaryDarkest, border: `1.5px solid ${colors.primaryDark}`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: colors.primaryLight, fontWeight: '800', fontSize: '11px', flexShrink: 0, textTransform: 'uppercase' }}>
        {email ? email[0] : '·'}
      </div>
      <div style={{ minWidth: 0 }}>
        <p style={{ color: colors.primaryLight, fontSize: '12px', fontWeight: '500', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={email ?? undefined}>
          {email ?? '—'}
        </p>
        <p style={{ color: colors.primaryDark, fontSize: '10px' }}>Farm Owner</p>
      </div>
    </div>
  </aside>
  );
};
