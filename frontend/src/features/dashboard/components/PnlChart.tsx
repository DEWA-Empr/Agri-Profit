import React from 'react';
import { BarChart3 } from 'lucide-react';

// Monthly revenue/expense overview. Bars are placeholder figures for now; this
// is the component that the P&L module (Phase 4) will feed with real data.
export const PnlChart: React.FC = () => (
  <div style={{ background: '#fff', borderRadius: '12px', border: '0.5px solid #e8ede4', padding: '20px' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <BarChart3 size={18} color="#639922" />
        <h3 style={{ fontSize: '12px', fontWeight: '600' }}>Monthly P&L overview</h3>
      </div>
      <a href="#" style={{ fontSize: '11px', color: '#639922', fontWeight: '700', textDecoration: 'none' }}>See full report →</a>
    </div>

    <div style={{ display: 'flex', alignItems: 'end', justifyContent: 'space-between', height: '112px', padding: '0 10px' }}>
      {[
        { r: 70, e: 45 }, { r: 87, e: 56 }, { r: 62, e: 41 },
        { r: 101, e: 64 }, { r: 77, e: 52 }, { r: 112, e: 62 }
      ].map((h, i) => (
        <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
          <div style={{ display: 'flex', gap: '2px', alignItems: 'end' }}>
            <div style={{ width: '8px', height: `${h.r}px`, backgroundColor: '#639922', borderRadius: '1px 1px 0 0' }} />
            <div style={{ width: '8px', height: `${h.e}px`, backgroundColor: '#c0dd97', borderRadius: '1px 1px 0 0' }} />
          </div>
          <span style={{ fontSize: '9px', color: '#aaa', marginTop: '10px', fontWeight: '500' }}>{['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'][i]}</span>
        </div>
      ))}
    </div>
    <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', marginTop: '20px' }}>
       <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '10px', color: '#888' }}><div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#639922' }} /> Revenue</div>
       <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '10px', color: '#888' }}><div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#c0dd97' }} /> Expenses</div>
    </div>
  </div>
);
