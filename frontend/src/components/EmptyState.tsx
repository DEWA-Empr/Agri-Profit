import type { CSSProperties, ReactNode } from 'react';
import { colors, cardShadow } from '../styles/theme';

// A shared first-run / no-data placeholder. Used wherever a list or view can be
// legitimately empty (no records yet, nothing to report) so the user sees a
// warm, instructive panel instead of a bare "nothing here" line. Keep it
// content-agnostic: callers pass the icon, copy and any call-to-action.
interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
  /** Render inside a bordered card (default) or bare, when the parent already
   *  provides the surface. */
  bare?: boolean;
}

export const EmptyState = ({ icon, title, description, action, bare = false }: EmptyStateProps) => {
  const wrap: CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    textAlign: 'center',
    padding: '48px 24px',
    gap: '6px',
    ...(bare
      ? {}
      : { background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, boxShadow: cardShadow }),
  };

  return (
    <div style={wrap}>
      <div style={{ background: colors.primarySurface, borderRadius: '50%', padding: '16px', marginBottom: '6px', display: 'flex' }}>
        {icon}
      </div>
      <h3 style={{ fontSize: '15px', fontWeight: 700, color: colors.text }}>{title}</h3>
      <p style={{ fontSize: '12px', color: colors.textMuted, maxWidth: '340px', lineHeight: 1.5 }}>{description}</p>
      {action && <div style={{ marginTop: '14px', display: 'flex', gap: '10px' }}>{action}</div>}
    </div>
  );
};
