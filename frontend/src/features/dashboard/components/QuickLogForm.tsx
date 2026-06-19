import React, { useState } from 'react';
import { db } from '../../../lib/db';
import { ledgerService } from '../../../lib/apiClient';

interface QuickLogFormProps {
  isOnline: boolean;
  pendingCount: number;
  onSaved: () => void;
}

// Quick capture of an Operational Log (and its paired Financial Transaction).
// Offline-aware: when disconnected (or on a network error) the entry is queued
// in IndexedDB with a client_id idempotency key and synced later.
export const QuickLogForm: React.FC<QuickLogFormProps> = ({ isOnline, pendingCount, onSaved }) => {
  const [form, setForm] = useState({ activity_type: 'yield', item: '', amount: '', date: new Date().toISOString().split('T')[0] });
  const [saveMessage, setSaveMessage] = useState('');

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    const clientId = crypto.randomUUID();
    const payload = {
      activity_type: form.activity_type,
      description: form.item,
      quantity: 1,
      unit: 'unit',
      client_id: clientId,
      financial_data: {
        amount: parseFloat(form.amount),
        transaction_type: form.activity_type === 'yield' ? 'credit' : 'debit',
        category: form.activity_type,
        description: form.item,
      },
    };

    if (!isOnline) {
      await db.pendingLogs.add({ clientId, payload, status: 'pending', failCount: 0, createdAt: Date.now() });
      setForm({ ...form, item: '', amount: '' });
      setSaveMessage('Saved offline — will sync when connected.');
      return;
    }

    try {
      await ledgerService.createLog(payload);
      setForm({ ...form, item: '', amount: '' });
      setSaveMessage('');
      onSaved();
    } catch {
      await db.pendingLogs.add({ clientId, payload, status: 'pending', failCount: 0, createdAt: Date.now() });
      setForm({ ...form, item: '', amount: '' });
      setSaveMessage('Network error — saved offline. Will retry when connected.');
    }
  };

  return (
    <div style={{ background: '#fff', borderRadius: '12px', border: '0.5px solid #e8ede4', padding: '16px', flex: 0 }}>
      <h3 style={{ fontSize: '12px', fontWeight: '700', marginBottom: '16px', color: '#222' }}>QUICK LOG ACTIVITY</h3>
      <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <select value={form.activity_type} onChange={e => setForm({ ...form, activity_type: e.target.value })} style={{ width: '100%', padding: '7px 10px', borderRadius: '7px', border: '1px solid #d0d8c8', fontSize: '12px' }}>
          <option value="yield">Crop Harvest / Sale</option>
          <option value="fertilizer">Fertilizer Application</option>
          <option value="seed">Seed Purchase</option>
          <option value="labour">Labour Payment</option>
        </select>
        <div style={{ display: 'flex', gap: '12px' }}>
          <input type="text" placeholder="Crop/Item" value={form.item} onChange={e => setForm({ ...form, item: e.target.value })} required style={{ flex: 1, padding: '7px 10px', borderRadius: '7px', border: '1px solid #d0d8c8', fontSize: '12px' }} />
          <input type="number" placeholder="Amount (₦)" value={form.amount} onChange={e => setForm({ ...form, amount: e.target.value })} required style={{ width: '100px', padding: '7px 10px', borderRadius: '7px', border: '1px solid #d0d8c8', fontSize: '12px' }} />
        </div>
        <input type="date" value={form.date} onChange={e => setForm({ ...form, date: e.target.value })} style={{ width: '100%', padding: '7px 10px', borderRadius: '7px', border: '1px solid #d0d8c8', fontSize: '12px' }} />
        <button type="submit" style={{ backgroundColor: '#3B6D11', color: '#EAF3DE', padding: '10px', borderRadius: '8px', border: 'none', fontWeight: '500', fontSize: '12px', cursor: 'pointer', marginTop: '4px' }}>SAVE RECORD</button>
        <div style={{ backgroundColor: pendingCount > 0 || !isOnline ? 'rgba(160,92,0,0.08)' : '#f0f7e8', border: `0.5px solid ${pendingCount > 0 || !isOnline ? '#d4a843' : '#c8dfa8'}`, padding: '7px 10px', borderRadius: '8px', marginTop: '8px' }}>
          {saveMessage ? (
            <span style={{ fontSize: '10px', color: '#a05c00' }}>{saveMessage}</span>
          ) : pendingCount > 0 ? (
            <span style={{ fontSize: '10px', color: '#a05c00' }}>⏳ {pendingCount} log{pendingCount > 1 ? 's' : ''} pending sync</span>
          ) : isOnline ? (
            <span style={{ fontSize: '10px', color: '#3B6D11' }}>⚡ Online · all logs synced</span>
          ) : (
            <span style={{ fontSize: '10px', color: '#a05c00' }}>📴 Offline · logs will sync when connected</span>
          )}
        </div>
      </form>
    </div>
  );
};
