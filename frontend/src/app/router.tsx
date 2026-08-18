import { lazy, Suspense, type FC } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { colors } from '../styles/theme';

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

export const AppRoutes: FC<{ isOnline: boolean; pendingCount: number; onRecordChange: () => void }> = ({ isOnline, pendingCount, onRecordChange }) => (
  <Suspense fallback={<RouteFallback />}>
    <Routes>
      <Route path="/" element={<DashboardPage isOnline={isOnline} pendingCount={pendingCount} />} />
      <Route path="/records" element={<FarmRecordsPage isOnline={isOnline} onRecordChange={onRecordChange} />} />
      <Route path="/reports" element={<ReportsPage />} />
      <Route path="/equipment" element={<EquipmentPage />} />
      <Route path="/dss" element={<DSSPredictPage />} />
      <Route path="/investors" element={<InvestorsPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </Suspense>
);
