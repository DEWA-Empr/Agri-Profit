import { useEffect, useState, type CSSProperties, type FormEvent } from 'react';
import { Tractor, Plus, Wrench, Calendar, Hash } from 'lucide-react';
import { equipmentService } from '../../lib/apiClient';
import type { Equipment } from '../../types/domain';
import { colors } from '../../styles/theme';
import { MaintenancePanel } from './components/MaintenancePanel';

// Salvaged from the original pages/Equipment.tsx (logic preserved, restyled to
// the app's inline-style standard since Tailwind is not compiled).
const EquipmentPage = () => {
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newEq, setNewEq] = useState({ name: '', model: '', purchase_price: 0, depreciation_rate: 10 });
  const [maintenanceFor, setMaintenanceFor] = useState<Equipment | null>(null);

  const fetchEquipment = () => {
    equipmentService.getEquipment()
      .then((res) => setEquipment(res.data))
      .catch((err) => console.error('Error fetching equipment:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchEquipment(); }, []);

  const handleAddEquipment = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await equipmentService.createEquipment(newEq);
      setShowAddForm(false);
      setNewEq({ name: '', model: '', purchase_price: 0, depreciation_rate: 10 });
      fetchEquipment();
    } catch (err) {
      console.error('Error adding equipment:', err);
    }
  };

  const input: CSSProperties = { width: '100%', padding: '7px 10px', borderRadius: '7px', border: `1px solid ${colors.borderInput}`, fontSize: '12px', marginTop: '4px' };
  const label: CSSProperties = { fontSize: '11px', fontWeight: 600, color: colors.labelText };

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
        <form onSubmit={handleAddEquipment} className="fade-in-up" style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, padding: '18px', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px', alignItems: 'end' }}>
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
            <input type="number" value={newEq.purchase_price} onChange={(e) => setNewEq({ ...newEq, purchase_price: parseFloat(e.target.value) })} style={input} />
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
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
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
                  <Hash size={13} /> {item.depreciation_rate ?? '—'}% Dep.
                </div>
              </div>
              <button
                onClick={() => setMaintenanceFor(item)}
                style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'none', border: 'none', color: colors.primary, fontSize: '12px', fontWeight: 600, cursor: 'pointer', padding: 0 }}
              >
                <Wrench size={14} /> Maintenance
              </button>
            </div>
          ))}
        </div>
      )}

      {maintenanceFor && (
        <MaintenancePanel equipment={maintenanceFor} onClose={() => setMaintenanceFor(null)} />
      )}
    </div>
  );
};

export default EquipmentPage;
