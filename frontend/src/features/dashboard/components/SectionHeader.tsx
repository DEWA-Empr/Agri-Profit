import type { FC, ReactNode } from 'react';
import { colors } from '../../../styles/theme';

interface SectionHeaderProps {
  icon: ReactNode;
  title: string;
  subtitle?: string;
  /** Right-aligned slot — a "View all →" link, a peak tag, etc. */
  action?: ReactNode;
}

// Shared card heading for the dashboard sections: an icon sitting in a soft
// green chip, the title, an optional subtitle, and an optional right-side
// action. Matches the reviewed standalone mockup so every panel reads the same.
export const SectionHeader: FC<SectionHeaderProps> = ({ icon, title, subtitle, action }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px', gap: '12px' }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
      <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '28px', height: '28px', borderRadius: '8px', background: colors.primarySurface, flexShrink: 0 }}>
        {icon}
      </span>
      <div style={{ minWidth: 0 }}>
        <h3 style={{ fontSize: '12px', fontWeight: 700, color: colors.textStrong, lineHeight: 1.2 }}>{title}</h3>
        {subtitle && <p style={{ fontSize: '10px', color: colors.textMuted, marginTop: '2px' }}>{subtitle}</p>}
      </div>
    </div>
    {action && <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexShrink: 0 }}>{action}</div>}
  </div>
);
