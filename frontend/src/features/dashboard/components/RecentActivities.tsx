import React from 'react';
import { Clock } from 'lucide-react';
import type { OperationalLog } from '../../../types/domain';

const placeholders = [
  { dot: '#639922', title: 'Maize harvest — 12 bags', meta: 'Crop yield · Today', amount: '+₦48,000', isPos: true },
  { dot: '#BA7517', title: 'NPK fertilizer — 3 bags', meta: 'Input cost · Yesterday', amount: '-₦9,600', isPos: false },
  { dot: '#378ADD', title: 'DSS yield forecast', meta: 'Prediction · Mon', amount: 'View →', isPos: true, customColor: '#378ADD' },
  { dot: '#639922', title: 'Tomato sale — 8 crates', meta: 'Produce sale · Sun', amount: '+₦32,000', isPos: true }
];

// Shows the latest operational logs, falling back to illustrative placeholders
// when there are none yet.
export const RecentActivities: React.FC<{ logs: OperationalLog[] }> = ({ logs }) => (
  <div style={{ background: '#fff', borderRadius: '12px', border: '0.5px solid #e8ede4', padding: '20px' }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '15px' }}>
      <Clock size={18} color="#639922" />
      <h3 style={{ fontSize: '12px', fontWeight: '600' }}>Recent activities</h3>
    </div>
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {(logs.length > 0 ? logs.slice(0, 4) : placeholders).map((item: any, idx) => (
        <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '11px', padding: '10px 0', borderBottom: '0.5px solid #f5f5f5' }}>
          <div style={{ width: '9px', height: '9px', borderRadius: '50%', backgroundColor: item.dot || (item.activity_type === 'yield' ? '#639922' : '#BA7517'), flexShrink: 0 }} />
          <div>
            <p style={{ fontSize: '12px', color: '#222' }}>{item.title || item.description}</p>
            <p style={{ fontSize: '10px', color: '#aaa', marginTop: '1px' }}>{item.meta || `${item.activity_type.toUpperCase()} · Today`}</p>
          </div>
          <span style={{
            fontSize: '12px', fontWeight: '500', marginLeft: 'auto',
            color: item.customColor || (item.isPos || item.financial_transaction?.transaction_type === 'credit' ? '#3B6D11' : '#c0392b')
          }}>
            {item.amount || (item.financial_transaction ? `${item.financial_transaction.transaction_type === 'credit' ? '+' : '-'}₦${item.financial_transaction.amount.toLocaleString()}` : 'N/A')}
          </span>
        </div>
      ))}
    </div>
  </div>
);
