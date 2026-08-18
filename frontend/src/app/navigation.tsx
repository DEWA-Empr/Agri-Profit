import type { ReactNode } from 'react';
import {
  LayoutDashboard, ClipboardList, FileText, Tractor,
  BrainCircuit, Users
} from 'lucide-react';

// Single source of truth for navigation. The Sidebar renders from this, and the
// route table in router.tsx mounts the corresponding pages — so a nav link can
// never point at a route that does not exist.
//
// This lives beside router.tsx rather than inside it because router.tsx exports
// a component: mixing component and non-component exports in one module breaks
// React Fast Refresh (react-refresh/only-export-components).
//
// Every entry here is a built feature. The former ACCESS section (USSD/SMS and
// WhatsApp) was removed rather than left as placeholders: neither had a backend
// of any kind, so the nav was advertising access channels that did not exist.
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
      { label: 'Farm Records', to: '/records', icon: <ClipboardList size={14} /> },
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
];
