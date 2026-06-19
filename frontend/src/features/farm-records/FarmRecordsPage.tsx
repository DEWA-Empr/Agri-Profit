import { useEffect, useState, type CSSProperties } from 'react';
import { ClipboardList } from 'lucide-react';
import { ledgerService } from '../../lib/apiClient';
import type { OperationalLog } from '../../types/domain';

// Farm Records = the list of Operational Logs (each with its paired Financial
// Transaction). Read-only here for now; the full create form is the dashboard
// quick-log and a richer form lands with the full module build.
const FarmRecordsPage = () => {
  const [logs, setLogs] = useState<OperationalLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ledgerService.getLogs()
      .then((res) => setLogs(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const th: CSSProperties = { textAlign: 'left', fontSize: '10px', fontWeight: 700, letterSpacing: '0.05em', color: '#888', textTransform: 'uppercase', padding: '10px 12px', borderBottom: '0.5px solid #e8ede4' };
  const td: CSSProperties = { fontSize: '12px', color: '#333', padding: '11px 12px', borderBottom: '0.5px solid #f5f5f5' };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <ClipboardList size={20} color="#639922" />
        <div>
          <h2 style={{ fontSize: '17px', fontWeight: 600, color: '#111' }}>Farm Records</h2>
          <p style={{ fontSize: '11px', color: '#888', marginTop: '2px' }}>All logged operational activities and their financial impact.</p>
        </div>
      </div>

      <div style={{ background: '#fff', borderRadius: '12px', border: '0.5px solid #e8ede4', overflow: 'hidden' }}>
        {loading ? (
          <p style={{ padding: '24px', fontSize: '12px', color: '#888' }}>Loading records…</p>
        ) : logs.length === 0 ? (
          <p style={{ padding: '24px', fontSize: '12px', color: '#888' }}>No records yet. Log an activity from the dashboard to get started.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={th}>Activity</th>
                <th style={th}>Description</th>
                <th style={th}>Quantity</th>
                <th style={th}>Amount (₦)</th>
                <th style={th}>Date</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => {
                const ft = log.financial_transaction;
                const isCredit = ft?.transaction_type === 'credit';
                return (
                  <tr key={log.id}>
                    <td style={{ ...td, fontWeight: 600, textTransform: 'capitalize' }}>{log.activity_type}</td>
                    <td style={td}>{log.description || '—'}</td>
                    <td style={td}>{log.quantity != null ? `${log.quantity} ${log.unit || ''}`.trim() : '—'}</td>
                    <td style={{ ...td, fontWeight: 600, color: ft ? (isCredit ? '#3B6D11' : '#c0392b') : '#888' }}>
                      {ft ? `${isCredit ? '+' : '-'}${ft.amount.toLocaleString()}` : '—'}
                    </td>
                    <td style={{ ...td, color: '#888' }}>{new Date(log.timestamp).toLocaleDateString()}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default FarmRecordsPage;
