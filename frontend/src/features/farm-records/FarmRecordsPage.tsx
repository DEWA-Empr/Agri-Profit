import { useEffect, useMemo, useState, type CSSProperties } from 'react';
import { Plus, ClipboardList, Undo2 } from 'lucide-react';
import { ledgerService } from '../../lib/apiClient';
import type { OperationalLog } from '../../types/domain';
import { colors } from '../../styles/theme';
import { EmptyState } from '../../components/EmptyState';
import { FarmRecordCreateForm } from './FarmRecordCreateForm';
import { ReverseConfirmDialog } from './ReverseConfirmDialog';

// Farm Records = the list of Operational Logs (each with its paired Financial
// Transaction), plus a full create form for logging new activity.
// onRecordChange notifies the app shell (via App) that the record set changed,
// so the live Farm Records nav badge can refresh.
const FarmRecordsPage = ({ isOnline, onRecordChange }: { isOnline: boolean; onRecordChange?: () => void }) => {
  const [logs, setLogs] = useState<OperationalLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  // The log awaiting confirmation, and any error from the last reversal attempt.
  const [pendingReversal, setPendingReversal] = useState<OperationalLog | null>(null);
  const [reversing, setReversing] = useState(false);
  const [reverseError, setReverseError] = useState('');

  const fetchLogs = () => {
    ledgerService.getLogs()
      .then((res) => setLogs(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  // After a save: refresh this list and the sidebar badge.
  const handleSaved = () => {
    fetchLogs();
    onRecordChange?.();
  };

  useEffect(() => { fetchLogs(); }, []);

  // Which logs have been reversed. The API exposes `reverses_id` (this log
  // offsets that one) but nothing in the other direction, so we invert the
  // relation here: any id that some other row points at has been reversed.
  //
  // CAVEAT: this is only as complete as the page we fetched. GET /ledger/logs
  // defaults to limit=100 with no ORDER BY, so past 100 records a reversal can
  // fall outside the response and leave its original looking eligible. The
  // eligibility test below is therefore a UX affordance, not a guarantee — the
  // 409 handler in handleConfirm is what actually keeps us honest.
  const reversedIds = useMemo(
    () => new Set(logs.map((l) => l.reverses_id).filter((id): id is number => id != null)),
    [logs],
  );

  const canReverse = (log: OperationalLog) =>
    log.reverses_id == null && !reversedIds.has(log.id);

  const handleConfirm = async () => {
    if (!pendingReversal) return;
    setReversing(true);
    setReverseError('');
    try {
      // ledgerService.reverseLog has already dropped the read cache by the
      // time this resolves, so the refetch below repopulates it with
      // post-reversal data rather than being served the pre-reversal list the
      // service worker held (vite.config.ts caches /ledger, /reports and the
      // /dss reads StaleWhileRevalidate).
      await ledgerService.reverseLog(pendingReversal.id);
      setPendingReversal(null);
      fetchLogs();
      onRecordChange?.();
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 409) {
        // Raced with another device, or the original's reversal was outside our
        // page. Re-read so the row picks up its real state.
        setReverseError('This record has already been reversed, or is itself a reversal. Refreshing your records…');
        fetchLogs();
      } else if (status === 404) {
        setReverseError('That record could not be found. Refreshing your records…');
        fetchLogs();
      } else if (!isOnline) {
        setReverseError('You are offline. Reversals need a connection — this one has not been saved.');
      } else {
        setReverseError('Could not post the correcting entry. Please try again.');
      }
    } finally {
      setReversing(false);
    }
  };

  const th: CSSProperties = { textAlign: 'left', fontSize: '10px', fontWeight: 700, letterSpacing: '0.05em', color: colors.textMuted, textTransform: 'uppercase', padding: '10px 12px', borderBottom: `0.5px solid ${colors.border}` };
  const td: CSSProperties = { fontSize: '12px', color: colors.textBody, padding: '11px 12px', borderBottom: `0.5px solid ${colors.dividerLight}` };
  const pill: CSSProperties = { display: 'inline-block', fontSize: '9.5px', fontWeight: 700, letterSpacing: '0.04em', padding: '2px 8px', borderRadius: '20px', whiteSpace: 'nowrap' };
  const card: CSSProperties = { background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, overflow: 'hidden' };

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
        <FarmRecordCreateForm isOnline={isOnline} onSaved={handleSaved} onClose={() => setShowForm(false)} />
      )}

      {reverseError && (
        <div style={{ background: 'rgba(192,57,43,0.08)', border: `0.5px solid ${colors.danger}`, borderRadius: '8px', padding: '10px 14px', fontSize: '12px', color: colors.danger }}>
          {reverseError}
        </div>
      )}

      {/* Three mutually exclusive states, in priority order:
            1. loading            — the first fetch has not resolved
            2. logs.length > 0    — the record table
            3. !showForm          — the empty state, with its call to action
          and nothing at all when the ledger is empty AND the create form is
          open: the form is the whole content then, and printing "no records
          yet" underneath it told the user something they were already busy
          fixing. */}
      {loading ? (
        <div style={card}>
          <p style={{ padding: '24px', fontSize: '12px', color: colors.textMuted }}>Loading records…</p>
        </div>
      ) : logs.length > 0 ? (
        <div style={card}>
          <div className="table-scroll"><table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={th}>Activity</th>
                <th style={th}>Description</th>
                <th style={th}>Quantity</th>
                <th style={th}>Amount (₦)</th>
                <th style={th}>Date</th>
                <th style={th}>Status</th>
                <th style={{ ...th, textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => {
                const ft = log.financial_transaction;
                const isCredit = ft?.transaction_type === 'credit';
                const isReversal = log.reverses_id != null;
                const wasReversed = reversedIds.has(log.id);
                return (
                  <tr key={log.id} style={{ background: isReversal ? 'rgba(160,92,0,0.04)' : undefined }}>
                    <td style={{ ...td, fontWeight: 600, textTransform: 'capitalize', color: wasReversed ? colors.textMuted : undefined }}>{log.activity_type}</td>
                    <td style={{ ...td, color: wasReversed ? colors.textMuted : undefined }}>{log.description || '—'}</td>
                    <td style={td}>{log.quantity != null ? `${log.quantity} ${log.unit || ''}`.trim() : '—'}</td>
                    <td style={{
                      ...td,
                      fontWeight: 600,
                      color: ft ? (isCredit ? colors.primaryDark : colors.danger) : colors.textMuted,
                      // A reversed original is struck through: the entry still
                      // stands in the record, but its money no longer counts.
                      textDecoration: wasReversed ? 'line-through' : undefined,
                      opacity: wasReversed ? 0.65 : 1,
                    }}>
                      {ft ? `${isCredit ? '+' : '-'}${ft.amount.toLocaleString()}` : '—'}
                    </td>
                    <td style={{ ...td, color: colors.textMuted }}>{new Date(log.timestamp).toLocaleDateString()}</td>
                    <td style={td}>
                      {isReversal ? (
                        <span style={{ ...pill, background: 'rgba(160,92,0,0.12)', color: colors.warn }}>
                          Correction of #{log.reverses_id}
                        </span>
                      ) : wasReversed ? (
                        <span style={{ ...pill, background: 'rgba(0,0,0,0.05)', color: colors.textMuted }}>
                          Reversed
                        </span>
                      ) : (
                        <span style={{ fontSize: '11px', color: colors.textFaint }}>—</span>
                      )}
                    </td>
                    <td style={{ ...td, textAlign: 'right' }}>
                      {canReverse(log) ? (
                        <button
                          onClick={() => { setReverseError(''); setPendingReversal(log); }}
                          title="Post a correcting entry for this record"
                          style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'transparent', border: `0.5px solid ${colors.borderInput}`, borderRadius: '7px', padding: '5px 10px', fontSize: '11px', fontWeight: 600, color: colors.textBody, cursor: 'pointer' }}
                        >
                          <Undo2 size={12} /> Reverse
                        </button>
                      ) : (
                        <span style={{ fontSize: '11px', color: colors.textFaint }}>—</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table></div>
        </div>
      ) : !showForm ? (
        <EmptyState
          icon={<ClipboardList size={26} color={colors.primary} />}
          title="No records yet"
          description="Log your first activity — a planting, an input purchase or a sale — and it will flow into your profit, costs and reports."
          action={
            <button
              onClick={() => setShowForm(true)}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', background: colors.primaryDark, color: colors.onPrimary, padding: '10px 16px', borderRadius: '8px', border: 'none', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
            >
              <Plus size={16} /> Log your first activity
            </button>
          }
        />
      ) : null}

      {pendingReversal && (
        <ReverseConfirmDialog
          log={pendingReversal}
          busy={reversing}
          onCancel={() => setPendingReversal(null)}
          onConfirm={handleConfirm}
        />
      )}
    </div>
  );
};

export default FarmRecordsPage;
