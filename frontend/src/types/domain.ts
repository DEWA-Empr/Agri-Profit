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
  // Set when this log is a reversing (contra) entry: the id of the log it
  // offsets. The API has always returned this (backend schemas.OperationalLog);
  // it was simply missing from this mirror.
  //
  // Note the asymmetry: a log can say what it reverses, but NOT whether it has
  // itself been reversed — there is no `reversed_by` field. That state is
  // derived on the client by collecting every non-null reverses_id in the list.
  reverses_id?: number | null;
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
// One unit's worth of a crop's recorded yield. `unit` is null for older rows
// saved before the unit field was constrained to a fixed list.
export interface YieldByUnit {
  unit?: string | null;
  quantity: number;
}

export interface DssCropMetrics {
  crop: string;
  revenue: number;
  expenses: number;
  gross_margin: number;
  // A single total ONLY when one unit is in play; 0 when nothing is recorded;
  // **null when the crop's yields span two or more units**, because no honest
  // single total exists then. Never a sum across different units.
  yield_quantity?: number | null;
  yield_unit?: string | null;
  // Always the authoritative per-unit breakdown.
  yield_by_unit?: YieldByUnit[];
  // null when the crop has no recorded yield, and when units are mixed (a unit
  // cost needs a single denominator). Denominated in the crop's HARVEST unit —
  // wet mass as weighed in the field.
  unit_cost_of_production?: number | null;
  // Marketable Mass (kg) summed across the crop's non-reversed drying runs, and
  // the second unit cost denominated against it. Both null when the crop has no
  // drying run; the per-kg cost is also null at zero marketable mass. These sit
  // BESIDE unit_cost_of_production — neither replaces the other, and the two
  // carry different denominators (harvest unit vs kg out of the dryer).
  marketable_mass_kg?: number | null;
  unit_cost_per_kg_marketable?: number | null;
  // Break-even yield at the price actually realised (revenue / yield_quantity).
  // RETROSPECTIVE: it says what was needed at the achieved price, not what will
  // be needed. null whenever no unit price can be derived — mixed units, no
  // yield, or no revenue.
  break_even_yield?: number | null;
  break_even_unit?: string | null;
}

export interface DssDecisionSupport {
  crops: DssCropMetrics[];
  overall: { revenue: number; expenses: number; gross_margin: number };
}

// --- Enterprise economics (GET /dss/cost-structure, /break-even-price,
// /sensitivity, POST /dss/partial-budget) ---
// Mirrors backend schemas.CostStructure and friends. Every figure here is
// derived from the farm's own ledger at read time; none of it is stored, and
// none of it comes from the Tier-2 yield model.

export interface CostStructure {
  variable_cost: number;
  // Its own line, never folded into the variable pool. Repairs are genuinely
  // semi-variable and the reader has to be able to see the assumption — though
  // it IS part of cash_cost for the computation.
  semi_variable_cost: number;
  // A DEPRECIATION row actually posted to the ledger. Distinct from the
  // allocated-fixed overlay below, which is never a ledger entry.
  fixed_cost_recorded: number;
  // Cost carrying no Cost Subtype. Never defaulted into a behaviour bucket.
  unclassified_cost: number;
  total_recorded_cost: number;
  cash_cost: number;
  // null when nothing is recorded — NOT 100 and NOT 0. There is no coverage of
  // nothing, and a vacuous 100 would read as "fully classified".
  classification_coverage_pct?: number | null;
  revenue_ngn: number;
  cash_operating_cost_ngn: number;
  // null at zero revenue: an input-only crop has no revenue for its cost to be
  // a proportion of. Not infinite, not zero.
  operating_expense_ratio_pct?: number | null;
}

export interface CropCostStructure extends CostStructure {
  crop: string;
}

export interface CostStructureResponse {
  crops: CropCostStructure[];
  farm: CostStructure;
}

// "derived" — the window is the span of the farm's own ledger, and widens with
// every new log. "specified" — the caller pinned it. The distinction travels
// with the figures because a price computed over a derived window cannot be
// re-derived after the next entry.
export type PeriodSource = 'derived' | 'specified';

export interface CropBreakEvenPrice {
  crop: string;
  // The two prices do NOT share a cost base, and the field names say so. The
  // cash figure is classified variable + semi-variable cost only; the total
  // figure is every recorded cost (unclassified included) plus the allocated
  // fixed overlay. Both null where the crop has no marketable mass.
  break_even_price_cash_ngn_per_kg?: number | null;
  break_even_price_total_ngn_per_kg?: number | null;
  variable_and_semi_variable_cost_ngn: number;
  total_recorded_cost_ngn: number;
  allocated_fixed_ngn?: number | null;
  total_cost_ngn: number;
  marketable_mass_kg?: number | null;
  classification_coverage_pct?: number | null;
}

export interface BreakEvenPriceResponse {
  crops: CropBreakEvenPrice[];
  period_days: number;
  period_source: PeriodSource;
  period_fixed_cost_ngn: number;
  equipment_count: number;
  // Assets carrying no depreciation rate. Non-zero means the overlay above is
  // PARTIAL, and saying so is what stops it being read as a small true fixed
  // cost.
  equipment_unrated_count: number;
  total_direct_cost_all_crops: number;
}

export interface SensitivityRow {
  percentage: number;
  marketable_mass_kg?: number | null;
  break_even_price_cash_ngn_per_kg?: number | null;
  break_even_price_total_ngn_per_kg?: number | null;
}

export interface CropSensitivity {
  crop: string;
  // Always true from this endpoint, and carried rather than assumed: the matrix
  // answers "if you harvest this much, what price covers your costs". It
  // forecasts neither yield nor price, and the interface must say so.
  conditional: boolean;
  baseline_marketable_mass_kg?: number | null;
  cash_cost_ngn: number;
  total_cost_ngn: number;
  rows: SensitivityRow[];
}

export interface SensitivityResponse {
  crops: CropSensitivity[];
  period_days: number;
  period_source: PeriodSource;
}

// Four quantities, all non-negative: the sign of the appraisal lives in which
// slot a quantity occupies, never in the number itself.
export interface PartialBudgetRequest {
  added_revenue_ngn: number;
  reduced_cost_ngn: number;
  lost_revenue_ngn: number;
  added_cost_ngn: number;
}

export interface PartialBudgetResponse extends PartialBudgetRequest {
  benefits_ngn: number;
  costs_ngn: number;
  // Signed and unclamped. A negative net change is a valid and useful answer —
  // it says the change is not worth making — and is never suppressed.
  net_change_ngn: number;
}

// --- Bioprocess: post-harvest drying (ticket 08) ---
// A drying run is an OperationalLog with activity_type 'bioprocess' whose
// extra_data carries a DryingParams payload. There is no separate create
// endpoint: runs are written through POST /ledger/logs like any other log, and
// read back — with every derived metric computed on the fly — from /bioprocess.

export type DryingMethod = 'SUN' | 'SOLAR_DRYER' | 'MECHANICAL' | 'AMBIENT';

// An optional intermediate moisture measurement during the run. Three or more
// usable readings unlock the Page-model fit; fewer and only Newton is reported.
export interface DryingReading {
  time_hours: number;
  moisture_wb: number;
}

// Mirrors backend schemas.DryingParams. Moisture is always **wet basis** here —
// what a field meter reads. The dry-basis conversion happens server-side.
export interface DryingParams {
  process_type: 'DRYING';
  method: DryingMethod;
  mass_in_kg: number;
  mass_out_kg: number;
  moisture_initial_wb: number;
  moisture_final_wb: number;
  drying_time_hours: number;
  air_temperature_c?: number | null;
  readings?: DryingReading[];
}

// The linearised Page fit. null on the metrics when there were fewer than three
// usable readings — the backend never fabricates a fit.
export interface DryingPageFit {
  n: number;
  k: number;
  r2_linear: number;
  n_used: number;
  n_dropped: number;
}

// Mirrors backend schemas.DryingMetrics — all computed on read, never stored.
export interface DryingMetrics {
  dry_matter_kg: number;
  // Outlet mass predicted by dry-matter conservation, and the signed gap
  // between it and what was actually weighed out.
  mass_out_expected_kg: number;
  process_loss_kg: number;
  process_loss_pct: number;
  // Set when |process_loss_pct| > 5: a data-quality signal, not an error.
  process_loss_warning: boolean;
  // A water balance — (mass_in x M_i) - (mass_out x M_f) — not the mass
  // difference. The two are only equal when dry matter is conserved; where
  // there is process loss, the mass difference also contains dry matter that
  // physically left the system.
  water_removed_kg: number;
  drying_rate_kg_h: number;
  specific_drying_rate: number;
  moisture_initial_db: number;
  moisture_final_db: number;
  moisture_ratio_final: number;
  newton_k: number;
  page?: DryingPageFit | null;
  // null — not false — when the crop is outside the safe-storage table, or when
  // no crop was recorded. An unknown crop is never assumed unsafe.
  safe_storage?: boolean | null;
  safe_storage_threshold_wb?: number | null;
}

// GET /bioprocess/{id}
export interface BioprocessDetail {
  id: number;
  crop?: string | null;
  params: DryingParams;
  metrics: DryingMetrics;
}

// GET /bioprocess/summary — per-crop aggregates. Reversed runs and reversal
// contras are excluded server-side, so these totals are a real mass balance.
export interface BioprocessCropSummary {
  crop: string;
  drying_runs: number;
  total_mass_in_kg: number;
  total_marketable_mass_kg: number;
  total_water_removed_kg: number;
  mean_drying_rate_kg_h: number;
  mean_newton_k_by_method: Record<string, number>;
  safe_storage_share?: number | null;
}

export interface BioprocessSummary {
  crops: BioprocessCropSummary[];
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
