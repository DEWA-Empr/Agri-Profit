import axios from 'axios';

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

// NOTE: request/response payloads are typed loosely here for now. Per-method
// typing against types/domain.ts lands in Phase 4 alongside the feature-page
// rewrites (the current page components pass loosely-typed form state).
export const ledgerService = {
  getLogs: () => api.get('/ledger/logs'),
  createLog: (data: unknown) => api.post('/ledger/logs', data),
  getSummary: () => api.get('/ledger/summary'),
  getTransactions: () => api.get('/ledger/transactions'),
};

export const equipmentService = {
  getEquipment: () => api.get('/equipment/'),
  createEquipment: (data: unknown) => api.post('/equipment/', data),
  getMaintenance: (id: number | string) => api.get(`/equipment/${id}/maintenance`),
  createMaintenance: (data: unknown) => api.post('/equipment/maintenance', data),
};

export const dssService = {
  predict: (data: unknown) => api.post('/dss/predict', data),
  train: () => api.post('/dss/train'),
};

export default api;
