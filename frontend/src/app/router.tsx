import { lazy, Suspense, type FC, type ReactNode } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { colors } from '../styles/theme';
import { homePathFor, permissionForPath } from './navigation';
import { useIdentity, permissionsOf } from '../features/auth/useIdentity';

// Route table. Every page is code-split with React.lazy so a first visit on a
// rural 3G connection downloads only the screen it needs, instead of one
// entry bundle carrying every page. The nav that mounts these routes lives in
// ./navigation.
const DashboardPage = lazy(() => import('../features/dashboard/DashboardPage'));
const FarmRecordsPage = lazy(() => import('../features/farm-records/FarmRecordsPage'));
const ReportsPage = lazy(() => import('../features/reports/ReportsPage'));
const EquipmentPage = lazy(() => import('../features/equipment/EquipmentPage'));
const DSSPredictPage = lazy(() => import('../features/dss/DSSPredictPage'));
const InvestorsPage = lazy(() => import('../features/investors/InvestorsPage'));

// Shown while a route chunk is in flight. Deliberately plain text rather than a
// spinner: on a slow link the chunk usually arrives in a few hundred ms, and a
// spinner that flashes reads as breakage.
const RouteFallback = () => (
  <div style={{ padding: '32px', fontSize: '12px', color: colors.labelText }}>Loading…</div>
);

// NAVIGATION, NOT ACCESS CONTROL. Every endpoint behind these screens is
// enforced by the API against the caller's role; this decides only where the
// browser lands. Removing it would expose no data — it would just put a worker
// back on a dashboard whose every panel answers 403, which is the bug it exists
// to fix (see docs: the panels used to swallow that and render zeros).
//
// A REDIRECT RATHER THAN A FORBIDDEN SCREEN. The user did not do anything
// wrong: their role simply does not include this screen, the nav never offered
// it, and the only way here is a typed URL or a stale bookmark. Sending them to
// a page they can actually use answers that better than an error page they
// would have to navigate away from. Panels that a permitted role can reach but
// whose individual data is refused still explain themselves — that is NoAccess,
// and the two are complementary rather than alternatives.
const Guard: FC<{ path: string; children: ReactNode }> = ({ path, children }) => {
  const identity = useIdentity();
  const permissions = permissionsOf(identity);

  // Decide nothing until the role is known. Redirecting on `null` would bounce
  // a manager to /records for the frame before /auth/me answers, and a redirect
  // is not undone when the answer arrives — they would simply be on the wrong
  // page having never asked to be.
  if (permissions === null) return <RouteFallback />;

  const required = permissionForPath(path);
  if (required && !permissions.includes(required)) {
    return <Navigate to={homePathFor(permissions)} replace />;
  }
  return <>{children}</>;
};

// Unmatched paths go to the caller's own home, not to a fixed one: `/` is the
// dashboard, and sending a worker there is the exact bounce this change removes.
const HomeRedirect = () => {
  const identity = useIdentity();
  const permissions = permissionsOf(identity);
  if (permissions === null) return <RouteFallback />;
  return <Navigate to={homePathFor(permissions)} replace />;
};

export const AppRoutes: FC<{ isOnline: boolean; pendingCount: number; onRecordChange: () => void }> = ({ isOnline, pendingCount, onRecordChange }) => (
  <Suspense fallback={<RouteFallback />}>
    <Routes>
      <Route path="/" element={<Guard path="/"><DashboardPage isOnline={isOnline} pendingCount={pendingCount} /></Guard>} />
      {/* Farm Records carries no permission: it is the one screen every signed-in
          role may use, which is what makes it a safe redirect target. */}
      <Route path="/records" element={<FarmRecordsPage isOnline={isOnline} onRecordChange={onRecordChange} />} />
      <Route path="/reports" element={<Guard path="/reports"><ReportsPage /></Guard>} />
      <Route path="/equipment" element={<Guard path="/equipment"><EquipmentPage /></Guard>} />
      <Route path="/dss" element={<Guard path="/dss"><DSSPredictPage /></Guard>} />
      <Route path="/investors" element={<Guard path="/investors"><InvestorsPage /></Guard>} />
      <Route path="*" element={<HomeRedirect />} />
    </Routes>
  </Suspense>
);
