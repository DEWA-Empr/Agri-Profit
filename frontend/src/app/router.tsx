import type { FC } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import DashboardPage from '../features/dashboard/DashboardPage';
import FarmRecordsPage from '../features/farm-records/FarmRecordsPage';
import ReportsPage from '../features/reports/ReportsPage';
import EquipmentPage from '../features/equipment/EquipmentPage';
import DSSPredictPage from '../features/dss/DSSPredictPage';
import InvestorsPage from '../features/investors/InvestorsPage';

// The route table. The nav that mounts these routes lives in ./navigation, so
// a nav link can never point at a route that does not exist.

export const AppRoutes: FC<{ isOnline: boolean; pendingCount: number; onRecordChange: () => void }> = ({ isOnline, pendingCount, onRecordChange }) => (
  <Routes>
    <Route path="/" element={<DashboardPage isOnline={isOnline} pendingCount={pendingCount} />} />
    <Route path="/records" element={<FarmRecordsPage isOnline={isOnline} onRecordChange={onRecordChange} />} />
    <Route path="/reports" element={<ReportsPage />} />
    <Route path="/equipment" element={<EquipmentPage />} />
    <Route path="/dss" element={<DSSPredictPage />} />
    <Route path="/investors" element={<InvestorsPage />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);
