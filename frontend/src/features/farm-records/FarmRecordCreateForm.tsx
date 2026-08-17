import { useState, type CSSProperties, type FormEvent } from 'react';
import { Save } from 'lucide-react';
import type { Category, TransactionType, OperationalLogCreate } from '../../types/domain';
import { saveOperationalLog } from '../../lib/logs';
import { colors } from '../../styles/theme';

// NOTE: "Bioprocess" is deliberately absent. The backend requires a valid
// DryingParams payload on any bioprocess log (schemas.OperationalLogCreate
// ._validate_bioprocess_payload) and this form has no way to collect one, so
// choosing it produced a guaranteed 422. That is worse than a plain error:
// saveOperationalLog treats the failure as a network problem and queues the
// record in IndexedDB, where it re-fails on every flush, exhausts its retries
// and sits there permanently — with a Retry button that can never succeed.
// Re-add this option only together with the drying-parameter fields.
const CATEGORIES: { value: Category; label: string }[] = [
  { value: 'yield', label: 'Crop yield / sale' },
  { value: 'seed', label: 'Seed' },
  { value: 'fertilizer', label: 'Fertilizer' },
  { value: 'labour', label: 'Labour' },
  { value: 'mechanization', label: 'Mechanization' },
  { value: 'other', label: 'Other' },
];

// Crops the deterministic DSS groups by (mirrors the yield model's crops). A
// record's crop drives the per-crop unit-cost / gross-margin panel; leaving it
// blank files the record under "Unspecified" there.
const CROPS = ['maize', 'rice', 'sorghum', 'soybean', 'cassava'];

// Harvest units, fixed rather than free text. Yield totals are grouped by unit
// on the backend, and free text meant "kg", "Kg" and "kilos" became three
// different units for the same thing — with the per-crop total silently
// unavailable as a result. Existing records keep whatever text they were saved
// with; only new entries are constrained.
const UNITS = ['kg', 'tonnes', 'bags', 'crates'];

// Sales/income default to a credit; everything else is a cost (debit).
const defaultTxType = (c: Category): TransactionType => (c === 'yield' ? 'credit' : 'debit');

interface Props {
  isOnline: boolean;
  onSaved: () => void;
  onClose: () => void;
}

// Full create form for an operational log + its paired financial transaction.
// Richer than the dashboard quick-log: exposes quantity/unit, debit-vs-credit,
// and an optional tax category. Offline-aware via saveOperationalLog.
export const FarmRecordCreateForm = ({ isOnline, onSaved, onClose }: Props) => {
  const [form, setForm] = useState({
    activity_type: 'yield' as Category,
    crop: '',
    description: '',
    quantity: '',
    unit: '',
    transaction_type: 'credit' as TransactionType,
    amount: '',
    tax_category: '',
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const setActivity = (value: Category) =>
    // Re-default the debit/credit choice to match the new activity (still overridable).
    setForm((f) => ({ ...f, activity_type: value, transaction_type: defaultTxType(value) }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    const payload: Omit<OperationalLogCreate, 'client_id'> = {
      activity_type: form.activity_type,
      crop: form.crop || undefined,
      description: form.description || undefined,
      quantity: form.quantity ? parseFloat(form.quantity) : undefined,
      unit: form.unit || undefined,
      financial_data: {
        amount: parseFloat(form.amount),
        transaction_type: form.transaction_type,
        category: form.activity_type,
        description: form.description || undefined,
        tax_category: form.tax_category || undefined,
      },
    };

    const result = await saveOperationalLog(payload, isOnline);
    setSaving(false);

    if (result === 'saved') {
      onSaved();
      onClose();
    } else if (result === 'offline') {
      setMessage('Saved offline — will sync when connected.');
      onSaved();
    } else {
      setMessage('Network error — saved offline. Will retry when connected.');
      onSaved();
    }
  };

  const label: CSSProperties = { fontSize: '11px', fontWeight: 600, color: colors.labelText, display: 'block', marginBottom: '4px' };
  const field: CSSProperties = { width: '100%', padding: '8px 10px', borderRadius: '7px', border: `1px solid ${colors.borderInput}`, fontSize: '12px', boxSizing: 'border-box' };

  return (
    <form
      onSubmit={handleSubmit}
      className="fade-in-up"
      style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, padding: '18px', display: 'flex', flexDirection: 'column', gap: '14px' }}
    >
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '14px' }}>
        <div>
          <label style={label}>Activity</label>
          <select value={form.activity_type} onChange={(e) => setActivity(e.target.value as Category)} style={field}>
            {CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
          </select>
        </div>
        <div>
          <label style={label}>Crop</label>
          <select value={form.crop} onChange={(e) => setForm({ ...form, crop: e.target.value })} style={field}>
            <option value="">Unspecified</option>
            {CROPS.map((c) => <option key={c} value={c} style={{ textTransform: 'capitalize' }}>{c[0].toUpperCase() + c.slice(1)}</option>)}
          </select>
        </div>
        <div>
          <label style={label}>Type</label>
          <select value={form.transaction_type} onChange={(e) => setForm({ ...form, transaction_type: e.target.value as TransactionType })} style={field}>
            <option value="debit">Money out (cost)</option>
            <option value="credit">Money in (sale)</option>
          </select>
        </div>
      </div>

      <div>
        <label style={label}>Description</label>
        <input type="text" required placeholder="e.g. Maize harvest — 12 bags" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} style={field} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '14px' }}>
        <div>
          <label style={label}>Quantity</label>
          <input type="number" min="0" step="any" placeholder="0" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} style={field} />
        </div>
        <div>
          <label style={label}>Unit</label>
          <select value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} style={field}>
            <option value="">—</option>
            {UNITS.map((u) => <option key={u} value={u}>{u}</option>)}
          </select>
        </div>
        <div>
          <label style={label}>Amount (₦)</label>
          <input type="number" required min="0" step="0.01" placeholder="0.00" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} style={field} />
        </div>
      </div>

      <div>
        <label style={label}>Tax category <span style={{ color: colors.textFaint, fontWeight: 400 }}>(optional)</span></label>
        <input type="text" placeholder="e.g. Agriculture Inputs" value={form.tax_category} onChange={(e) => setForm({ ...form, tax_category: e.target.value })} style={field} />
      </div>

      {message && <p style={{ fontSize: '11px', color: colors.warn, margin: 0 }}>{message}</p>}

      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
        <button type="button" onClick={onClose} style={{ padding: '8px 14px', borderRadius: '8px', border: `1px solid ${colors.borderInput}`, background: colors.surface, color: colors.textBody, fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}>
          Cancel
        </button>
        <button type="submit" disabled={saving} style={{ display: 'flex', alignItems: 'center', gap: '7px', padding: '8px 16px', borderRadius: '8px', border: 'none', background: colors.primaryDark, color: colors.onPrimary, fontSize: '12px', fontWeight: 600, cursor: saving ? 'default' : 'pointer', opacity: saving ? 0.6 : 1 }}>
          <Save size={15} /> {saving ? 'Saving…' : 'Save record'}
        </button>
      </div>
    </form>
  );
};
