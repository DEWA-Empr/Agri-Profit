import { useEffect, useMemo, useState, type CSSProperties } from 'react';
import { Plus, ClipboardList, Undo2, Droplets } from 'lucide-react';
import { ledgerService } from '../../lib/apiClient';
import type { OperationalLog } from '../../types/domain';
import { colors } from '../../styles/theme';
import { EmptyState } from '../../components/EmptyState';
import { FarmRecordCreateForm } from './FarmRecordCreateForm';
import { ReverseConfirmDialog } from './ReverseConfirmDialog';
import { DryingRunResult } from './DryingRunResult';

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
  // Filters. Empty string means "no filter" for both.
  const [cropFilter, setCropFilter] = useState('');
  const [activityFilter, setActivityFilter] = useState('');
  // The bioprocess log whose metrics are on screen. Display only: the panel
  // re-reads GET /bioprocess/{id}, which computes everything from the stored
  // parameters, so browsing a run shows exactly what saving it showed.
  const [metricsLogId, setMetricsLogId] = useState<number | null>(null);

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
  // defaults to limit=100, so past 100 records a reversal can fall outside the
  // response and leave its original looking eligible. The eligibility test
  // below is therefore a UX affordance, not a guarantee — the 409 handler in
  // handleConfirm is what actually keeps us honest.
  //
  // The FILTERS BELOW WIDEN THAT GAP, and deliberately so. reversedIds is built
  // from every fetched log, not from the filtered view, so filtering does not
  // hide a "Reversed" pill. But a crop filter still narrows what a reader can
  // SEE: reverse_log carries no crop onto the correcting entry (so a reversal
  // cannot distort per-crop yield analytics), which means a reversal never
  // matches a crop filter. Filter to one crop and the reversed original shows
  // its pill with its correction nowhere on screen. The money is right; the
  // audit trail is half-visible. Same 409 backstop, same honesty about it.
  const reversedIds = useMemo(
    () => new Set(logs.map((l) => l.reverses_id).filter((id): id is number => id != null)),
    [logs],
  );

  const canReverse = (log: OperationalLog) =>
    log.reverses_id == null && !reversedIds.has(log.id);

  // Filter options come from the records themselves rather than from a literal.
  // The form's own crop list is assembled from the API (see ./cropOptions) and
  // its category list is a literal beside the form; duplicating either here
  // would be a third list to drift. What the farm has actually filed is both
  // the honest set and the only one that can never offer an option that matches
  // nothing.
  const cropChoices = useMemo(
    () => [...new Set(logs.map((l) => l.crop).filter((c): c is string => !!c))].sort(),
    [logs],
  );
  const activityChoices = useMemo(
    () => [...new Set(logs.map((l) => l.activity_type))].sort(),
    [logs],
  );

  // The filtered view. Applied on the client over the whole fetched set, which
  // is sound HERE because every farm's ledger is well inside the limit=100 the
  // read returns — the largest is 34 records. If a farm ever crosses that, this
  // becomes a filter over a truncated set and would under-report matches
  // silently; the filter would have to move into the query at that point.
  const visibleLogs = useMemo(
    () => logs.filter((l) =>
      (!cropFilter || l.crop === cropFilter)
      && (!activityFilter || l.activity_type === activityFilter)),
    [logs, cropFilter, activityFilter],
  );

  const filtering = cropFilter !== '' || activityFilter !== '';

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
  const filterLabel: CSSProperties = { fontSize: '11px', fontWeight: 600, color: colors.labelText };
  const filterField: CSSProperties = { padding: '6px 9px', borderRadius: '7px', border: `1px solid ${colors.borderInput}`, fontSize: '11.5px', background: colors.surface, color: colors.textBody, textTransform: 'capitalize' };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
        {/* Filters appear only once there is something to filter. */}
        {logs.length > 0 ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <label htmlFor="fr-activity" style={filterLabel}>Activity</label>
            <select
              id="fr-activity"
              value={activityFilter}
              onChange={(e) => setActivityFilter(e.target.value)}
              style={filterField}
            >
              <option value="">All</option>
              {activityChoices.map((a) => (
                <option key={a} value={a} style={{ textTransform: 'capitalize' }}>{a}</option>
              ))}
            </select>
            <label htmlFor="fr-crop" style={filterLabel}>Crop</label>
            <select
              id="fr-crop"
              value={cropFilter}
              onChange={(e) => setCropFilter(e.target.value)}
              style={filterField}
            >
              <option value="">All</option>
              {cropChoices.map((c) => (
                <option key={c} value={c} style={{ textTransform: 'capitalize' }}>{c}</option>
              ))}
            </select>
            {filtering && (
              <button
                onClick={() => { setCropFilter(''); setActivityFilter(''); }}
                style={{ background: 'transparent', border: `0.5px solid ${colors.borderInput}`, borderRadius: '7px', padding: '5px 10px', fontSize: '11px', fontWeight: 600, color: colors.textBody, cursor: 'pointer' }}
              >
                Clear
              </button>
            )}
            <span style={{ fontSize: '11px', color: colors.textMuted }}>
              {filtering ? `${visibleLogs.length} of ${logs.length} records` : `${logs.length} record${logs.length === 1 ? '' : 's'}`}
            </span>
          </div>
        ) : <span />}
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

      {metricsLogId != null && (
        <DryingRunResult
          logId={metricsLogId}
          title="Drying run"
          onDone={() => setMetricsLogId(null)}
        />
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
      ) : logs.length > 0 && visibleLogs.length === 0 ? (
        // Filtered down to nothing. Deliberately NOT the EmptyState: the ledger
        // is not empty and "log your first activity" would be false.
        <div style={card}>
          <p style={{ padding: '24px', fontSize: '12px', color: colors.textMuted }}>
            No records match this filter.{' '}
            <button
              onClick={() => { setCropFilter(''); setActivityFilter(''); }}
              style={{ background: 'none', border: 'none', padding: 0, font: 'inherit', color: colors.primaryDark, fontWeight: 600, cursor: 'pointer' }}
            >
              Clear the filter
            </button>{' '}
            to see all {logs.length} records.
          </p>
        </div>
      ) : logs.length > 0 ? (
        <div style={card}>
          <div className="table-scroll"><table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={th}>Activity</th>
                <th style={th}>Crop</th>
                <th style={th}>Description</th>
                <th style={th}>Quantity</th>
                <th style={th}>Amount (₦)</th>
                <th style={th}>Date</th>
                <th style={th}>Status</th>
                <th style={{ ...th, textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {visibleLogs.map((log) => {
                const ft = log.financial_transaction;
                const isCredit = ft?.transaction_type === 'credit';
                const isReversal = log.reverses_id != null;
                const wasReversed = reversedIds.has(log.id);
                return (
                  <tr key={log.id} style={{ background: isReversal ? 'rgba(160,92,0,0.04)' : undefined }}>
                    <td style={{ ...td, fontWeight: 600, textTransform: 'capitalize', color: wasReversed ? colors.textMuted : undefined }}>{log.activity_type}</td>
                    {/* Stored normalised to lower case (schemas._normalise_crop), so
                        capitalize here rather than trusting what was typed. Nullable
                        column: an em-dash, not a blank cell, when there is no crop —
                        which is also every reversal entry (reverse_log deliberately
                        carries no crop). */}
                    <td style={{ ...td, textTransform: 'capitalize', color: wasReversed ? colors.textMuted : undefined }}>{log.crop || '—'}</td>
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
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', justifyContent: 'flex-end' }}>
                      {log.activity_type === 'bioprocess' && (
                        <button
                          onClick={() => setMetricsLogId(log.id)}
                          title="Show the drying metrics for this run"
                          style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'transparent', border: `0.5px solid ${colors.borderInput}`, borderRadius: '7px', padding: '5px 10px', fontSize: '11px', fontWeight: 600, color: colors.textBody, cursor: 'pointer' }}
                        >
                          <Droplets size={12} /> View metrics
                        </button>
                      )}
                      {canReverse(log) ? (
                        <button
                          onClick={() => { setReverseError(''); setPendingReversal(log); }}
                          title="Post a correcting entry for this record"
                          style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'transparent', border: `0.5px solid ${colors.borderInput}`, borderRadius: '7px', padding: '5px 10px', fontSize: '11px', fontWeight: 600, color: colors.textBody, cursor: 'pointer' }}
                        >
                          <Undo2 size={12} /> Reverse
                        </button>
                      ) : (
                        log.activity_type !== 'bioprocess' && <span style={{ fontSize: '11px', color: colors.textFaint }}>—</span>
                      )}
                      </span>
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
