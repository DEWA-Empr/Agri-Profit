import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AppRoutes } from './router';
import { IdentityContext, type IdentityState } from '../features/auth/useIdentity';
import type { CurrentUser } from '../lib/apiClient';

// WHAT THESE PROTECT. Frontend routing is a usability layer — every endpoint
// behind these screens is enforced by the API against the caller's role, and
// deleting this guard would leak nothing. What it would restore is the bug it
// was written for: a worker signing in landed on /, whose KPI tiles, both
// charts and the decision table each answered 403 and each swallowed it, so the
// farm's first screen was a wall of zeros that looked like a statement about
// the business.
//
// The assertions are about WHERE A ROLE ENDS UP, not about how the guard is
// built. Each page is stubbed to a marker so a test failure names the screen
// that was reached rather than dragging in recharts and the real data layer.

vi.mock('../features/dashboard/DashboardPage', () => ({
  default: () => <div>DASHBOARD</div>,
}));
vi.mock('../features/farm-records/FarmRecordsPage', () => ({
  default: () => <div>FARM RECORDS</div>,
}));
vi.mock('../features/reports/ReportsPage', () => ({
  default: () => <div>P&L REPORT</div>,
}));
vi.mock('../features/equipment/EquipmentPage', () => ({
  default: () => <div>EQUIPMENT</div>,
}));
vi.mock('../features/dss/DSSPredictPage', () => ({
  default: () => <div>DSS</div>,
}));
vi.mock('../features/investors/InvestorsPage', () => ({
  default: () => <div>INVESTORS</div>,
}));

const OWNER = [
  'log:create', 'log:read', 'log:reverse', 'finance:read',
  'equipment:read', 'equipment:manage', 'forecast:read', 'forecast:use',
  'share:manage', 'member:manage',
];
const MANAGER = OWNER.filter((p) => p !== 'share:manage' && p !== 'member:manage');
const WORKER = ['log:create', 'log:read', 'forecast:read'];

const user = (role: string, permissions: string[]): CurrentUser => ({
  id: 1, email: `${role}@test.example`, farm_id: 1, role, is_active: true, permissions,
});

/** Render the route table at `path` for a caller whose identity is `state`. */
function renderAt(path: string, state: IdentityState) {
  return render(
    <IdentityContext.Provider value={state}>
      <MemoryRouter initialEntries={[path]}>
        <AppRoutes isOnline pendingCount={0} onRecordChange={() => {}} />
      </MemoryRouter>
    </IdentityContext.Provider>,
  );
}

const asRole = (role: string, permissions: string[]): IdentityState =>
  ({ status: 'ready', user: user(role, permissions) });

describe('a worker is routed to the screens they can actually use', () => {
  it('lands on Farm Records instead of the dashboard', async () => {
    renderAt('/', asRole('worker', WORKER));
    expect(await screen.findByText('FARM RECORDS')).toBeTruthy();
    expect(screen.queryByText('DASHBOARD')).toBeNull();
  });

  it('is redirected away from the P&L report', async () => {
    renderAt('/reports', asRole('worker', WORKER));
    expect(await screen.findByText('FARM RECORDS')).toBeTruthy();
    expect(screen.queryByText('P&L REPORT')).toBeNull();
  });

  it('is redirected away from equipment', async () => {
    renderAt('/equipment', asRole('worker', WORKER));
    expect(await screen.findByText('FARM RECORDS')).toBeTruthy();
    expect(screen.queryByText('EQUIPMENT')).toBeNull();
  });

  it('is redirected away from investor sharing', async () => {
    renderAt('/investors', asRole('worker', WORKER));
    expect(await screen.findByText('FARM RECORDS')).toBeTruthy();
    expect(screen.queryByText('INVESTORS')).toBeNull();
  });

  it('reaches Farm Records directly, which needs no permission', async () => {
    renderAt('/records', asRole('worker', WORKER));
    expect(await screen.findByText('FARM RECORDS')).toBeTruthy();
  });

  it('lands on Farm Records from an unknown path, not on the dashboard', async () => {
    renderAt('/no-such-page', asRole('worker', WORKER));
    expect(await screen.findByText('FARM RECORDS')).toBeTruthy();
  });
});

describe('a manager keeps the dashboard and everything their role admits', () => {
  it('sees the dashboard at /', async () => {
    renderAt('/', asRole('manager', MANAGER));
    expect(await screen.findByText('DASHBOARD')).toBeTruthy();
  });

  it('reaches the P&L report', async () => {
    renderAt('/reports', asRole('manager', MANAGER));
    expect(await screen.findByText('P&L REPORT')).toBeTruthy();
  });

  it('reaches equipment and the forecast', async () => {
    renderAt('/equipment', asRole('manager', MANAGER));
    expect(await screen.findByText('EQUIPMENT')).toBeTruthy();
  });

  it('is still redirected away from investor sharing, which is owner-only', async () => {
    renderAt('/investors', asRole('manager', MANAGER));
    // Back to the manager's own home — the dashboard — not to a worker's.
    expect(await screen.findByText('DASHBOARD')).toBeTruthy();
    expect(screen.queryByText('INVESTORS')).toBeNull();
  });
});

describe('an owner reaches every screen', () => {
  it.each([
    ['/', 'DASHBOARD'],
    ['/records', 'FARM RECORDS'],
    ['/reports', 'P&L REPORT'],
    ['/equipment', 'EQUIPMENT'],
    ['/dss', 'DSS'],
    ['/investors', 'INVESTORS'],
  ])('opens %s', async (path, marker) => {
    renderAt(path, asRole('owner', OWNER));
    expect(await screen.findByText(marker)).toBeTruthy();
  });
});

describe('while the role is still unknown', () => {
  it('decides nothing rather than bouncing the caller', async () => {
    // A redirect fired on incomplete information is not undone when the answer
    // arrives — the user would simply be on the wrong page having never asked.
    renderAt('/', { status: 'loading' });
    await waitFor(() => expect(screen.queryByText('DASHBOARD')).toBeNull());
    expect(screen.queryByText('FARM RECORDS')).toBeNull();
  });

  it('falls back to the universally-available screen if identity fails', async () => {
    renderAt('/', { status: 'error' });
    expect(await screen.findByText('FARM RECORDS')).toBeTruthy();
  });
});
