import React from 'react';
import {
  BrowserRouter as Router, Routes, Route, NavLink
} from 'react-router-dom';
import {
  LayoutDashboard, ClipboardList, FileText, Tractor,
  BrainCircuit, Users, MessageSquare, MessageCircle,
  WifiOff, Plus, Download, Leaf
} from 'lucide-react';
import { useOnlineStatus } from './hooks/useOnlineStatus';
import { usePendingSync } from './hooks/usePendingSync';
import DashboardPage from './features/dashboard/DashboardPage';

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

// --- App Shell ---

const App: React.FC = () => {
  const isOnline = useOnlineStatus();
  const pendingCount = usePendingSync();

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
              <Route path="/" element={<DashboardPage isOnline={isOnline} pendingCount={pendingCount} />} />
              <Route path="*" element={<div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#888', fontWeight: '700', fontStyle: 'italic' }}>Module Under Construction</div>} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
};

export default App;
