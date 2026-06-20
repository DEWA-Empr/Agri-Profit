import { useEffect, useState, type CSSProperties, type FormEvent } from 'react';
import { X, Wrench, Plus, Calendar } from 'lucide-react';
import { equipmentService } from '../../../lib/apiClient';
import type { Equipment, MaintenanceLog } from '../../../types/domain';
import { colors } from '../../../styles/theme';

const naira = (n: number) => `₦${n.toLocaleString()}`;

// Modal panel for a single piece of equipment: shows its maintenance history
// (GET /equipment/{id}/maintenance) and a form to log a new service record
// (POST /equipment/maintenance). Refreshes the list after each save.
export const MaintenancePanel = ({ equipment, onClose }: { equipment: Equipment; onClose: () => void }) => {
  const [logs, setLogs] = useState<MaintenanceLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ description: '', cost: '' });

  useEffect(() => {
    let active = true;
    setLoading(true);
    equipmentService.getMaintenance(equipment.id)
      .then((res) => { if (active) setLogs(res.data); })
      .catch(() => { if (active) setError('Could not load maintenance history.'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [equipment.id]);

  const refresh = () => {
    equipmentService.getMaintenance(equipment.id)
      .then((res) => setLogs(res.data))
      .catch(() => setError('Could not load maintenance history.'));
  };

  const handleAdd = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await equipmentService.createMaintenance({
        equipment_id: equipment.id,
        description: form.description,
        cost: form.cost ? parseFloat(form.cost) : undefined,
      });
      setForm({ description: '', cost: '' });
      refresh();
    } catch {
      setError('Could not save the maintenance log.');
    } finally {
      setSaving(false);
    }
  };

  const totalCost = logs.reduce((sum, l) => sum + (l.cost || 0), 0);

  const input: CSSProperties = { width: '100%', padding: '8px 10px', borderRadius: '7px', border: `1px solid ${colors.borderInput}`, fontSize: '12px' };

  return (
    <div
      onClick={onClose}
      style={{ position: 'fixed', inset: 0, backgroundColor: 'transparent', display: 'flex', justifyContent: 'flex-end', zIndex: 50 }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="drawer-panel"
        style={{ width: '420px', maxWidth: '90vw', height: '100%', background: colors.surface, borderLeft: `1px solid ${colors.border}`, display: 'flex', flexDirection: 'column', overflow: 'hidden', boxShadow: '-24px 0 60px -12px rgba(15,31,9,0.28)' }}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', padding: '18px 20px', borderBottom: `0.5px solid ${colors.border}` }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ background: colors.primarySurface, padding: '9px', borderRadius: '9px' }}><Wrench size={18} color={colors.primary} /></div>
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: 700, color: colors.textStrong }}>{equipment.name}</h3>
              <p style={{ fontSize: '11px', color: colors.textMuted, marginTop: '1px' }}>Maintenance history{logs.length > 0 ? ` · ${naira(totalCost)} total` : ''}</p>
            </div>
          </div>
          <button onClick={onClose} aria-label="Close" style={{ background: 'none', border: 'none', cursor: 'pointer', color: colors.textMuted, padding: '2px', display: 'flex' }}>
            <X size={18} />
          </button>
        </div>

        {/* History */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px' }} className="scroll-container">
          {loading ? (
            <p style={{ fontSize: '12px', color: colors.textMuted }}>Loading history…</p>
          ) : logs.length === 0 ? (
            <div style={{ padding: '28px', textAlign: 'center', background: colors.surfaceMuted, borderRadius: '10px', border: `1px dashed ${colors.border}` }}>
              <p style={{ fontSize: '12px', color: colors.textMuted }}>No maintenance logged yet for this machine.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {logs.map((log) => (
                <div key={log.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px', padding: '11px 13px', background: colors.surfaceMuted, borderRadius: '9px', border: `0.5px solid ${colors.border}` }}>
                  <div>
                    <p style={{ fontSize: '12px', color: colors.textBody, fontWeight: 500 }}>{log.description || 'Service'}</p>
                    <p style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '10px', color: colors.textMuted, marginTop: '3px' }}>
                      <Calendar size={11} /> {new Date(log.service_date).toLocaleDateString()}
                    </p>
                  </div>
                  <span style={{ fontSize: '12px', fontWeight: 700, color: colors.danger, whiteSpace: 'nowrap' }}>
                    {log.cost != null ? `-${naira(log.cost)}` : '—'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Add form */}
        <form onSubmit={handleAdd} style={{ borderTop: `0.5px solid ${colors.border}`, padding: '14px 20px', display: 'flex', flexDirection: 'column', gap: '10px', background: colors.surface }}>
          {error && <p style={{ fontSize: '11px', color: colors.danger }}>{error}</p>}
          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type="text" placeholder="What was serviced?" required
              value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
              style={{ ...input, flex: 1 }}
            />
            <input
              type="number" placeholder="Cost (₦)" min="0" step="0.01"
              value={form.cost} onChange={(e) => setForm({ ...form, cost: e.target.value })}
              style={{ ...input, width: '120px' }}
            />
          </div>
          <button
            type="submit" disabled={saving}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '7px', background: colors.primaryDark, color: colors.onPrimary, padding: '9px', borderRadius: '8px', border: 'none', fontSize: '12px', fontWeight: 600, cursor: saving ? 'default' : 'pointer', opacity: saving ? 0.6 : 1 }}
          >
            <Plus size={15} /> {saving ? 'Saving…' : 'Log maintenance'}
          </button>
        </form>
      </div>
    </div>
  );
};
