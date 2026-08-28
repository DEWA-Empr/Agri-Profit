import { useEffect, useState, type CSSProperties, type FormEvent } from 'react';
import { Tractor, Plus, Wrench, Calendar, Hash, Pencil } from 'lucide-react';
import { equipmentService } from '../../lib/apiClient';
import { purgeApiReadCache } from '../../lib/apiCache';
import type { Equipment, EquipmentCreate, EquipmentUpdate } from '../../types/domain';
import { colors } from '../../styles/theme';
import { MaintenancePanel } from './components/MaintenancePanel';
import { NoAccess } from '../../components/NoAccess';
import { isForbidden } from '../../lib/accessError';

// Salvaged from the original pages/Equipment.tsx (logic preserved, restyled to
// the app's inline-style standard since Tailwind is not compiled).
const EquipmentPage = () => {
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  // Optional numbers are held as STRINGS so that "left blank" survives to the
  // payload as absent. There is no default depreciation rate: an asset entered
  // without one carries null and is excluded from — and counted in — the
  // depreciation overlay, rather than being charged at a rate nobody chose.
  const emptyForm = { name: '', model: '', purchase_date: '', purchase_price: '', depreciation_rate: '' };
  const [newEq, setNewEq] = useState(emptyForm);
  const [maintenanceFor, setMaintenanceFor] = useState<Equipment | null>(null);
  // Which asset is being corrected, and the draft values. A mistyped
  // depreciation rate used to be permanent, and it silently biases the
  // depreciation overlay, allocated fixed cost and both break-even prices.
  const [editing, setEditing] = useState<Equipment | null>(null);
  const [editDraft, setEditDraft] = useState({ purchase_price: '', depreciation_rate: '' });
  const [editError, setEditError] = useState('');
  const [denied, setDenied] = useState(false);

  const startEdit = (item: Equipment) => {
    setEditError('');
    setEditDraft({
      purchase_price: item.purchase_price != null ? String(item.purchase_price) : '',
      depreciation_rate: item.depreciation_rate != null ? String(item.depreciation_rate) : '',
    });
    setEditing(item);
  };

  const saveEdit = async () => {
    if (!editing) return;
    // Only send what the farmer actually changed. The PATCH is partial, so an
    // omitted field is left alone — sending every field would overwrite values
    // that were never in question.
    const changes: EquipmentUpdate = {};
    const price = editDraft.purchase_price.trim();
    const rate = editDraft.depreciation_rate.trim();

    if (price !== '' && Number(price) !== editing.purchase_price) {
      if (!Number.isFinite(Number(price)) || Number(price) < 0) {
        setEditError('Purchase price must be a number and cannot be negative.');
        return;
      }
      changes.purchase_price = Number(price);
    }
    if (rate !== '' && Number(rate) !== editing.depreciation_rate) {
      const value = Number(rate);
      // 0 is refused rather than stored: in the overlay it is indistinguishable
      // from "unrated", and an unrated asset is counted, never charged at zero.
      if (!Number.isFinite(value) || value <= 0 || value > 100) {
        setEditError('Depreciation rate must be between 0 and 100 percent per year.');
        return;
      }
      changes.depreciation_rate = value;
    }
    if (Object.keys(changes).length === 0) {
      setEditing(null);
      return;
    }

    try {
      await equipmentService.updateEquipment(editing.id, changes);
      setEditing(null);
      fetchEquipment();
    } catch {
      setEditError('Could not save the correction. Check the values and try again.');
    }
  };

  const fetchEquipment = () => {
    equipmentService.getEquipment()
      .then((res) => setEquipment(res.data))
      .catch((err) => {
        if (isForbidden(err)) setDenied(true);
        else console.error('Error fetching equipment:', err);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchEquipment(); }, []);

  const handleAddEquipment = async (e: FormEvent) => {
    e.preventDefault();
    // A blank optional field is omitted, not sent as 0. Zero is a real value the
    // API rejects for a rate, and a zero purchase price would understate the
    // overlay silently.
    const payload: EquipmentCreate = { name: newEq.name };
    if (newEq.model) payload.model = newEq.model;
    if (newEq.purchase_date) payload.purchase_date = newEq.purchase_date;
    if (newEq.purchase_price !== '') payload.purchase_price = parseFloat(newEq.purchase_price);
    if (newEq.depreciation_rate !== '') payload.depreciation_rate = parseFloat(newEq.depreciation_rate);
    try {
      await equipmentService.createEquipment(payload);
      // A new asset changes the depreciation overlay on the DSS reads — the
      // allocated fixed cost, the break-even price to cover total cost, and the
      // "N of your M assets have no depreciation rate recorded" qualification
      // that travels with it. Those reads are cached StaleWhileRevalidate, so
      // without this the panel would keep reading the pre-creation counts.
      // Equipment does not post through ledgerService.createLog, so it gets no
      // purge from there.
      await purgeApiReadCache();
      setShowAddForm(false);
      setNewEq(emptyForm);
      fetchEquipment();
    } catch (err) {
      console.error('Error adding equipment:', err);
    }
  };

  const input: CSSProperties = { width: '100%', padding: '7px 10px', borderRadius: '7px', border: `1px solid ${colors.borderInput}`, fontSize: '12px', marginTop: '4px' };
  const label: CSSProperties = { fontSize: '11px', fontWeight: 600, color: colors.labelText };


  // Reached only if equipment:read is withdrawn mid-session; the route guard
  // redirects a role without it before this page mounts.
  if (denied) {
    return <NoAccess what="the farm's equipment register" />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          style={{ display: 'flex', alignItems: 'center', gap: '8px', background: colors.primaryDark, color: colors.onPrimary, padding: '8px 14px', borderRadius: '8px', border: 'none', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
        >
          <Plus size={16} /> Add Equipment
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleAddEquipment} className="fade-in-up grid-4" style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, padding: '18px', alignItems: 'end' }}>
          <div>
            <label style={label}>Name</label>
            <input type="text" required value={newEq.name} onChange={(e) => setNewEq({ ...newEq, name: e.target.value })} style={input} />
          </div>
          <div>
            <label style={label}>Model / Year</label>
            <input type="text" value={newEq.model} onChange={(e) => setNewEq({ ...newEq, model: e.target.value })} style={input} />
          </div>
          <div>
            <label style={label}>Price (₦)</label>
            <input type="number" min="0" step="any" value={newEq.purchase_price} onChange={(e) => setNewEq({ ...newEq, purchase_price: e.target.value })} style={input} />
          </div>
          <div>
            <label style={label}>Purchase date</label>
            <input type="date" value={newEq.purchase_date} onChange={(e) => setNewEq({ ...newEq, purchase_date: e.target.value })} style={input} />
          </div>
          <div>
            {/* Unit in the label, and NO pre-filled value: a rate the farmer did
                not choose would be charged against them as though they had. */}
            <label style={label}>Depreciation rate (%/yr)</label>
            <input
              type="number"
              min="0"
              max="100"
              step="any"
              placeholder="e.g. 10"
              value={newEq.depreciation_rate}
              onChange={(e) => setNewEq({ ...newEq, depreciation_rate: e.target.value })}
              style={input}
            />
            <p style={{ fontSize: '10px', color: colors.textMuted, marginTop: '3px' }}>
              Optional. Left blank, this asset is excluded from the depreciation overlay.
            </p>
          </div>
          <button type="submit" style={{ background: colors.primaryDark, color: colors.onPrimary, padding: '9px', borderRadius: '8px', border: 'none', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}>Save</button>
        </form>
      )}

      {loading ? (
        <p style={{ fontSize: '12px', color: colors.textMuted }}>Loading equipment…</p>
      ) : equipment.length === 0 ? (
        <div style={{ padding: '48px', textAlign: 'center', background: colors.surfaceMuted, borderRadius: '12px', border: '2px dashed #e0e6d8' }}>
          <Tractor size={40} color="#cdd6c0" style={{ marginBottom: '12px' }} />
          <p style={{ fontSize: '12px', color: colors.textMuted, fontWeight: 500 }}>No equipment yet. Add your first machine.</p>
        </div>
      ) : (
        <div className="grid-3" style={{ gap: '16px' }}>
          {equipment.map((item) => (
            <div key={item.id} className="card-interactive" style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, padding: '18px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ background: colors.primarySurface, padding: '10px', borderRadius: '9px' }}><Tractor size={20} color={colors.primary} /></div>
                <span style={{ fontSize: '10px', fontWeight: 700, background: colors.divider, color: colors.textMuted, padding: '2px 8px', borderRadius: '6px' }}>ID: {item.id}</span>
              </div>
              <div>
                <h3 style={{ fontSize: '14px', fontWeight: 700, color: colors.text }}>{item.name}</h3>
                <p style={{ fontSize: '11px', color: colors.textMuted }}>{item.model || 'No model info'}</p>
              </div>
              <div style={{ display: 'flex', gap: '14px', borderTop: `0.5px solid ${colors.divider}`, borderBottom: `0.5px solid ${colors.divider}`, padding: '10px 0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: '#666' }}>
                  <Calendar size={13} /> ₦{item.purchase_price?.toLocaleString() ?? '—'}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: '#666' }}>
                  {/* "Dep. rate", not "Dep.": this is the rate as entered, not
                      a depreciation figure. Nothing in the system computes
                      accumulated depreciation or a book value. */}
                  <Hash size={13} /> Dep. rate {item.depreciation_rate ?? '—'}%/yr
                </div>
              </div>
              {item.updated_at && (
                <p style={{ fontSize: '10px', color: colors.textMuted }}>
                  Corrected {new Date(item.updated_at).toLocaleDateString()}
                </p>
              )}

              {editing?.id === item.id ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <label style={label}>
                    Purchase price (₦)
                    <input style={input} inputMode="decimal" value={editDraft.purchase_price}
                      onChange={(e) => setEditDraft({ ...editDraft, purchase_price: e.target.value })} />
                  </label>
                  <label style={label}>
                    Depreciation rate (%/yr)
                    <input style={input} inputMode="decimal" value={editDraft.depreciation_rate}
                      onChange={(e) => setEditDraft({ ...editDraft, depreciation_rate: e.target.value })} />
                  </label>
                  {editError && <p style={{ fontSize: '11px', color: colors.dangerStrong }}>{editError}</p>}
                  <p style={{ fontSize: '10px', color: colors.textMuted }}>
                    Changing these moves your break-even prices.
                  </p>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button onClick={saveEdit} style={{ flex: 1, padding: '7px', borderRadius: '7px', border: 'none', background: colors.primary, color: colors.surface, fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}>Save</button>
                    <button onClick={() => setEditing(null)} style={{ flex: 1, padding: '7px', borderRadius: '7px', border: `1px solid ${colors.borderInput}`, background: 'none', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}>Cancel</button>
                  </div>
                </div>
              ) : (
                <div style={{ display: 'flex', gap: '16px' }}>
                  <button
                    onClick={() => setMaintenanceFor(item)}
                    style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'none', border: 'none', color: colors.primary, fontSize: '12px', fontWeight: 600, cursor: 'pointer', padding: 0 }}
                  >
                    <Wrench size={14} /> Maintenance
                  </button>
                  <button
                    onClick={() => startEdit(item)}
                    style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'none', border: 'none', color: colors.textMuted, fontSize: '12px', fontWeight: 600, cursor: 'pointer', padding: 0 }}
                  >
                    <Pencil size={14} /> Correct
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {maintenanceFor && (
        <MaintenancePanel key={maintenanceFor.id} equipment={maintenanceFor} onClose={() => setMaintenanceFor(null)} />
      )}
    </div>
  );
};

export default EquipmentPage;
