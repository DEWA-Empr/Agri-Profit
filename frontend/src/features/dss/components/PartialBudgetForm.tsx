import { useState, type CSSProperties } from 'react';
import { Calculator, WifiOff } from 'lucide-react';
import { colors } from '../../../styles/theme';
import { nairaExact } from '../format';
import { dssService } from '../../../lib/apiClient';
import { partialBudgetLocal } from '../partialBudget';
import type { PartialBudgetRequest, PartialBudgetResponse } from '../../../types/domain';

// Partial budget: appraise ONE proposed change, without building a whole
// enterprise budget for the farm.
//
// OFFLINE BY DESIGN. This is the only panel here that reads no ledger row. Four
// numbers the user typed go in and a signed net change comes out, so there is
// nothing to be stale and nothing to sync. It calls the backend when it can —
// enterprise_service.partial_budget is where the arithmetic is defined and the
// server stays the source of truth — and falls back to the identical local
// computation when the request fails. The fallback is LABELLED rather than
// substituted silently: the user is told which side of the wire produced the
// figure they are reading, in the same spirit as period_source on the
// break-even response.

const FIELDS = [
  {
    key: 'added_revenue_ngn' as const,
    label: 'Added revenue',
    hint: 'New money the change brings in',
    side: 'benefit' as const,
  },
  {
    key: 'reduced_cost_ngn' as const,
    label: 'Reduced cost',
    hint: 'Spending the change saves you',
    side: 'benefit' as const,
  },
  {
    key: 'lost_revenue_ngn' as const,
    label: 'Lost revenue',
    hint: 'Money you stop earning because of it',
    side: 'cost' as const,
  },
  {
    key: 'added_cost_ngn' as const,
    label: 'Added cost',
    hint: 'New spending the change requires',
    side: 'cost' as const,
  },
];

const EMPTY: Record<string, string> = {
  added_revenue_ngn: '', reduced_cost_ngn: '', lost_revenue_ngn: '', added_cost_ngn: '',
};

export const PartialBudgetForm = ({ card }: { card: CSSProperties }) => {
  const [values, setValues] = useState<Record<string, string>>(EMPTY);
  const [result, setResult] = useState<PartialBudgetResponse | null>(null);
  // Which side of the wire produced the figure on screen.
  const [computedLocally, setComputedLocally] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const parsed = (): PartialBudgetRequest | null => {
    const out: Record<string, number> = {};
    for (const f of FIELDS) {
      const raw = values[f.key].trim();
      // A blank field is zero — "this change does not touch that quantity" is
      // the common case and forcing four entries to appraise a one-sided change
      // would be busywork.
      const n = raw === '' ? 0 : Number(raw);
      // The backend rejects a negative with a 422. Catching it here keeps the
      // form usable offline, where there is no 422 to catch.
      if (!Number.isFinite(n) || n < 0) return null;
      out[f.key] = n;
    }
    return out as unknown as PartialBudgetRequest;
  };

  const submit = async () => {
    const input = parsed();
    if (!input) {
      setError('Every figure must be a number, and none of them can be negative. The direction of the change is set by which box you put it in, not by a minus sign.');
      setResult(null);
      return;
    }
    setError(null);
    setBusy(true);
    try {
      const res = await dssService.partialBudget(input);
      setResult(res.data);
      setComputedLocally(false);
    } catch {
      // No network, or the server is unreachable. The appraisal needs neither.
      setResult(partialBudgetLocal(input));
      setComputedLocally(true);
    } finally {
      setBusy(false);
    }
  };

  const reset = () => { setValues(EMPTY); setResult(null); setError(null); setComputedLocally(false); };

  const input: CSSProperties = { width: '100%', padding: '8px 10px', borderRadius: '7px', border: `1px solid ${colors.borderInput}`, fontSize: '12px', marginTop: '4px' };
  const label: CSSProperties = { fontSize: '11px', fontWeight: 600, color: colors.labelText };

  const positive = result != null && result.net_change_ngn >= 0;

  return (
    <div style={card}>
      <h3 style={{ fontSize: '12px', fontWeight: 700, color: colors.text, display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '0.5px solid #eee', paddingBottom: '10px', marginBottom: '4px' }}>
        <Calculator size={15} color={colors.primary} /> Partial budget
      </h3>
      <p style={{ fontSize: '10.5px', color: colors.textMuted, lineHeight: 1.6, margin: '8px 0 12px' }}>
        Appraise one change on its own — hiring a thresher, switching fertiliser, renting another plot. It looks only
        at the quantities that change, so it needs no budget for the rest of the farm and reads none of your records.
      </p>

      <div className="grid-2" style={{ gap: '11px' }}>
        {FIELDS.map((f) => (
          <div key={f.key}>
            <label style={{ ...label, color: f.side === 'benefit' ? colors.primaryDark : colors.dangerAlt }}>
              {f.label}
            </label>
            <input
              type="number"
              min={0}
              step="0.01"
              inputMode="decimal"
              placeholder="0"
              value={values[f.key]}
              onChange={(e) => setValues({ ...values, [f.key]: e.target.value })}
              style={input}
            />
            <span style={{ display: 'block', fontSize: '9.5px', color: colors.textFaint, marginTop: '3px', lineHeight: 1.45 }}>{f.hint}</span>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', gap: '8px', marginTop: '13px' }}>
        <button
          onClick={submit}
          disabled={busy}
          style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', background: colors.primaryDark, color: colors.onPrimary, padding: '10px', borderRadius: '8px', border: 'none', fontSize: '12px', fontWeight: 600, cursor: busy ? 'default' : 'pointer', opacity: busy ? 0.6 : 1 }}
        >
          <Calculator size={15} /> {busy ? 'Working…' : 'Work it out'}
        </button>
        <button
          onClick={reset}
          style={{ background: colors.surfaceMuted, color: colors.textBody, padding: '10px 14px', borderRadius: '8px', border: `1px solid ${colors.border}`, fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
        >
          Clear
        </button>
      </div>

      {error && (
        <p style={{ fontSize: '11px', color: colors.danger, marginTop: '10px', lineHeight: 1.6 }}>{error}</p>
      )}

      {result && (
        <div style={{ marginTop: '13px', border: `0.5px solid ${colors.border}`, borderRadius: '9px', overflow: 'hidden' }}>
          <div style={{ background: positive ? 'rgba(99,153,34,0.08)' : 'rgba(192,57,43,0.06)', padding: '13px' }}>
            <p style={{ fontSize: '10px', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: positive ? colors.primaryDark : colors.danger }}>
              Net change
            </p>
            {/* Signed and unclamped. A negative result is the useful answer as
                often as a positive one, and it is stated as plainly. */}
            <p style={{ fontSize: '22px', fontWeight: 800, color: positive ? colors.primaryDark : colors.danger, marginTop: '4px' }}>
              {nairaExact(result.net_change_ngn)}
            </p>
            <p style={{ fontSize: '11px', color: colors.textBody, marginTop: '5px', lineHeight: 1.6 }}>
              {positive
                ? 'On these figures the change leaves you better off by this much.'
                : 'On these figures the change leaves you worse off by this much. That is a reason not to make it.'}
            </p>
          </div>
          {/* The working, so the result can be checked rather than trusted. */}
          <div style={{ padding: '11px 13px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {[
              ['Added revenue', result.added_revenue_ngn],
              ['Reduced cost', result.reduced_cost_ngn],
              ['Benefits', result.benefits_ngn],
              ['Lost revenue', result.lost_revenue_ngn],
              ['Added cost', result.added_cost_ngn],
              ['Costs', result.costs_ngn],
            ].map(([l, v], i) => (
              <div key={l as string} style={{ display: 'flex', justifyContent: 'space-between', gap: '10px' }}>
                <span style={{ fontSize: '11px', color: colors.textMuted, fontWeight: i === 2 || i === 5 ? 700 : 400 }}>{l}</span>
                <span style={{ fontSize: '11px', color: colors.textBody, fontWeight: i === 2 || i === 5 ? 700 : 500 }}>{nairaExact(v as number)}</span>
              </div>
            ))}
          </div>
          {computedLocally && (
            <div style={{ background: colors.surfaceMuted, borderTop: `0.5px solid ${colors.border}`, padding: '9px 13px', display: 'flex', alignItems: 'flex-start', gap: '7px' }}>
              <WifiOff size={13} color={colors.warn} style={{ flexShrink: 0, marginTop: '1px' }} />
              <span style={{ fontSize: '10px', color: colors.warn, lineHeight: 1.55 }}>
                Worked out on this device — the server could not be reached. The appraisal uses only the four figures
                you entered, so the answer is the same one the server would have given.
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
