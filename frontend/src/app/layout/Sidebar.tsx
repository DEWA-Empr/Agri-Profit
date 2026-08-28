import { type FC } from 'react';
import { Leaf } from 'lucide-react';
import { NavItem } from './NavItem';
import { SyncStatus } from './SyncStatus';
import { navSections, visibleSections } from '../navigation';
import { useIdentity, permissionsOf } from '../../features/auth/useIdentity';
import { colors } from '../../styles/theme';

// How a stored role is written in the profile footer. Anything unrecognised
// falls back to the raw value rather than to a flattering default — a role this
// build does not know about must not be displayed as "Farm Owner".
const ROLE_LABELS: Record<string, string> = {
  owner: 'Farm Owner',
  manager: 'Farm Manager',
  worker: 'Farm Worker',
};

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
  // Identity comes from the shared provider rather than a fetch of its own: the
  // router needs the same answer to decide where a role may go, and two fetches
  // would mean two moments at which the app disagrees with itself about the
  // same user.
  //
  // `permissionsOf` yields null until the call answers, and `visibleSections`
  // treats null as "no permissions yet" and shows only the unrestricted links —
  // so the nav never briefly offers a screen the caller cannot open.
  const identity = useIdentity();
  const permissions = permissionsOf(identity);
  const user = identity.status === 'ready' ? identity.user : null;
  const email = user?.email ?? null;

  const sections = visibleSections(navSections, permissions);

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
      {sections.map((section) => (
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

    {/* Profile — the signed-in user's real email and REAL ROLE from GET /auth/me.
        This line used to read "Farm Owner" for everyone, which was true only
        while registration was the sole way an account came into existence. It
        is not any more: an owner can add workers and managers
        (POST /auth/members), so the label is read from the account rather than
        assumed. */}
    <div style={{ padding: '18px', borderTop: '0.5px solid rgba(99, 153, 34, 0.12)', display: 'flex', alignItems: 'center', gap: '12px' }}>
      <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: colors.primaryDarkest, border: `1.5px solid ${colors.primaryDark}`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: colors.primaryLight, fontWeight: '800', fontSize: '11px', flexShrink: 0, textTransform: 'uppercase' }}>
        {email ? email[0] : '·'}
      </div>
      <div style={{ minWidth: 0 }}>
        <p style={{ color: colors.primaryLight, fontSize: '12px', fontWeight: '500', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={email ?? undefined}>
          {email ?? '—'}
        </p>
        <p style={{ color: colors.primaryDark, fontSize: '10px' }}>
          {user ? (ROLE_LABELS[user.role] ?? user.role) : '—'}
        </p>
      </div>
    </div>
  </aside>
  );
};
