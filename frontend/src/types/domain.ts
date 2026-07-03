// Shared domain types — the frontend mirror of the backend Pydantic schemas
// (backend/app/schemas/schemas.py). These are the single source of truth for
// API shapes on the frontend; do not redefine them ad-hoc in components.
//
// Names match the backend deliberately (OperationalLog, FinancialTransaction,
// …). When the backend schemas change, update this file. A future option is to
// auto-generate from /openapi.json (see STRUCTURE.md §5).

export type TransactionType = 'debit' | 'credit';

export type Category =
  | 'seed'
  | 'fertilizer'
  | 'labour'
  | 'mechanization'
  | 'yield'
  | 'bioprocess'
  | 'other';

export interface FinancialTransaction {
  id: number;
  amount: number;
  transaction_type: TransactionType;
  category: Category;
  description?: string | null;
  tax_category?: string | null;
  timestamp: string;
}

export interface OperationalLog {
  id: number;
  activity_type: Category;
  description?: string | null;
  quantity?: number | null;
  unit?: string | null;
  crop?: string | null;
  timestamp: string;
  financial_transaction_id?: number | null;
  financial_transaction?: FinancialTransaction | null;
}

export interface Equipment {
  id: number;
  name: string;
  model?: string | null;
  purchase_date?: string | null;
  purchase_price?: number | null;
  depreciation_rate?: number | null;
}

export interface MaintenanceLog {
  id: number;
  equipment_id: number;
  description?: string | null;
  cost?: number | null;
  service_date: string;
}

// The aggregate returned by GET /ledger/summary.
export interface Summary {
  revenue: number;
  expenses: number;
  gross_margin: number;
}

// Profit & Loss report (GET /reports/pnl).
export interface PnlCategory {
  category: Category;
  revenue: number;
  expenses: number;
  net: number;
}

export interface PnlReport {
  revenue: number;
  expenses: number;
  gross_margin: number;
  categories: PnlCategory[];
}

// One month of the trend (GET /reports/pnl/monthly).
export interface MonthlyPnlPoint {
  month: string;
  revenue: number;
  expenses: number;
}

// --- DSS Tier 1: deterministic decision support (GET /dss/decision-support) ---
// Per-crop metrics computed from the real ledger — no model, no synthetic data.
export interface DssCropMetrics {
  crop: string;
  revenue: number;
  expenses: number;
  gross_margin: number;
  yield_quantity: number;
  yield_unit?: string | null;
  // null when the crop has no recorded yield (no fabricated unit cost).
  unit_cost_of_production?: number | null;
}

export interface DssDecisionSupport {
  crops: DssCropMetrics[];
  overall: { revenue: number; expenses: number; gross_margin: number };
}

// --- Investor share links (ticket 05) ---
// Owner-facing metadata for a share link. The token is NEVER present here — only
// its hash is stored server-side — so a lost link must be re-minted.
export interface ShareLink {
  id: number;
  label?: string | null;
  revoked: boolean;
  created_at: string;
}

// The mint response is the only place the raw token is ever returned.
export interface ShareLinkMinted extends ShareLink {
  token: string;
}

// The public read-only report an investor sees from a shared link.
export interface InvestorReport {
  farm_name: string;
  generated_at: string;
  pnl: PnlReport;
  crops: DssCropMetrics[];
}

// --- Create payloads (request bodies) ---

export interface FinancialTransactionCreate {
  amount: number;
  transaction_type: TransactionType;
  category: Category;
  description?: string;
  tax_category?: string;
}

// Creating an Operational Log always carries its paired Financial Transaction.
export interface OperationalLogCreate {
  activity_type: Category;
  description?: string;
  quantity?: number;
  unit?: string;
  crop?: string;
  client_id?: string;
  extra_data?: Record<string, unknown>;
  financial_data: FinancialTransactionCreate;
}

export interface EquipmentCreate {
  name: string;
  model?: string;
  purchase_date?: string;
  purchase_price?: number;
  depreciation_rate?: number;
}

export interface MaintenanceLogCreate {
  equipment_id: number;
  description?: string;
  cost?: number;
}
