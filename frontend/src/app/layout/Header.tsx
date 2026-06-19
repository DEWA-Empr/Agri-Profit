import type { FC } from 'react';
import { Download, Plus } from 'lucide-react';

// Top bar with page title and primary actions. The Export and Log Activity
// buttons are wired up in later phases (P&L export, quick-log shortcut).
export const Header: FC = () => (
  <header style={{ height: '60px', background: '#fff', borderBottom: '0.5px solid #e8ede4', padding: '15px 22px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
    <div>
      <h2 style={{ fontSize: '17px', fontWeight: '500', color: '#111', letterSpacing: '-0.3px' }}>Farm Overview</h2>
      <p style={{ fontSize: '11px', color: '#888', marginTop: '2px' }}>Tuesday, 16 June 2026 • Currency in NGN (₦)</p>
    </div>
    <div style={{ display: 'flex', gap: '10px' }}>
      <button style={{ padding: '7px 14px', border: '0.5px solid #d0d8c8', borderRadius: '8px', backgroundColor: '#fff', color: '#444', fontSize: '12px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
        <Download size={14} /> Export
      </button>
      <button style={{ padding: '7px 14px', background: '#3B6D11', color: '#EAF3DE', borderRadius: '8px', fontSize: '12px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', border: 'none' }}>
        <Plus size={14} /> Log Activity
      </button>
    </div>
  </header>
);
