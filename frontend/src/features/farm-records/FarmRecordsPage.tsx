import { useEffect, useState, type CSSProperties } from 'react';
import { Plus } from 'lucide-react';
import { ledgerService } from '../../lib/apiClient';
import type { OperationalLog } from '../../types/domain';
import { colors } from '../../styles/theme';
import { FarmRecordCreateForm } from './FarmRecordCreateForm';

// Farm Records = the list of Operational Logs (each with its paired Financial
// Transaction), plus a full create form for logging new activity.
const FarmRecordsPage = ({ isOnline }: { isOnline: boolean }) => {
  const [logs, setLogs] = useState<OperationalLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  const fetchLogs = () => {
    ledgerService.getLogs()
      .then((res) => setLogs(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchLogs(); }, []);

  const th: CSSProperties = { textAlign: 'left', fontSize: '10px', fontWeight: 700, letterSpacing: '0.05em', color: colors.textMuted, textTransform: 'uppercase', padding: '10px 12px', borderBottom: `0.5px solid ${colors.border}` };
  const td: CSSProperties = { fontSize: '12px', color: colors.textBody, padding: '11px 12px', borderBottom: `0.5px solid ${colors.dividerLight}` };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
        <button
          onClick={() => setShowForm((s) => !s)}
          style={{ display: 'flex', alignItems: 'center', gap: '8px', background: colors.primaryDark, color: colors.onPrimary, padding: '8px 14px', borderRadius: '8px', border: 'none', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
        >
          <Plus size={16} /> {showForm ? 'Close' : 'Log activity'}
        </button>
      </div>

      {showForm && (
        <FarmRecordCreateForm isOnline={isOnline} onSaved={fetchLogs} onClose={() => setShowForm(false)} />
      )}

      <div style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, overflow: 'hidden' }}>
        {loading ? (
          <p style={{ padding: '24px', fontSize: '12px', color: colors.textMuted }}>Loading records…</p>
        ) : logs.length === 0 ? (
          <p style={{ padding: '24px', fontSize: '12px', color: colors.textMuted }}>No records yet. Use “Log activity” to add your first record.</p>
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
                    <td style={{ ...td, fontWeight: 600, color: ft ? (isCredit ? colors.primaryDark : colors.danger) : colors.textMuted }}>
                      {ft ? `${isCredit ? '+' : '-'}${ft.amount.toLocaleString()}` : '—'}
                    </td>
                    <td style={{ ...td, color: colors.textMuted }}>{new Date(log.timestamp).toLocaleDateString()}</td>
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
