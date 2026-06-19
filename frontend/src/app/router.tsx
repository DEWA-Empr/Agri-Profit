import type { FC, ReactNode } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import {
  LayoutDashboard, ClipboardList, FileText, Tractor,
  BrainCircuit, Users, MessageSquare, MessageCircle
} from 'lucide-react';
import DashboardPage from '../features/dashboard/DashboardPage';
import FarmRecordsPage from '../features/farm-records/FarmRecordsPage';
import ReportsPage from '../features/reports/ReportsPage';
import EquipmentPage from '../features/equipment/EquipmentPage';
import DSSPredictPage from '../features/dss/DSSPredictPage';
import InvestorsPage from '../features/investors/InvestorsPage';
import UssdPage from '../features/messaging/UssdPage';
import WhatsappPage from '../features/messaging/WhatsappPage';

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

export const AppRoutes: FC<{ isOnline: boolean; pendingCount: number }> = ({ isOnline, pendingCount }) => (
  <Routes>
    <Route path="/" element={<DashboardPage isOnline={isOnline} pendingCount={pendingCount} />} />
    <Route path="/records" element={<FarmRecordsPage />} />
    <Route path="/reports" element={<ReportsPage />} />
    <Route path="/equipment" element={<EquipmentPage />} />
    <Route path="/dss" element={<DSSPredictPage />} />
    <Route path="/investors" element={<InvestorsPage />} />
    <Route path="/ussd" element={<UssdPage />} />
    <Route path="/whatsapp" element={<WhatsappPage />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);
