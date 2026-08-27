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
  /**
   * Permission the page's own reads need, matching a value in the backend's
   * core/roles.py. Omitted means every signed-in role may see the link.
   *
   * The Sidebar hides an item whose permission the caller lacks, so a worker is
   * not offered a screen that would answer 403. This is presentation only — the
   * route still exists and the API still enforces. Nothing here decides access.
   */
  permission?: string;
}

export interface NavSection {
  heading: string;
  items: NavItemDef[];
}

/**
 * Nav filtered to what `permissions` admits. A section with nothing left in it
 * is dropped rather than rendered as a bare heading.
 *
 * A null/undefined permission list (the identity call has not returned, or
 * failed) yields ONLY the unrestricted items. Failing closed matters: showing
 * every link while the answer is unknown would flash screens at a worker that
 * then 403, which reads as breakage rather than as a boundary.
 */
export function visibleSections(
  sections: NavSection[],
  permissions: string[] | null,
): NavSection[] {
  const held = new Set(permissions ?? []);
  return sections
    .map((section) => ({
      ...section,
      items: section.items.filter((item) => !item.permission || held.has(item.permission)),
    }))
    .filter((section) => section.items.length > 0);
}

export const navSections: NavSection[] = [
  {
    heading: 'OVERVIEW',
    items: [
      { label: 'Dashboard', to: '/', icon: <LayoutDashboard size={14} /> },
      { label: 'Farm Records', to: '/records', icon: <ClipboardList size={14} /> },
      { label: 'P&L Report', to: '/reports', icon: <FileText size={14} />, permission: 'finance:read' },
    ],
  },
  {
    heading: 'INTELLIGENCE',
    items: [
      { label: 'Equipment', to: '/equipment', icon: <Tractor size={14} />, permission: 'equipment:read' },
      { label: 'DSS Predict', to: '/dss', icon: <BrainCircuit size={14} />, permission: 'finance:read' },
      { label: 'Investors', to: '/investors', icon: <Users size={14} />, permission: 'share:manage' },
    ],
  },
];
