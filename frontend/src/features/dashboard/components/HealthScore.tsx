import React from 'react';
import { colors } from '../../../styles/theme';

// Farm health gauge. Static placeholder figures for now; a future iteration can
// derive the score from records & profitability.
export const HealthScore: React.FC = () => (
  <div style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, padding: '16px', display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 0 }}>
     <div style={{ position: 'relative', width: '96px', height: '96px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <svg width="96" height="96" style={{ transform: 'rotate(-90deg)', overflow: 'visible' }}>
          <circle cx="48" cy="48" r="40" stroke={colors.primarySurface} strokeWidth="9" fill="transparent" />
          <circle cx="48" cy="48" r="40" stroke={colors.primary} strokeWidth="9" fill="transparent" strokeDasharray="251" strokeDashoffset="55" strokeLinecap="round" />
        </svg>
        <div style={{ position: 'absolute', textAlign: 'center' }}>
          <span style={{ fontSize: '24px', fontWeight: '500', color: colors.primaryDarkest, display: 'block', lineHeight: 1 }}>78</span>
          <span style={{ fontSize: '9px', color: colors.primary, fontWeight: '500' }}>/ 100</span>
        </div>
     </div>
     <p style={{ fontSize: '13px', fontWeight: '500', color: colors.primaryDarker, marginTop: '10px' }}>Good standing</p>
     <p style={{ fontSize: '10px', color: colors.textMuted, marginTop: '2px' }}>Based on records & profitability</p>

     <div style={{ width: '100%', marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
        {[
          { l: 'Profitability', p: 82, c: colors.primary },
          { l: 'Record keeping', p: 75, c: colors.primaryLight },
          { l: 'Equipment', p: 60, c: colors.warnAccent }
        ].map(b => (
          <div key={b.l}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
              <span style={{ fontSize: '10px', color: '#666', fontWeight: '500' }}>{b.l.toUpperCase()}</span>
              <span style={{ fontSize: '10px', color: '#666', fontWeight: '500' }}>{b.p}%</span>
            </div>
            <div style={{ height: '5px', background: colors.divider, borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: `${b.p}%`, height: '100%', background: b.c }} />
            </div>
          </div>
        ))}
     </div>
  </div>
);
