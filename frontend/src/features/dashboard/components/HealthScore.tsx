import React from 'react';

// Farm health gauge. Static placeholder figures for now; a future iteration can
// derive the score from records & profitability.
export const HealthScore: React.FC = () => (
  <div style={{ background: '#fff', borderRadius: '12px', border: '0.5px solid #e8ede4', padding: '16px', display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 0 }}>
     <div style={{ position: 'relative', width: '96px', height: '96px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <svg width="96" height="96" style={{ transform: 'rotate(-90deg)', overflow: 'visible' }}>
          <circle cx="48" cy="48" r="40" stroke="#f0f7e8" strokeWidth="9" fill="transparent" />
          <circle cx="48" cy="48" r="40" stroke="#639922" strokeWidth="9" fill="transparent" strokeDasharray="251" strokeDashoffset="55" strokeLinecap="round" />
        </svg>
        <div style={{ position: 'absolute', textAlign: 'center' }}>
          <span style={{ fontSize: '24px', fontWeight: '500', color: '#1e3d0a', display: 'block', lineHeight: 1 }}>78</span>
          <span style={{ fontSize: '9px', color: '#639922', fontWeight: '500' }}>/ 100</span>
        </div>
     </div>
     <p style={{ fontSize: '13px', fontWeight: '500', color: '#27500A', marginTop: '10px' }}>Good standing</p>
     <p style={{ fontSize: '10px', color: '#888', marginTop: '2px' }}>Based on records & profitability</p>

     <div style={{ width: '100%', marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
        {[
          { l: 'Profitability', p: 82, c: '#639922' },
          { l: 'Record keeping', p: 75, c: '#97C459' },
          { l: 'Equipment', p: 60, c: '#BA7517' }
        ].map(b => (
          <div key={b.l}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
              <span style={{ fontSize: '10px', color: '#666', fontWeight: '500' }}>{b.l.toUpperCase()}</span>
              <span style={{ fontSize: '10px', color: '#666', fontWeight: '500' }}>{b.p}%</span>
            </div>
            <div style={{ height: '5px', background: '#f0f0f0', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: `${b.p}%`, height: '100%', background: b.c }} />
            </div>
          </div>
        ))}
     </div>
  </div>
);
