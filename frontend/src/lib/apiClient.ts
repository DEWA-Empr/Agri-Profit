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
  DssDecisionSupport,
  ShareLink,
  ShareLinkMinted,
  InvestorReport,
  BioprocessDetail,
  BioprocessSummary,
  CostStructureResponse,
  BreakEvenPriceResponse,
  SensitivityResponse,
  PartialBudgetRequest,
  PartialBudgetResponse,
  YieldBaselineResponse,
} from '../types/domain';
import { getToken, clearToken } from './authToken';
import { purgeApiReadCache } from './apiCache';

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

// Attach the bearer token (if any) to every request, so all domain calls are
// authenticated without each caller having to remember to add the header.
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// A 401 means the token is missing/expired/invalid: drop it and send the user
// back to the login screen. `onUnauthorized` is wired up by the AuthProvider so
// this module stays free of React/router imports.
let onUnauthorized: (() => void) | null = null;
export const setUnauthorizedHandler = (handler: () => void) => {
  onUnauthorized = handler;
};

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearToken();
      onUnauthorized?.();
    }
    return Promise.reject(error);
  },
);

// Auth endpoints. Register creates a farm + first user; both return a JWT.
export interface AuthToken {
  access_token: string;
  token_type: string;
}

// Mirrors backend schemas.UserOut. The farm's *name* is deliberately absent —
// UserOut does not expose it, so the UI shows the email (which it does expose)
// rather than inventing a display name.
export interface CurrentUser {
  id: number;
  email: string;
  farm_id: number;
}

export const authService = {
  register: (data: { email: string; password: string; farm_name?: string }) =>
    api.post<AuthToken>('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post<AuthToken>('/auth/login', data),
  me: () => api.get<CurrentUser>('/auth/me'),
};

// Request/response payloads are typed against types/domain.ts — the shared
// mirror of the backend Pydantic schemas (STRUCTURE.md §5).
export const ledgerService = {
  getLogs: () => api.get<OperationalLog[]>('/ledger/logs'),
  // The ONE write path for an operational log — both the online save
  // (lib/logs.ts) and the offline queue flush (lib/sync.ts) post through here,
  // so the read-cache invalidation lives here rather than in either caller.
  // Every derived read the service worker caches (the ledger, the P&L, and the
  // four /dss reads behind the cost structure, both break-even prices, the
  // sensitivity table and the OER) is computed from these rows, so a log that
  // reached the server makes all of them stale at once.
  //
  // Purge on 2xx, and on 409 too: a 409 here is an idempotent replay of a
  // client_id the server already holds, which means the record exists on the
  // server side and the cached reads are just as stale as after a fresh write.
  // Every other failure — offline, timeout, 5xx — leaves the write queued
  // rather than posted, and there is nothing new to invalidate.
  createLog: async (data: OperationalLogCreate) => {
    try {
      const res = await api.post<OperationalLog>('/ledger/logs', data);
      await purgeApiReadCache();
      return res;
    } catch (err: unknown) {
      if ((err as { response?: { status?: number } })?.response?.status === 409) {
        await purgeApiReadCache();
      }
      throw err;
    }
  },
  getSummary: () => api.get<Summary>('/ledger/summary'),
  getTransactions: () => api.get<FinancialTransaction[]>('/ledger/transactions'),
  // Post an offsetting entry for a mistaken log. Ledger records are immutable —
  // this is the only correction mechanism. 409 if the target is itself a
  // reversal or has already been reversed; 404 if it isn't this farm's.
  //
  // The purge lives here, not in the page, for the same reason it does in
  // createLog: a reversal changes the ledger, the P&L and all four cached /dss
  // reads at once, and every caller of this method would otherwise have to
  // remember that. Purge on 2xx, and on 409 and 404 too — both mean the server
  // holds a state the cached reads were not built from (the target is already
  // reversed, is itself a contra, or is not this farm's row at all), so the
  // caller's refetch must not be served the pre-mutation body. Every other
  // failure — offline, timeout, 5xx — leaves the ledger untouched, and there is
  // nothing to invalidate.
  reverseLog: async (id: number) => {
    try {
      const res = await api.post<OperationalLog>(`/ledger/logs/${id}/reverse`);
      await purgeApiReadCache();
      return res;
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 409 || status === 404) {
        await purgeApiReadCache();
      }
      throw err;
    }
  },
};

// Read-only. Drying runs are CREATED through ledgerService.createLog with a
// DryingParams payload in extra_data — there is deliberately no second write
// path (see backend/app/api/endpoints/bioprocess.py).
export const bioprocessService = {
  getRun: (id: number) => api.get<BioprocessDetail>(`/bioprocess/${id}`),
  getSummary: (crop?: string) =>
    api.get<BioprocessSummary>('/bioprocess/summary', { params: crop ? { crop } : undefined }),
};

export const equipmentService = {
  getEquipment: () => api.get<Equipment[]>('/equipment/'),
  createEquipment: (data: EquipmentCreate) => api.post<Equipment>('/equipment/', data),
  getMaintenance: (id: number | string) => api.get<MaintenanceLog[]>(`/equipment/${id}/maintenance`),
  createMaintenance: (data: MaintenanceLogCreate) => api.post<MaintenanceLog>('/equipment/maintenance', data),
};

// The DSS yield model output: a predicted yield plus an honest confidence
// (derived from the spread across the forest's trees) and a prediction interval.
export interface DssPrediction {
  prediction: number;
  unit: string;
  confidence: number;
  interval: { lower: number; upper: number };
  feature_importances: Record<string, number>;
}

// Metadata for the trained yield model, from GET /dss/model. `trained` is
// false when no model has been fitted yet, in which case NOTHING else is
// present — callers must not read metrics off an untrained response.
export interface DssModelInfo {
  trained: boolean;
  metrics?: { r2: number; mae: number };
  n_samples?: number;
  n_estimators?: number;
  target?: string;
  target_unit?: string;
  trained_at?: string;
  // The crops the model was trained on. Absent while untrained — the endpoint
  // reports {"trained": false} and nothing else, rather than an empty list that
  // would read as "no crops" instead of "no model".
  crops?: string[];
}

// Predict request: three numeric field conditions plus the crop to forecast.
export interface DssPredictInput {
  rainfall: number;
  fertilizer_used: number;
  soil_ph: number;
  crop: string;
}

export const dssService = {
  predict: (data: DssPredictInput) => api.post<DssPrediction>('/dss/predict', data),
  train: () => api.post('/dss/train'),
  // Model quality metadata (R², MAE, sample count, train time).
  getModel: () => api.get<DssModelInfo>('/dss/model'),
  // Tier 1: deterministic per-crop metrics computed from the real ledger.
  getDecisionSupport: () => api.get<DssDecisionSupport>('/dss/decision-support'),

  // --- Enterprise economics ------------------------------------------------
  // All three reads are fetched UNFILTERED and the crop is chosen on the
  // client. Filtering server-side would mean a request per crop switch, and
  // these are the screens most likely to be read on a poor link; one payload
  // that the offline cache can serve whole is worth more than a narrower one
  // fetched five times. The farm-wide figures on the cost structure are
  // computed over every crop regardless of the filter in any case.
  getCostStructure: () => api.get<CostStructureResponse>('/dss/cost-structure'),
  getBreakEvenPrice: () => api.get<BreakEvenPriceResponse>('/dss/break-even-price'),
  getSensitivity: () => api.get<SensitivityResponse>('/dss/sensitivity'),
  // Olympic and grand average yield per crop. Fetched unfiltered like its three
  // neighbours, and cached by the same service-worker rule (vite.config.ts).
  getYieldBaseline: () => api.get<YieldBaselineResponse>('/dss/yield-baseline'),

  // Stateless: four numbers in, a signed net change out. It reads no ledger row
  // and writes nothing, which is why the form that calls it can fall back to
  // computing the same arithmetic on the device when there is no network.
  partialBudget: (data: PartialBudgetRequest) =>
    api.post<PartialBudgetResponse>('/dss/partial-budget', data),
};

export const reportsService = {
  getPnl: () => api.get<PnlReport>('/reports/pnl'),
  getMonthlyPnl: () => api.get<MonthlyPnlPoint[]>('/reports/pnl/monthly'),
  // Direct URL for the CSV download (served with a Content-Disposition header).
  pnlCsvUrl: () => `${api.defaults.baseURL}/reports/pnl.csv`,
};

// Investor share links (ticket 05). Owner routes are authenticated; getReport is
// the public, token-only read an investor opens — no login required.
export const shareService = {
  listLinks: () => api.get<ShareLink[]>('/share/links'),
  createLink: (label?: string) => api.post<ShareLinkMinted>('/share/links', { label: label || null }),
  revokeLink: (id: number) => api.post<ShareLink>(`/share/links/${id}/revoke`),
  getReport: (token: string) => api.get<InvestorReport>(`/share/report/${token}`),
};

export default api;
