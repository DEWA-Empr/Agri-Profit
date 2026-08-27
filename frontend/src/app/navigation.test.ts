import { describe, it, expect } from 'vitest';
import {
  navSections, visibleSections, homePathFor, permissionForPath, type NavSection,
} from './navigation';

// Nav filtering is presentation, not access control — every one of these routes
// is independently enforced by the API. What these tests protect is that the
// filter FAILS CLOSED: the failure mode worth catching is a worker being shown
// links that 403 when clicked, which reads as a broken app rather than as a
// boundary.

const OWNER = [
  'log:create', 'log:read', 'log:reverse', 'finance:read',
  'equipment:read', 'equipment:manage', 'forecast:read', 'forecast:use',
  'share:manage', 'member:manage',
];
const MANAGER = OWNER.filter((p) => p !== 'share:manage' && p !== 'member:manage');
const WORKER = ['log:create', 'log:read', 'forecast:read'];

const labels = (sections: NavSection[]) =>
  sections.flatMap((s) => s.items.map((i) => i.label));

describe('visibleSections', () => {
  it('shows an owner every link', () => {
    expect(labels(visibleSections(navSections, OWNER))).toEqual(labels(navSections));
  });

  it('hides investor sharing from a manager', () => {
    const shown = labels(visibleSections(navSections, MANAGER));
    expect(shown).not.toContain('Investors');
    expect(shown).toContain('P&L Report');
    expect(shown).toContain('Equipment');
  });

  it('shows a worker only entry screens', () => {
    const shown = labels(visibleSections(navSections, WORKER));
    // The dashboard is NOT among them. Every panel on it reads a finance:read
    // endpoint, so offering the link to a worker led to a page whose tiles,
    // charts and decision table all answered 403.
    expect(shown).not.toContain('Dashboard');
    expect(shown).toContain('Farm Records');
    expect(shown).not.toContain('P&L Report');
    expect(shown).not.toContain('Equipment');
    expect(shown).not.toContain('DSS Predict');
    expect(shown).not.toContain('Investors');
  });

  it('fails closed while the identity call is still in flight', () => {
    // null = not yet known. Showing everything here would flash links that then
    // 403; showing the unrestricted subset degrades quietly instead.
    const shown = labels(visibleSections(navSections, null));
    expect(shown).toContain('Farm Records');
    expect(shown).not.toContain('Dashboard');
    expect(shown).not.toContain('P&L Report');
  });

  it('fails closed on an empty permission list', () => {
    expect(labels(visibleSections(navSections, []))).not.toContain('Investors');
  });

  it('drops a section that has been emptied rather than leaving a bare heading', () => {
    const sections = visibleSections(navSections, WORKER);
    expect(sections.every((s) => s.items.length > 0)).toBe(true);
    expect(sections.map((s) => s.heading)).not.toContain('INTELLIGENCE');
  });

  it('ignores a permission the client does not recognise', () => {
    const shown = labels(visibleSections(navSections, [...WORKER, 'some:future:permission']));
    expect(shown).not.toContain('Investors');
  });

  it('never invents a link that is not in the source table', () => {
    const all = new Set(labels(navSections));
    for (const perms of [OWNER, MANAGER, WORKER, [], null]) {
      for (const label of labels(visibleSections(navSections, perms))) {
        expect(all.has(label)).toBe(true);
      }
    }
  });
});

// The route guard and the nav read the same table, so these two helpers are
// what stop a link and its route disagreeing about who may pass.
describe('homePathFor', () => {
  it('sends an owner and a manager to the dashboard', () => {
    expect(homePathFor(OWNER)).toBe('/');
    expect(homePathFor(MANAGER)).toBe('/');
  });

  it('sends a worker to farm records', () => {
    // The approved product decision: a worker's practical home is the screen
    // they actually use, not a dashboard of figures they may not read.
    expect(homePathFor(WORKER)).toBe('/records');
  });

  it('sends an unknown caller to farm records rather than guessing', () => {
    expect(homePathFor(null)).toBe('/records');
    expect(homePathFor([])).toBe('/records');
  });

  it('only ever returns a path that needs no permission', () => {
    // A home that were itself guarded would redirect to itself forever.
    for (const perms of [OWNER, MANAGER, WORKER, [], null]) {
      const home = homePathFor(perms);
      const required = permissionForPath(home);
      expect(required === undefined || (perms ?? []).includes(required)).toBe(true);
    }
  });
});

describe('permissionForPath', () => {
  it('reports what each guarded screen needs', () => {
    expect(permissionForPath('/')).toBe('finance:read');
    expect(permissionForPath('/reports')).toBe('finance:read');
    expect(permissionForPath('/equipment')).toBe('equipment:read');
    expect(permissionForPath('/investors')).toBe('share:manage');
  });

  it('leaves farm records open to every signed-in role', () => {
    expect(permissionForPath('/records')).toBeUndefined();
  });
});
