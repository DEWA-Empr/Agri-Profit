import type { FC } from 'react';
import { Leaf } from 'lucide-react';
import { NavItem } from './NavItem';
import { SyncStatus } from './SyncStatus';
import { navSections } from '../router';
import { colors } from '../../styles/theme';

// Left navigation rail: brand, season badge, nav (rendered from navSections),
// sync status, and the user profile footer.
export const Sidebar: FC<{ isOnline: boolean; pendingCount: number }> = ({ isOnline, pendingCount }) => (
  <aside style={{ width: '220px', backgroundColor: colors.sidebarBg, display: 'flex', flexDirection: 'column', flexShrink: 0, borderRight: '0.5px solid rgba(99, 153, 34, 0.15)' }}>

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

      <div style={{
        marginTop: '20px', display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 11px',
        backgroundColor: 'rgba(99, 153, 34, 0.12)', border: '0.5px solid rgba(99, 153, 34, 0.25)', borderRadius: '20px'
      }}>
        <div style={{ width: '6px', height: '6px', backgroundColor: colors.primaryLight, borderRadius: '50%', boxShadow: '0 0 0 2px rgba(151,196,89,0.25)' }} />
        <span style={{ color: colors.primaryLight, fontSize: '11px', fontWeight: '500' }}>2026 Wet Season</span>
      </div>
    </div>

    {/* Nav */}
    <nav style={{ flex: 1, marginTop: '10px', overflowY: 'auto' }} className="scroll-container">
      {navSections.map((section) => (
        <div key={section.heading}>
          <p style={{ fontSize: '9px', color: colors.sidebarHeading, fontWeight: '800', letterSpacing: '0.1em', padding: '14px 18px 5px' }}>{section.heading}</p>
          {section.items.map((item) => (
            <NavItem key={item.to} icon={item.icon} label={item.label} to={item.to} badge={item.badge} />
          ))}
        </div>
      ))}
    </nav>

    <SyncStatus isOnline={isOnline} pendingCount={pendingCount} />

    {/* Profile */}
    <div style={{ padding: '18px', borderTop: '0.5px solid rgba(99, 153, 34, 0.12)', display: 'flex', alignItems: 'center', gap: '12px' }}>
      <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: colors.primaryDarkest, border: `1.5px solid ${colors.primaryDark}`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: colors.primaryLight, fontWeight: '800', fontSize: '11px' }}>AD</div>
      <div>
        <p style={{ color: colors.primaryLight, fontSize: '12px', fontWeight: '500' }}>Abubakar D.</p>
        <p style={{ color: colors.primaryDark, fontSize: '10px' }}>Farm Owner</p>
      </div>
    </div>
  </aside>
);
