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
