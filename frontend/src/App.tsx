import React, { useState, useEffect } from 'react';
import {
  BrowserRouter as Router, Routes, Route, NavLink
} from 'react-router-dom';
import {
  LayoutDashboard, ClipboardList, FileText, Tractor,
  BrainCircuit, Users, MessageSquare, MessageCircle,
  TrendingUp, TrendingDown, Wallet, Clock,
  BarChart3, WifiOff, Plus, Download, Leaf
} from 'lucide-react';
import { liveQuery } from 'dexie';
import { db } from './lib/db';
import { flushPendingLogs, registerSyncListener } from './lib/sync';
import { ledgerService } from './lib/apiClient';
import type { Summary, OperationalLog } from './types/domain';

// --- Components ---

const NavItem: React.FC<{ icon: React.ReactNode, label: string, to: string, badge?: string }> = ({ icon, label, to, badge }) => (
  <NavLink 
    to={to}
    className="nav-item-hover"
    style={({ isActive }) => ({
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '7px 18px',
      fontSize: '12px',
      textDecoration: 'none',
      transition: 'all 0.2s',
      position: 'relative',
      backgroundColor: isActive ? 'rgba(99, 153, 34, 0.12)' : 'transparent',
      color: isActive ? '#C0DD97' : '#4a7a1a',
      fontWeight: isActive ? '700' : '500',
      borderRadius: isActive ? '0 3px 3px 0' : '0',
      borderLeft: isActive ? '3px solid #639922' : '3px solid transparent',
    })}
  >
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      <span style={{ display: 'flex' }}>{icon}</span>
      <span>{label}</span>
    </div>
    {badge && (
      <span style={{
        backgroundColor: 'rgba(99, 153, 34, 0.2)', color: '#97C459', fontSize: '9px', fontWeight: '800',
        padding: '2px 7px', borderRadius: '10px'
      }}>{badge}</span>
    )}
  </NavLink>
);

const MetricCard: React.FC<{ label: string, value: string, trend: string, icon: React.ReactNode, iconBg: string, iconColor: string, trendBg: string, trendColor: string, isRevenue?: boolean }> =
({ label, value, trend, icon, iconBg, iconColor, trendBg, trendColor, isRevenue }) => (
  <div style={{
    backgroundColor: isRevenue ? '#f0f7e8' : '#fff',
    borderRadius: '12px',
    padding: '14px',
    border: isRevenue ? '0.5px solid #c8dfa8' : '0.5px solid #e8ede4',
    display: 'flex',
    flexDirection: 'column',
    flex: 1,
    minHeight: '100px',
  }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{
        width: '32px', height: '32px', borderRadius: '9px', backgroundColor: iconBg,
        display: 'flex', alignItems: 'center', justifyContent: 'center'
      }}>
        <div style={{ color: iconColor, display: 'flex' }}>{React.cloneElement(icon as React.ReactElement<{ size?: number }>, { size: 16 })}</div>
      </div>
      <span style={{
        fontSize: '10px', fontWeight: '700', padding: '3px 8px', borderRadius: '8px',
        backgroundColor: trendBg, color: trendColor
      }}>{trend}</span>
    </div>
    <p style={{ 
      fontSize: '22px', fontWeight: '500', color: isRevenue ? '#27500A' : '#111', 
      marginTop: '12px', letterSpacing: '-0.5px' 
    }}>{value}</p>
    <p style={{ fontSize: '11px', color: '#888', marginTop: '3px' }}>{label}</p>
  </div>
);

// --- Dashboard ---

const Dashboard: React.FC<{ isOnline: boolean; pendingCount: number }> = ({ isOnline, pendingCount }) => {
  const [summary, setSummary] = useState<Summary>({ revenue: 0, expenses: 0, gross_margin: 0 });
  const [logs, setLogs] = useState<OperationalLog[]>([]);
  const [form, setForm] = useState({ activity_type: 'yield', item: '', amount: '', date: new Date().toISOString().split('T')[0] });
  const [saveMessage, setSaveMessage] = useState('');

  const fetchData = async () => {
    try {
      const [sRes, lRes] = await Promise.all([
        ledgerService.getSummary(),
        ledgerService.getLogs(),
      ]);
      setSummary(sRes.data);
      setLogs(lRes.data);
    } catch (err) { console.error(err); }
  };

  useEffect(() => { fetchData(); }, []);

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
      fetchData();
    } catch {
      await db.pendingLogs.add({ clientId, payload, status: 'pending', failCount: 0, createdAt: Date.now() });
      setForm({ ...form, item: '', amount: '' });
      setSaveMessage('Network error — saved offline. Will retry when connected.');
    }
  };

  const placeholders = [
    { dot: '#639922', title: "Maize harvest — 12 bags", meta: "Crop yield · Today", amount: "+₦48,000", isPos: true },
    { dot: '#BA7517', title: "NPK fertilizer — 3 bags", meta: "Input cost · Yesterday", amount: "-₦9,600", isPos: false },
    { dot: '#378ADD', title: "DSS yield forecast", meta: "Prediction · Mon", amount: "View →", isPos: true, customColor: '#378ADD' },
    { dot: '#639922', title: "Tomato sale — 8 crates", meta: "Produce sale · Sun", amount: "+₦32,000", isPos: true }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      
      {/* METRIC GRID */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '11px' }}>
        <MetricCard 
          label="Total Revenue" value={`₦${summary.revenue.toLocaleString()}`} 
          trend="↑ 12%"icon={<TrendingUp />} 
          iconBg="#dff0c4" iconColor="#3B6D11" trendBg="#e8f5d4" trendColor="#3B6D11" isRevenue={true} 
        />
        <MetricCard 
          label="Total Expenses" value={`₦${summary.expenses.toLocaleString()}`} 
          trend="↑ 4%"icon={<TrendingDown />} 
          iconBg="#fde8e8" iconColor="#b33333" trendBg="#fde8e8" trendColor="#b33333"
        />
        <MetricCard 
          label="Gross Margin" value={`₦${summary.gross_margin.toLocaleString()}`} 
          trend="50% rate"icon={<Wallet />} 
          iconBg="#ddeeff" iconColor="#185FA5" trendBg="#e8f5d4" trendColor="#3B6D11"
        />
        <MetricCard 
          label="Total Activities" value={logs.length > 0 ? logs.length.toString() : "24"} 
          trend="+6 this wk"icon={<ClipboardList />} 
          iconBg="#fef3d8" iconColor="#a05c00" trendBg="#fff3e0" trendColor="#a05c00"
        />
      </div>

      <div style={{ display: 'flex', gap: '22px' }}>
        {/* LEFT COLUMN */}
        <div style={{ flex: 1.2, display: 'flex', flexDirection: 'column', gap: '22px' }}>
          
          {/* P&L CHART */}
          <div style={{ background: '#fff', borderRadius: '12px', border: '0.5px solid #e8ede4', padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BarChart3 size={18} color="#639922" />
                <h3 style={{ fontSize: '12px', fontWeight: '600' }}>Monthly P&L overview</h3>
              </div>
              <a href="#" style={{ fontSize: '11px', color: '#639922', fontWeight: '700', textDecoration: 'none' }}>See full report →</a>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'end', justifyContent: 'space-between', height: '112px', padding: '0 10px' }}>
              {[
                { r: 70, e: 45 }, { r: 87, e: 56 }, { r: 62, e: 41 }, 
                { r: 101, e: 64 }, { r: 77, e: 52 }, { r: 112, e: 62 }
              ].map((h, i) => (
                <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
                  <div style={{ display: 'flex', gap: '2px', alignItems: 'end' }}>
                    <div style={{ width: '8px', height: `${h.r}px`, backgroundColor: '#639922', borderRadius: '1px 1px 0 0' }} />
                    <div style={{ width: '8px', height: `${h.e}px`, backgroundColor: '#c0dd97', borderRadius: '1px 1px 0 0' }} />
                  </div>
                  <span style={{ fontSize: '9px', color: '#aaa', marginTop: '10px', fontWeight: '500' }}>{['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'][i]}</span>
                </div>
              ))}
            </div>
            <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', marginTop: '20px' }}>
               <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '10px', color: '#888' }}><div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#639922' }} /> Revenue</div>
               <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '10px', color: '#888' }}><div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#c0dd97' }} /> Expenses</div>
            </div>
          </div>

          {/* RECENT ACTIVITIES */}
          <div style={{ background: '#fff', borderRadius: '12px', border: '0.5px solid #e8ede4', padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '15px' }}>
              <Clock size={18} color="#639922" />
              <h3 style={{ fontSize: '12px', fontWeight: '600' }}>Recent activities</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              {(logs.length > 0 ? logs.slice(0, 4) : placeholders).map((item: any, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '11px', padding: '10px 0', borderBottom: '0.5px solid #f5f5f5' }}>
                  <div style={{ width: '9px', height: '9px', borderRadius: '50%', backgroundColor: item.dot || (item.activity_type === 'yield' ? '#639922' : '#BA7517'), flexShrink: 0 }} />
                  <div>
                    <p style={{ fontSize: '12px', color: '#222' }}>{item.title || item.description}</p>
                    <p style={{ fontSize: '10px', color: '#aaa', marginTop: '1px' }}>{item.meta || `${item.activity_type.toUpperCase()} · Today`}</p>
                  </div>
                  <span style={{ 
                    fontSize: '12px', fontWeight: '500', marginLeft: 'auto', 
                    color: item.customColor || (item.isPos || item.financial_transaction?.transaction_type === 'credit' ? '#3B6D11' : '#c0392b') 
                  }}>
                    {item.amount || (item.financial_transaction ? `${item.financial_transaction.transaction_type === 'credit' ? '+' : '-'}₦${item.financial_transaction.amount.toLocaleString()}` : 'N/A')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN */}
        <div style={{ flex: 0.8, display: 'flex', flexDirection: 'column', gap: '12px' }}>
          
          {/* HEALTH SCORE CARD */}
          <div style={{ background: '#fff', borderRadius: '12px', border: '0.5px solid #e8ede4', padding: '16px', display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 0 }}>
             <div style={{ position: 'relative', width: '96px', height: '96px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <svg width="96" height="96" style={{ transform: 'rotate(-90deg)', overflow: 'visible' }}>
                  <circle cx="48" cy="48" r="40" stroke="#f0f7e8" strokeWidth="9" fill="transparent" />
                  <circle cx="48" cy="48" r="40" stroke="#639922" strokeWidth="9" fill="transparent" strokeDasharray="251" strokeDashoffset="55" strokeLinecap="round" />
                </svg>
                <div style={{ position: 'absolute', textAlign: 'center' }}>
                  <span style={{ fontSize: '24px', fontWeight: '500', color: '#1e3d0a', display: 'block', lineHeight: 1 }}>78</span>
                  <span style={{ fontSize: '9px', color: '#639922', fontWeight: '500' }}>/ 100</span>
                </div>
             </div>
             <p style={{ fontSize: '13px', fontWeight: '500', color: '#27500A', marginTop: '10px' }}>Good standing</p>
             <p style={{ fontSize: '10px', color: '#888', marginTop: '2px' }}>Based on records & profitability</p>
             
             <div style={{ width: '100%', marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
                {[
                  { l: "Profitability", p: 82, c: "#639922" },
                  { l: "Record keeping", p: 75, c: "#97C459" },
                  { l: "Equipment", p: 60, c: "#BA7517" }
                ].map(b => (
                  <div key={b.l}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                      <span style={{ fontSize: '10px', color: '#666', fontWeight: '500' }}>{b.l.toUpperCase()}</span>
                      <span style={{ fontSize: '10px', color: '#666', fontWeight: '500' }}>{b.p}%</span>
                    </div>
                    <div style={{ height: '5px', background: '#f0f0f0', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ width: `${b.p}%`, height: '100%', background: b.c }} />
                    </div>
                  </div>
                ))}
             </div>
          </div>

          {/* QUICK LOG CARD */}
          <div style={{ background: '#fff', borderRadius: '12px', border: '0.5px solid #e8ede4', padding: '16px', flex: 0 }}>
            <h3 style={{ fontSize: '12px', fontWeight: '700', marginBottom: '16px', color: '#222' }}>QUICK LOG ACTIVITY</h3>
            <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <select value={form.activity_type} onChange={e => setForm({...form, activity_type: e.target.value})} style={{ width: '100%', padding: '7px 10px', borderRadius: '7px', border: '1px solid #d0d8c8', fontSize: '12px' }}>
                <option value="yield">Crop Harvest / Sale</option>
                <option value="fertilizer">Fertilizer Application</option>
                <option value="seed">Seed Purchase</option>
                <option value="labour">Labour Payment</option>
              </select>
              <div style={{ display: 'flex', gap: '12px' }}>
                <input type="text" placeholder="Crop/Item" value={form.item} onChange={e => setForm({...form, item: e.target.value})} required style={{ flex: 1, padding: '7px 10px', borderRadius: '7px', border: '1px solid #d0d8c8', fontSize: '12px' }}/>
                <input type="number" placeholder="Amount (₦)" value={form.amount} onChange={e => setForm({...form, amount: e.target.value})} required style={{ width: '100px', padding: '7px 10px', borderRadius: '7px', border: '1px solid #d0d8c8', fontSize: '12px' }}/>
              </div>
              <input type="date" value={form.date} onChange={e => setForm({...form, date: e.target.value})} style={{ width: '100%', padding: '7px 10px', borderRadius: '7px', border: '1px solid #d0d8c8', fontSize: '12px' }} />
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
        </div>
      </div>
    </div>
  );
};

// --- App Shell ---

const App: React.FC = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    const onOnline = () => { setIsOnline(true); flushPendingLogs(); };
    const onOffline = () => setIsOnline(false);
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
    const cleanupSync = registerSyncListener();
    return () => {
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
      cleanupSync();
    };
  }, []);

  useEffect(() => {
    const sub = liveQuery(() =>
      db.pendingLogs.where('status').equals('pending').count()
    ).subscribe({ next: setPendingCount, error: () => {} });
    return () => sub.unsubscribe();
  }, []);

  return (
    <Router>
      <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden', backgroundColor: '#f7f9f4' }}>
        
        {/* SIDEBAR */}
        <aside style={{ width: '220px', backgroundColor: '#0f1f09', display: 'flex', flexDirection: 'column', flexShrink: 0, borderRight: '0.5px solid rgba(99, 153, 34, 0.15)' }}>
          
          {/* Logo Area */}
          <div style={{ padding: '22px 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '38px', height: '38px', backgroundColor: '#639922', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>
                <Leaf size={20} />
              </div>
              <div>
                <h1 style={{ color: '#EAF3DE', fontSize: '15px', fontWeight: '500', lineHeight: 1.1 }}>AgriProfit</h1>
                <p style={{ color: '#3B6D11', fontSize: '9px', fontWeight: '500', letterSpacing: '0.12em', textTransform: 'uppercase', marginTop: '2px' }}>Farm Management</p>
              </div>
            </div>
            
            <div style={{
              marginTop: '20px', display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 11px',
              backgroundColor: 'rgba(99, 153, 34, 0.12)', border: '0.5px solid rgba(99, 153, 34, 0.25)', borderRadius: '20px'
            }}>
              <div style={{ width: '6px', height: '6px', backgroundColor: '#97C459', borderRadius: '50%', boxShadow: '0 0 0 2px rgba(151,196,89,0.25)' }} />
              <span style={{ color: '#97C459', fontSize: '11px', fontWeight: '500' }}>2026 Wet Season</span>
            </div>
          </div>

          {/* Nav */}
          <nav style={{ flex: 1, marginTop: '10px', overflowY: 'auto' }} className="scroll-container">
            <div>
              <p style={{ fontSize: '9px', color: '#2d5010', fontWeight: '800', letterSpacing: '0.1em', padding: '14px 18px 5px' }}>OVERVIEW</p>
              <NavItem icon={<LayoutDashboard size={14}/>} label="Dashboard" to="/" />
              <NavItem icon={<ClipboardList size={14}/>} label="Farm Records" to="/records" badge="24" />
              <NavItem icon={<FileText size={14}/>} label="P&L Report" to="/reports" />
            </div>
            <div>
              <p style={{ fontSize: '9px', color: '#2d5010', fontWeight: '800', letterSpacing: '0.1em', padding: '14px 18px 5px' }}>INTELLIGENCE</p>
              <NavItem icon={<Tractor size={14}/>} label="Equipment" to="/equipment" />
              <NavItem icon={<BrainCircuit size={14}/>} label="DSS Predict" to="/dss" />
              <NavItem icon={<Users size={14}/>} label="Investors" to="/investors" />
            </div>
            <div>
              <p style={{ fontSize: '9px', color: '#2d5010', fontWeight: '800', letterSpacing: '0.1em', padding: '14px 18px 5px' }}>ACCESS</p>
              <NavItem icon={<MessageSquare size={14}/>} label="USSD/SMS" to="/ussd" />
              <NavItem icon={<MessageCircle size={14}/>} label="WhatsApp" to="/whatsapp" />
            </div>
          </nav>

          {/* Sync status */}
          {(!isOnline || pendingCount > 0) && (
            <div style={{ padding: '10px 18px', borderTop: '0.5px solid rgba(99,153,34,0.12)', display: 'flex', flexDirection: 'column', gap: '5px' }}>
              {!isOnline && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '5px 8px', backgroundColor: 'rgba(160,92,0,0.15)', borderRadius: '6px' }}>
                  <WifiOff size={11} color="#BA7517" />
                  <span style={{ color: '#BA7517', fontSize: '10px', fontWeight: '600' }}>Offline</span>
                </div>
              )}
              {pendingCount > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '5px 8px', backgroundColor: 'rgba(160,92,0,0.1)', borderRadius: '6px' }}>
                  <span style={{ color: '#BA7517', fontSize: '10px' }}>⏳ {pendingCount} pending sync</span>
                </div>
              )}
            </div>
          )}

          {/* Profile */}
          <div style={{ padding: '18px', borderTop: '0.5px solid rgba(99, 153, 34, 0.12)', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: '#1e3d0a', border: '1.5px solid #3B6D11', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#97C459', fontWeight: '800', fontSize: '11px' }}>AD</div>
            <div>
              <p style={{ color: '#97C459', fontSize: '12px', fontWeight: '500' }}>Abubakar D.</p>
              <p style={{ color: '#3B6D11', fontSize: '10px' }}>Farm Owner</p>
            </div>
          </div>
        </aside>

        {/* MAIN AREA */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          
          <header style={{ height: '60px', background: '#fff', borderBottom: '0.5px solid #e8ede4', padding: '15px 22px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
            <div>
              <h2 style={{ fontSize: '17px', fontWeight: '500', color: '#111', letterSpacing: '-0.3px' }}>Farm Overview</h2>
              <p style={{ fontSize: '11px', color: '#888', marginTop: '2px' }}>Tuesday, 16 June 2026 • Currency in NGN (₦)</p>
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button style={{ padding: '7px 14px', border: '0.5px solid #d0d8c8', borderRadius: '8px', backgroundColor: '#fff', color: '#444', fontSize: '12px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                <Download size={14} /> Export
              </button>
              <button style={{ padding: '7px 14px', background: '#3B6D11', color: '#EAF3DE', borderRadius: '8px', fontSize: '12px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', border: 'none' }}>
                <Plus size={14} /> Log Activity
              </button>
            </div>
          </header>

          <main style={{ flex: 1, padding: '22px', overflowY: 'auto' }} className="scroll-container">
            <Routes>
              <Route path="/" element={<Dashboard isOnline={isOnline} pendingCount={pendingCount} />} />
              <Route path="*" element={<div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#888', fontWeight: '700', fontStyle: 'italic' }}>Module Under Construction</div>} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
};

export default App;
