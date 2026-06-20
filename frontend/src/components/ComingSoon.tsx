import type { FC, ReactNode } from 'react';
import { colors } from '../styles/theme';

// Shared placeholder for modules that are scaffolded but not yet built out.
// Keeps every not-yet-implemented route consistent (replaces the old inline
// "Module Under Construction" text).
export const ComingSoon: FC<{ title: string; description: string; icon?: ReactNode }> = ({ title, description, icon }) => (
  <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
    <div style={{ textAlign: 'center', maxWidth: '380px', padding: '40px', background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}` }}>
      {icon && <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px', color: colors.primary }}>{icon}</div>}
      <h2 style={{ fontSize: '18px', fontWeight: 600, color: colors.primaryDarker }}>{title}</h2>
      <p style={{ fontSize: '12px', color: colors.textMuted, marginTop: '8px', lineHeight: 1.6 }}>{description}</p>
      <span style={{ display: 'inline-block', marginTop: '18px', fontSize: '10px', fontWeight: 700, letterSpacing: '0.08em', color: colors.warn, backgroundColor: 'rgba(160,92,0,0.1)', padding: '4px 12px', borderRadius: '12px' }}>COMING SOON</span>
    </div>
  </div>
);
