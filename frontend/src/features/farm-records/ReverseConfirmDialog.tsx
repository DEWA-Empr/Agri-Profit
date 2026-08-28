import { useEffect, type CSSProperties } from 'react';
import { Undo2 } from 'lucide-react';
import type { OperationalLog } from '../../types/domain';
import { colors } from '../../styles/theme';

// Confirmation for posting a reversal.
//
// The wording is deliberate. Reversal is NOT deletion — the original entry
// stays in the record and both rows remain visible afterwards — so the dialog
// says what actually happens in plain terms rather than asking "are you sure?".
// Nothing here uses the word delete, remove or undo, because none of them is
// what the ledger does (see CONTEXT.md, "Reversal").
interface Props {
  log: OperationalLog;
  busy: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

export const ReverseConfirmDialog = ({ log, busy, onCancel, onConfirm }: Props) => {
  // Escape closes, as long as the request isn't already in flight.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !busy) onCancel();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [busy, onCancel]);

  const ft = log.financial_transaction;
  const isCredit = ft?.transaction_type === 'credit';
  const amount = ft ? `${isCredit ? '+' : '-'}₦${ft.amount.toLocaleString()}` : '—';

  const btn: CSSProperties = { padding: '9px 16px', borderRadius: '8px', fontSize: '12px', fontWeight: 600, cursor: busy ? 'default' : 'pointer', opacity: busy ? 0.6 : 1 };

  // The overlay scrolls rather than centring when the dialog is taller than the
  // viewport: `align-items: center` overflows equally in both directions, which
  // puts the title above the top edge and out of reach on a short window.
  // `margin: auto` on the card centres it when it fits and scrolls when it does
  // not — the behaviour a farmer on a small phone actually needs.
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="reverse-dialog-title"
      onClick={() => { if (!busy) onCancel(); }}
      style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.35)', display: 'flex', justifyContent: 'center', overflowY: 'auto', padding: '20px', zIndex: 100 }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="fade-in-up"
        style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, padding: '24px', maxWidth: '440px', width: '100%', margin: 'auto', boxShadow: '0 8px 32px rgba(0,0,0,0.18)' }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ background: 'rgba(160,92,0,0.12)', borderRadius: '9px', padding: '8px', display: 'flex' }}>
            <Undo2 size={17} color={colors.warn} />
          </div>
          <h3 id="reverse-dialog-title" style={{ fontSize: '15px', fontWeight: 700, color: colors.textStrong }}>
            Correct this record?
          </h3>
        </div>

        <p style={{ fontSize: '12.5px', color: colors.textBody, lineHeight: 1.6, marginTop: '14px' }}>
          This posts a correcting entry of the same amount, which cancels out the money on this
          record. The original stays in your records, and both remain visible — nothing is deleted.
        </p>

        {/* The record in question, so there is no doubt which row this affects. */}
        <div style={{ marginTop: '14px', background: colors.appBg, borderRadius: '8px', padding: '12px 14px', border: `0.5px solid ${colors.border}` }}>
          <p style={{ fontSize: '12px', fontWeight: 600, color: colors.textStrong, textTransform: 'capitalize' }}>
            {log.activity_type}{log.description ? ` — ${log.description}` : ''}
          </p>
          <p style={{ fontSize: '11px', color: colors.textMuted, marginTop: '3px' }}>
            {amount} · {new Date(log.timestamp).toLocaleDateString()}
          </p>
        </div>

        <p style={{ fontSize: '11px', color: colors.textMuted, lineHeight: 1.5, marginTop: '12px' }}>
          Your profit, costs and reports will update to leave this entry out. A correcting entry
          cannot itself be corrected, so check the details above before continuing.
        </p>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
          <button
            onClick={onCancel}
            disabled={busy}
            style={{ ...btn, background: colors.surface, border: `0.5px solid ${colors.borderInput}`, color: colors.textBody }}
          >
            Keep as it is
          </button>
          <button
            onClick={onConfirm}
            disabled={busy}
            style={{ ...btn, background: colors.warn, border: 'none', color: colors.onPrimary }}
          >
            {busy ? 'Posting…' : 'Post correcting entry'}
          </button>
        </div>
      </div>
    </div>
  );
};
