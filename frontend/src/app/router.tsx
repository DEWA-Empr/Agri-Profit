import type { FC, ReactNode } from 'react';
import { Routes, Route } from 'react-router-dom';
import {
  LayoutDashboard, ClipboardList, FileText, Tractor,
  BrainCircuit, Users, MessageSquare, MessageCircle
} from 'lucide-react';
import DashboardPage from '../features/dashboard/DashboardPage';

// Single source of truth for navigation. The Sidebar renders from this, and the
// route table below mounts the corresponding pages — so a nav link can never
// point at a route that does not exist. As feature pages land (Phase 4), swap
// their UnderConstruction element for the real page.
export interface NavItemDef {
  label: string;
  to: string;
  icon: ReactNode;
  badge?: string;
}

export interface NavSection {
  heading: string;
  items: NavItemDef[];
}

export const navSections: NavSection[] = [
  {
    heading: 'OVERVIEW',
    items: [
      { label: 'Dashboard', to: '/', icon: <LayoutDashboard size={14} /> },
      { label: 'Farm Records', to: '/records', icon: <ClipboardList size={14} />, badge: '24' },
      { label: 'P&L Report', to: '/reports', icon: <FileText size={14} /> },
    ],
  },
  {
    heading: 'INTELLIGENCE',
    items: [
      { label: 'Equipment', to: '/equipment', icon: <Tractor size={14} /> },
      { label: 'DSS Predict', to: '/dss', icon: <BrainCircuit size={14} /> },
      { label: 'Investors', to: '/investors', icon: <Users size={14} /> },
    ],
  },
  {
    heading: 'ACCESS',
    items: [
      { label: 'USSD/SMS', to: '/ussd', icon: <MessageSquare size={14} /> },
      { label: 'WhatsApp', to: '/whatsapp', icon: <MessageCircle size={14} /> },
    ],
  },
];

const UnderConstruction: FC = () => (
  <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#888', fontWeight: '700', fontStyle: 'italic' }}>
    Module Under Construction
  </div>
);

export const AppRoutes: FC<{ isOnline: boolean; pendingCount: number }> = ({ isOnline, pendingCount }) => (
  <Routes>
    <Route path="/" element={<DashboardPage isOnline={isOnline} pendingCount={pendingCount} />} />
    <Route path="*" element={<UnderConstruction />} />
  </Routes>
);
