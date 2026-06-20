import type { FC } from 'react';
import { Download, Plus } from 'lucide-react';
import { downloadPnlCsv } from '../../features/reports/downloadPnlCsv';
import { colors } from '../../styles/theme';

// Top bar with page title and primary actions. Export downloads the P&L CSV;
// the Log Activity shortcut is wired in a later phase.
export const Header: FC = () => (
  <header style={{ height: '60px', background: colors.surface, borderBottom: `0.5px solid ${colors.border}`, padding: '15px 22px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
    <div>
      <h2 style={{ fontSize: '17px', fontWeight: '500', color: colors.textStrong, letterSpacing: '-0.3px' }}>Farm Overview</h2>
      <p style={{ fontSize: '11px', color: colors.textMuted, marginTop: '2px' }}>Tuesday, 16 June 2026 • Currency in NGN (₦)</p>
    </div>
    <div style={{ display: 'flex', gap: '10px' }}>
      <button onClick={downloadPnlCsv} style={{ padding: '7px 14px', border: `0.5px solid ${colors.borderInput}`, borderRadius: '8px', backgroundColor: colors.surface, color: '#444', fontSize: '12px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
        <Download size={14} /> Export
      </button>
      <button style={{ padding: '7px 14px', background: colors.primaryDark, color: colors.onPrimary, borderRadius: '8px', fontSize: '12px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', border: 'none' }}>
        <Plus size={14} /> Log Activity
      </button>
    </div>
  </header>
);
