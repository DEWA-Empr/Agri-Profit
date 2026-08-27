import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import type { ReactElement } from 'react';
import DashboardPage from './DashboardPage';
import { DecisionSupport } from './components/DecisionSupport';

// THE BUG THESE PIN. Every dashboard panel used to end its fetch in
// `.catch((err) => console.error(err))`. A 403 therefore left the component
// holding its initial state — zero revenue, zero expenses, no crops — and the
// page rendered that as fact. The worst version was the first-run onboarding:
// a caller who may not read the farm's finances was told the farm had no
// records at all.
//
// A refusal must say it is a refusal. These assert the user-visible outcome,
// not which state variable was set.

const forbidden = { response: { status: 403 } };
const serverError = { response: { status: 500 } };

vi.mock('../../lib/apiClient', () => ({
  ledgerService: { getSummary: vi.fn() },
  dssService: { getDecisionSupport: vi.fn() },
  reportsService: { getPnl: vi.fn(), getMonthlyPnl: vi.fn() },
}));

const { ledgerService, dssService, reportsService } = await import('../../lib/apiClient');

// The onboarding and chart panels contain <Link>s, so the tree needs a router
// even though none of these tests navigate.
const draw = (ui: ReactElement) => render(<MemoryRouter>{ui}</MemoryRouter>);

/** A decision-support response with nothing in it — used where the panel is not
 *  the subject of the test and should simply stay quiet. */
const noCrops = { data: { crops: [] } } as never;

describe('the dashboard explains a refusal instead of rendering zeros', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(dssService.getDecisionSupport).mockRejectedValue(forbidden);
    // The two charts are React.lazy, so their chunks can resolve and mount
    // after the test that triggered them has finished. Without a standing
    // default they would call a cleared mock and throw into an unrelated test.
    // They are never the subject here; these keep them silent.
    vi.mocked(reportsService.getPnl).mockResolvedValue({
      data: { revenue: 0, expenses: 0, gross_margin: 0, categories: [] },
    } as never);
    vi.mocked(reportsService.getMonthlyPnl).mockResolvedValue({ data: [] } as never);
  });

  it('tells the user they lack permission when the summary is refused', async () => {
    vi.mocked(ledgerService.getSummary).mockRejectedValue(forbidden);

    draw(<DashboardPage isOnline pendingCount={0} />);

    expect(await screen.findByText(/don't have permission/i)).toBeTruthy();
  });

  it('does not claim the farm has no records when access was refused', async () => {
    // The onboarding path is the dangerous one: it is triggered by an all-zero
    // summary, which is exactly what a swallowed 403 leaves behind.
    vi.mocked(ledgerService.getSummary).mockRejectedValue(forbidden);

    draw(<DashboardPage isOnline pendingCount={0} />);

    await screen.findByText(/don't have permission/i);
    expect(screen.queryByText(/₦0/)).toBeNull();
  });

  it('still shows the real figures when the summary is allowed', async () => {
    // This case is about the summary, so the other panel must succeed too —
    // otherwise its own refusal notice is what the assertion below would find.
    vi.mocked(dssService.getDecisionSupport).mockResolvedValue(noCrops);
    vi.mocked(ledgerService.getSummary).mockResolvedValue({
      data: { revenue: 1_500_000, expenses: 500_000, gross_margin: 1_000_000 },
    } as never);

    draw(<DashboardPage isOnline pendingCount={0} />);

    expect(await screen.findByText('₦1.00M')).toBeTruthy();
    expect(screen.queryByText(/don't have permission/i)).toBeNull();
  });

  it('does not mistake a server fault for a permission boundary', async () => {
    // A 500 is not "you may not". Telling the user their role is wrong would
    // send them to ask the farm owner for something the owner cannot fix.
    vi.mocked(dssService.getDecisionSupport).mockResolvedValue(noCrops);
    vi.mocked(ledgerService.getSummary).mockRejectedValue(serverError);

    draw(<DashboardPage isOnline pendingCount={0} />);

    // It settles into the ordinary first-run state, which is the honest answer
    // when the figures could not be fetched for a reason that is not the user.
    expect(await screen.findByText(/welcome to agriprofit/i)).toBeTruthy();
    expect(screen.queryByText(/don't have permission/i)).toBeNull();
  });
});

describe('the decision-support panel explains a refusal', () => {
  beforeEach(() => vi.clearAllMocks());

  it('says so rather than reporting zero crops', async () => {
    vi.mocked(dssService.getDecisionSupport).mockRejectedValue(forbidden);

    draw(<DecisionSupport />);

    expect(await screen.findByText(/don't have permission/i)).toBeTruthy();
    expect(screen.queryByText(/0 crops/i)).toBeNull();
  });
});
