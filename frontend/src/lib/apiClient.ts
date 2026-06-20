import axios from 'axios';
import type {
  OperationalLog,
  OperationalLogCreate,
  FinancialTransaction,
  Summary,
  Equipment,
  EquipmentCreate,
  MaintenanceLog,
  MaintenanceLogCreate,
  PnlReport,
  MonthlyPnlPoint,
} from '../types/domain';

// The single axios instance for the whole app. Components and feature api
// modules import from here — nothing constructs raw axios calls or hardcodes
// the base URL (see STRUCTURE.md §3). The base URL is environment-driven.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request/response payloads are typed against types/domain.ts — the shared
// mirror of the backend Pydantic schemas (STRUCTURE.md §5).
export const ledgerService = {
  getLogs: () => api.get<OperationalLog[]>('/ledger/logs'),
  createLog: (data: OperationalLogCreate) => api.post<OperationalLog>('/ledger/logs', data),
  getSummary: () => api.get<Summary>('/ledger/summary'),
  getTransactions: () => api.get<FinancialTransaction[]>('/ledger/transactions'),
};

export const equipmentService = {
  getEquipment: () => api.get<Equipment[]>('/equipment/'),
  createEquipment: (data: EquipmentCreate) => api.post<Equipment>('/equipment/', data),
  getMaintenance: (id: number | string) => api.get<MaintenanceLog[]>(`/equipment/${id}/maintenance`),
  createMaintenance: (data: MaintenanceLogCreate) => api.post<MaintenanceLog>('/equipment/maintenance', data),
};

// The DSS model output shape (a prediction string, or an error/detail message).
export interface DssPrediction {
  prediction?: string;
  error?: string;
  detail?: string;
}

export const dssService = {
  predict: (data: Record<string, number>) => api.post<DssPrediction>('/dss/predict', data),
  train: () => api.post('/dss/train'),
};

export const reportsService = {
  getPnl: () => api.get<PnlReport>('/reports/pnl'),
  getMonthlyPnl: () => api.get<MonthlyPnlPoint[]>('/reports/pnl/monthly'),
  // Direct URL for the CSV download (served with a Content-Disposition header).
  pnlCsvUrl: () => `${api.defaults.baseURL}/reports/pnl.csv`,
};

export default api;
