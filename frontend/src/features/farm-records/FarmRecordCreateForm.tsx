import { useState, type CSSProperties, type FormEvent } from 'react';
import { Save } from 'lucide-react';
import type { Category, TransactionType, OperationalLogCreate } from '../../types/domain';
import { saveOperationalLog } from '../../lib/logs';
import { useCropOptions } from './useCropOptions';
import { validateRecord } from './recordBounds';
import { normaliseCrop } from './cropOptions';
import { colors } from '../../styles/theme';
import { DryingFields } from './DryingFields';
import { buildDryingParams, emptyDryingForm, type DryingForm } from './dryingParams';
import { DryingRunResult } from './DryingRunResult';

// "Post-harvest drying" (bioprocess) is only safe to offer alongside the
// drying-parameter fields: the backend rejects a bioprocess log whose
// extra_data is not a valid DryingParams payload (schemas.OperationalLogCreate
// ._validate_bioprocess_payload), and saveOperationalLog cannot tell that 422
// from a network failure — it would queue the record in IndexedDB, where it
// would re-fail on every flush until its retries ran out. So the option and
// the fields ship together, with the payload validated client-side before it
// can ever reach the queue (see DryingFields.buildDryingParams).
const CATEGORIES: { value: Category; label: string }[] = [
  { value: 'yield', label: 'Crop yield / sale' },
  { value: 'seed', label: 'Seed' },
  { value: 'fertilizer', label: 'Fertilizer' },
  { value: 'labour', label: 'Labour' },
  { value: 'mechanization', label: 'Mechanization' },
  { value: 'bioprocess', label: 'Post-harvest drying' },
  { value: 'other', label: 'Other' },
];

// The crop list is no longer a literal here: it is assembled from the farm's own
// recorded crops and the predictor's, at runtime. See ./cropOptions for why, and
// for the cowpea/tomato drift the literal caused.
const OTHER_CROP = '__other__';

// Harvest units, fixed rather than free text. Yield totals are grouped by unit
// on the backend, and free text meant "kg", "Kg" and "kilos" became three
// different units for the same thing — with the per-crop total silently
// unavailable as a result. Existing records keep whatever text they were saved
// with; only new entries are constrained.
const UNITS = ['kg', 'tonnes', 'bags', 'crates'];

// Mechanisation cost classification. Mirrors the backend's Literal on
// MechanizationParams.cost_subtype (schemas.py) — these five strings are the
// keys COST_BEHAVIOUR is looked up by, so each one decides whether the row's
// money lands in the variable, semi-variable or fixed bucket, and therefore
// every cost-structure, break-even and sensitivity figure downstream.
//
// Without this control the form sent no extra_data at all on a mechanisation
// log, so cost_behaviour_for missed the lookup and EVERY mechanisation cost
// entered through the app landed in the unclassified pile — a ledger entered
// entirely through the UI reported 0% classification coverage.
//
// OPTIONAL, deliberately: the backend accepts a mechanisation log with no
// extra_data (it is what every legacy row looks like), so leaving this unset
// must stay legal. See the guard in handleSubmit.
//
// equipment_id and hours_used are NOT offered. They are capture-only fields
// with no consumer, settled in docs/adr/0003 — adding UI for them would widen
// the form without moving any figure.
const COST_SUBTYPES: { value: string; label: string }[] = [
  { value: 'FUEL', label: 'Fuel' },
  { value: 'LUBRICANTS', label: 'Lubricants' },
  { value: 'REPAIRS', label: 'Repairs' },
  { value: 'MACHINERY_HIRE', label: 'Machinery hire' },
  { value: 'DEPRECIATION', label: 'Depreciation' },
];

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
    cost_subtype: '',
  });
  const [drying, setDrying] = useState<DryingForm>(emptyDryingForm);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  // Set once a drying run has been written to the server: the form is replaced
  // by its computed metrics rather than closing silently, because the numbers
  // that matter (water removed, process loss, safe-storage verdict) only exist
  // after the backend has seen the run.
  const [savedDryingId, setSavedDryingId] = useState<number | null>(null);
  // Crops come from the API, not a literal (see ./cropOptions). `otherCrop`
  // holds a name being typed for a crop the farm has not recorded before —
  // without it, a farmer taking up a new crop this season could not file a
  // record against it at all.
  const [otherCrop, setOtherCrop] = useState('');
  const { crops: cropOptions, loading: cropsLoading } = useCropOptions();

  const isDrying = form.activity_type === 'bioprocess';
  const isMechanization = form.activity_type === 'mechanization';
  const isOtherCrop = form.crop === OTHER_CROP;
  // Normalised at the edge so "Maize", " maize" and "maize" are one crop. Crop
  // grouping in the DSS is an exact string match on this column.
  const resolvedCrop = isOtherCrop ? normaliseCrop(otherCrop) : form.crop;

  const setActivity = (value: Category) =>
    // Re-default the debit/credit choice to match the new activity (still overridable).
    // The cost subtype is dropped whenever the activity moves away from
    // mechanisation: it classifies a mechanisation cost and means nothing on a
    // seed or labour row, so a stale value must not survive the switch and ride
    // along in extra_data.
    setForm((f) => ({
      ...f,
      activity_type: value,
      transaction_type: defaultTxType(value),
      cost_subtype: value === 'mechanization' ? f.cost_subtype : '',
    }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Validate BEFORE anything is queued: an invalid record is a permanent 422,
    // and a permanent 422 in the offline queue is a record that can never sync —
    // it retries three times and is stranded. Money and quantity are checked
    // first because they are on every record; the drying payload follows.
    const boundsError = validateRecord({ amount: form.amount, quantity: form.quantity });
    if (boundsError) {
      setMessage(boundsError);
      return;
    }

    let extraData: Record<string, unknown> | undefined;
    if (isDrying) {
      const built = buildDryingParams(drying);
      if ('error' in built) {
        setMessage(built.error);
        return;
      }
      extraData = { ...built.params };
    } else if (isMechanization && form.cost_subtype) {
      // THE `form.cost_subtype` GUARD IS LOAD-BEARING. MechanizationParams
      // requires cost_subtype, so `{cost_subtype: ''}` is a 422 — and
      // saveOperationalLog cannot tell a 422 from a network failure, so it
      // would queue the record in IndexedDB where it would re-fail on every
      // flush until its retries ran out (the same trap documented above the
      // CATEGORIES list). An unset subtype must send NO extra_data at all,
      // which the backend accepts and classifies as None.
      extraData = { cost_subtype: form.cost_subtype };
    }

    setSaving(true);
    setMessage('');

    const payload: Omit<OperationalLogCreate, 'client_id'> = {
      activity_type: form.activity_type,
      crop: resolvedCrop || undefined,
      description: form.description || undefined,
      quantity: form.quantity ? parseFloat(form.quantity) : undefined,
      unit: form.unit || undefined,
      extra_data: extraData,
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

    if (result.status === 'saved') {
      onSaved();
      if (isDrying) {
        setSavedDryingId(result.log.id);
      } else {
        onClose();
      }
    } else if (result.status === 'offline') {
      setMessage(isDrying
        ? 'Saved offline — drying metrics will be available once it syncs.'
        : 'Saved offline — will sync when connected.');
      onSaved();
    } else if (result.status === 'unauthenticated') {
      // Nothing was queued: an offline record has to name the account that
      // captured it (lib/queueOwner), and there is no signed-in account to name.
      setMessage('Your session has ended. Sign in again, then re-enter this record.');
    } else {
      setMessage('Network error — saved offline. Will retry when connected.');
      onSaved();
    }
  };

  const label: CSSProperties = { fontSize: '11px', fontWeight: 600, color: colors.labelText, display: 'block', marginBottom: '4px' };
  const field: CSSProperties = { width: '100%', padding: '8px 10px', borderRadius: '7px', border: `1px solid ${colors.borderInput}`, fontSize: '12px', boxSizing: 'border-box' };

  if (savedDryingId !== null) {
    return <DryingRunResult logId={savedDryingId} onDone={onClose} />;
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="fade-in-up"
      style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, padding: '18px', display: 'flex', flexDirection: 'column', gap: '14px' }}
    >
      <div className="grid-3">
        <div>
          <label style={label}>Activity</label>
          <select value={form.activity_type} onChange={(e) => setActivity(e.target.value as Category)} style={field}>
            {CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
          </select>
        </div>
        <div>
          <label style={label}>Crop</label>
          <select value={form.crop} onChange={(e) => setForm({ ...form, crop: e.target.value })} style={field}>
            <option value="">{cropsLoading ? 'Loading crops…' : 'Unspecified'}</option>
            {cropOptions.map((c) => (
              <option key={c} value={c} style={{ textTransform: 'capitalize' }}>{c[0].toUpperCase() + c.slice(1)}</option>
            ))}
            <option value={OTHER_CROP}>Another crop…</option>
          </select>
          {isOtherCrop && (
            <input
              type="text"
              placeholder="Crop name, e.g. groundnut"
              value={otherCrop}
              onChange={(e) => setOtherCrop(e.target.value)}
              aria-label="New crop name"
              style={{ ...field, marginTop: '6px' }}
            />
          )}
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

      <div className="grid-3">
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
          {/* A sun-dried lot with the farm's own labour genuinely costs ₦0, and
              0 is accepted: every operational log keeps its paired transaction,
              so the pairing invariant holds even for a free process. */}
          <label style={label}>Amount (₦){isDrying && <span style={{ color: colors.textFaint, fontWeight: 400 }}> — 0 is fine for sun drying</span>}</label>
          <input type="number" required min="0" step="0.01" placeholder="0.00" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} style={field} />
        </div>
      </div>

      {isDrying && <DryingFields value={drying} onChange={setDrying} label={label} field={field} />}

      {isMechanization && (
        <div>
          <label style={label}>
            Cost type <span style={{ color: colors.textFaint, fontWeight: 400 }}>(optional — classifies this cost)</span>
          </label>
          <select value={form.cost_subtype} onChange={(e) => setForm({ ...form, cost_subtype: e.target.value })} style={field}>
            <option value="">Not classified</option>
            {COST_SUBTYPES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
          </select>
          <p style={{ fontSize: '10.5px', color: colors.textFaint, margin: '4px 0 0' }}>
            Classifying a mechanisation cost puts it in the right bucket on your cost structure and break-even price. Left unset, it is reported as unclassified.
          </p>
        </div>
      )}

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
