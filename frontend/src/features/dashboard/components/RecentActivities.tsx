import React from 'react';
import { Clock } from 'lucide-react';
import type { OperationalLog } from '../../../types/domain';
import { colors } from '../../../styles/theme';

const placeholders = [
  { dot: colors.primary, title: 'Maize harvest — 12 bags', meta: 'Crop yield · Today', amount: '+₦48,000', isPos: true },
  { dot: colors.warnAccent, title: 'NPK fertilizer — 3 bags', meta: 'Input cost · Yesterday', amount: '-₦9,600', isPos: false },
  { dot: colors.infoAlt, title: 'DSS yield forecast', meta: 'Prediction · Mon', amount: 'View →', isPos: true, customColor: colors.infoAlt },
  { dot: colors.primary, title: 'Tomato sale — 8 crates', meta: 'Produce sale · Sun', amount: '+₦32,000', isPos: true }
];

// Shows the latest operational logs, falling back to illustrative placeholders
// when there are none yet.
export const RecentActivities: React.FC<{ logs: OperationalLog[] }> = ({ logs }) => (
  <div style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, padding: '20px' }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '15px' }}>
      <Clock size={18} color={colors.primary} />
      <h3 style={{ fontSize: '12px', fontWeight: '600' }}>Recent activities</h3>
    </div>
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {(logs.length > 0 ? logs.slice(0, 4) : placeholders).map((item: any, idx) => (
        <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '11px', padding: '10px 0', borderBottom: `0.5px solid ${colors.dividerLight}` }}>
          <div style={{ width: '9px', height: '9px', borderRadius: '50%', backgroundColor: item.dot || (item.activity_type === 'yield' ? colors.primary : colors.warnAccent), flexShrink: 0 }} />
          <div>
            <p style={{ fontSize: '12px', color: colors.text }}>{item.title || item.description}</p>
            <p style={{ fontSize: '10px', color: colors.textFaint, marginTop: '1px' }}>{item.meta || `${item.activity_type.toUpperCase()} · Today`}</p>
          </div>
          <span style={{
            fontSize: '12px', fontWeight: '500', marginLeft: 'auto',
            color: item.customColor || (item.isPos || item.financial_transaction?.transaction_type === 'credit' ? colors.primaryDark : colors.danger)
          }}>
            {item.amount || (item.financial_transaction ? `${item.financial_transaction.transaction_type === 'credit' ? '+' : '-'}₦${item.financial_transaction.amount.toLocaleString()}` : 'N/A')}
          </span>
        </div>
      ))}
    </div>
  </div>
);
