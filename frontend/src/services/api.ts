import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const ledgerService = {
  getLogs: () => api.get('/ledger/logs'),
  createLog: (data) => api.post('/ledger/logs', data),
  getSummary: () => api.get('/ledger/summary'),
  getTransactions: () => api.get('/ledger/transactions'),
};

export const equipmentService = {
  getEquipment: () => api.get('/equipment/'),
  createEquipment: (data) => api.post('/equipment/', data),
  getMaintenance: (id) => api.get(`/equipment/${id}/maintenance`),
  createMaintenance: (data) => api.post('/equipment/maintenance', data),
};

export const dssService = {
  predict: (data) => api.post('/dss/predict', data),
  train: () => api.post('/dss/train'),
};

export default api;
