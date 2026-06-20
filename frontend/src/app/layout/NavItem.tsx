import type { FC, ReactNode } from 'react';
import { NavLink } from 'react-router-dom';
import { colors } from '../../styles/theme';

// A single sidebar navigation link with active styling and an optional badge.
export const NavItem: FC<{ icon: ReactNode; label: string; to: string; badge?: string }> = ({ icon, label, to, badge }) => (
  <NavLink
    to={to}
    className="nav-item-hover"
    style={({ isActive }) => ({
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '7px 18px',
      fontSize: '12px',
      textDecoration: 'none',
      transition: 'all 0.2s',
      position: 'relative',
      backgroundColor: isActive ? 'rgba(99, 153, 34, 0.12)' : 'transparent',
      color: isActive ? colors.primaryTint : colors.sidebarText,
      fontWeight: isActive ? '700' : '500',
      borderRadius: isActive ? '0 3px 3px 0' : '0',
      borderLeft: isActive ? `3px solid ${colors.primary}` : '3px solid transparent',
    })}
  >
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      <span style={{ display: 'flex' }}>{icon}</span>
      <span>{label}</span>
    </div>
    {badge && (
      <span style={{
        backgroundColor: 'rgba(99, 153, 34, 0.2)', color: colors.primaryLight, fontSize: '9px', fontWeight: '800',
        padding: '2px 7px', borderRadius: '10px'
      }}>{badge}</span>
    )}
  </NavLink>
);
