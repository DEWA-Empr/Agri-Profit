from pydantic import BaseModel, Field, ConfigDict, EmailStr, model_validator, ValidationError
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict, List, Literal
from ..core.enums import Category, TransactionType

# --- Auth Schemas ---
class RegisterRequest(BaseModel):
    # EmailStr rejects malformed addresses at the edge (422) so an unvalidated
    # free-text string can never become an account identifier.
    email: EmailStr
    password: str = Field(..., min_length=8, description="At least 8 characters")
    # Optional: a new tenant's display name; defaults to "<email>'s Farm".
    farm_name: Optional[str] = None

class LoginRequest(BaseModel):
    # Plain str on purpose: login must not distinguish "malformed email" from
    # "wrong credentials" — an unknown/invalid address simply fails to match.
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: str
    farm_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Financial Transaction Schemas ---
class FinancialTransactionBase(BaseModel):
    amount: float
    transaction_type: TransactionType
    category: Category
    description: Optional[str] = None
    tax_category: Optional[str] = None

class FinancialTransactionCreate(FinancialTransactionBase):
    pass

class FinancialTransaction(FinancialTransactionBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Bioprocess: post-harvest drying parameters (ticket 08) ---
# Carried in the OperationalLog.extra_data JSON column for BIOPROCESS logs only
# (see docs/adr/0001). Moisture is entered on a WET basis (what a field meter
# reads); the service layer converts to dry basis for kinetics. This is the
# first place numeric bounds are enforced (LIMITATIONS §3) — every rejection is
# a 422 at the schema edge, never a 500.
class DryingReading(BaseModel):
    time_hours: float = Field(..., gt=0, le=720)
    moisture_wb: float = Field(..., gt=0, lt=100)


class DryingParams(BaseModel):
    process_type: Literal["DRYING"]
    method: Literal["SUN", "SOLAR_DRYER", "MECHANICAL", "AMBIENT"]
    mass_in_kg: float = Field(..., gt=0, le=100_000)
    mass_out_kg: float = Field(..., gt=0)                 # <= mass_in_kg, enforced below
    moisture_initial_wb: float = Field(..., gt=0, lt=100)
    moisture_final_wb: float = Field(..., gt=0, lt=100)   # < initial, enforced below
    drying_time_hours: float = Field(..., gt=0, le=720)
    air_temperature_c: Optional[float] = Field(default=None, ge=-10, le=150)
    readings: List[DryingReading] = []                    # optional intermediate points

    @model_validator(mode="after")
    def _check_physical_consistency(self) -> "DryingParams":
        # Mass cannot increase during drying.
        if self.mass_out_kg > self.mass_in_kg:
            raise ValueError("mass_out_kg cannot exceed mass_in_kg")
        # Drying removes water: the final moisture must be strictly below initial.
        if self.moisture_final_wb >= self.moisture_initial_wb:
            raise ValueError("moisture_final_wb must be less than moisture_initial_wb")
        # readings (when present) must be strictly increasing in time, and every
        # moisture must lie within the run's [final, initial] band (inclusive).
        prev_t: Optional[float] = None
        for r in self.readings:
            if prev_t is not None and r.time_hours <= prev_t:
                raise ValueError("readings must be strictly increasing in time_hours")
            prev_t = r.time_hours
            if not (self.moisture_final_wb <= r.moisture_wb <= self.moisture_initial_wb):
                raise ValueError(
                    "each reading moisture_wb must lie within "
                    "[moisture_final_wb, moisture_initial_wb]"
                )
        return self


# --- Mechanisation: cost classification (enterprise economics, Phase 2) ------
# Carried in the OperationalLog.extra_data JSON column for MECHANIZATION logs
# only, by the same conditional mechanism DryingParams uses for BIOPROCESS (see
# docs/adr/0001) — a cost taxonomy enforced at the schema edge on an existing
# JSON column, so no ledger column and no migration.
class CostBehaviour(str, Enum):
    VARIABLE      = "VARIABLE"
    SEMI_VARIABLE = "SEMI_VARIABLE"
    FIXED         = "FIXED"


class MechanizationParams(BaseModel):
    cost_subtype: Literal["FUEL", "LUBRICANTS", "REPAIRS", "MACHINERY_HIRE", "DEPRECIATION"]
    equipment_id: int | None = None
    hours_used: float | None = Field(default=None, gt=0, le=1000)


# TODO(cite): cost-behaviour classification follows standard enterprise-budget
# practice (variable = scales with output; fixed = independent of output).
# Cite an agricultural economics text or extension enterprise-budget guide
# before submission. "The taxonomy was supplied" is not a citation.
#
# Keyed on (activity category, cost subtype) so a category that later gains a
# subtype model of its own — LABOUR splitting into permanent and casual — is
# added by replacing its single None-keyed row with one row per subtype, with no
# change to the lookup. Categories absent here (YIELD, OTHER) are unclassified.
COST_BEHAVIOUR: dict[tuple[str, str], CostBehaviour] = {
    ("MECHANIZATION", "FUEL"):           CostBehaviour.VARIABLE,
    ("MECHANIZATION", "LUBRICANTS"):     CostBehaviour.VARIABLE,
    ("MECHANIZATION", "REPAIRS"):        CostBehaviour.SEMI_VARIABLE,
    ("MECHANIZATION", "MACHINERY_HIRE"): CostBehaviour.VARIABLE,
    ("MECHANIZATION", "DEPRECIATION"):   CostBehaviour.FIXED,
    ("SEED",      None):                 CostBehaviour.VARIABLE,
    ("FERTILIZER", None):                CostBehaviour.VARIABLE,
    ("LABOUR",    None):                 CostBehaviour.VARIABLE,
    ("BIOPROCESS", None):                CostBehaviour.VARIABLE,
}


def cost_behaviour_for(
    activity_type: "Category | str",
    cost_subtype: Optional[str] = None,
) -> Optional[CostBehaviour]:
    """Pure lookup: (activity category, cost subtype) -> CostBehaviour or None.

    `None` means *unclassified* — the pair has no entry in COST_BEHAVIOUR, which
    covers a mechanisation row carrying no subtype (every legacy row), and any
    category outside the taxonomy. An unclassified row must stay unclassified:
    never default it to VARIABLE, because a guessed classification is
    indistinguishable from a recorded one in every figure derived from it, and
    the coverage percentage exists precisely to keep the two apart.

    Pure: no I/O, no session, no state. Category is normalised to the constant's
    upper-case spelling; the enum's own values are lower-case.
    """
    category = activity_type.value if isinstance(activity_type, Category) else str(activity_type)
    return COST_BEHAVIOUR.get((category.upper(), cost_subtype))


# --- Operational Log Schemas ---
class OperationalLogBase(BaseModel):
    activity_type: Category
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    crop: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    client_id: Optional[str] = None

class OperationalLogCreate(OperationalLogBase):
    financial_data: FinancialTransactionCreate

    @model_validator(mode="after")
    def _validate_activity_payload(self) -> "OperationalLogCreate":
        # Structured validation applies ONLY to the activity types named below.
        # Every other activity type keeps extra_data as an arbitrary,
        # unvalidated dict — exactly as before. Each nested ValidationError is
        # re-raised as a ValueError so Pydantic folds it into this model's own
        # validation error: a 422 at the edge, never a 500.
        #
        # A Bioprocess log must carry a valid drying payload; a missing or
        # malformed one is rejected.
        if self.activity_type == Category.BIOPROCESS:
            try:
                DryingParams.model_validate(self.extra_data)
            except ValidationError as exc:
                raise ValueError(f"Invalid Bioprocess drying parameters: {exc}") from exc
        # A Mechanization log MAY carry cost-classification parameters, and they
        # are validated when present. extra_data is None on every legacy row and
        # classification is opt-in, so absence is accepted and simply classifies
        # as None — refusing it would break a shipped write path.
        if self.activity_type == Category.MECHANIZATION and self.extra_data is not None:
            try:
                MechanizationParams.model_validate(self.extra_data)
            except ValidationError as exc:
                raise ValueError(f"Invalid Mechanization cost parameters: {exc}") from exc
        return self

class OperationalLog(OperationalLogBase):
    id: int
    timestamp: datetime
    # Set when this log is a reversing entry: the id of the log it offsets.
    reverses_id: Optional[int] = None
    financial_transaction_id: Optional[int] = None
    financial_transaction: Optional[FinancialTransaction] = None
    model_config = ConfigDict(from_attributes=True)

# --- Equipment Schemas ---
class EquipmentBase(BaseModel):
    name: str
    model: Optional[str] = None
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    depreciation_rate: Optional[float] = None

class EquipmentCreate(EquipmentBase):
    pass

class Equipment(EquipmentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- P&L Report Schemas ---
class PnlCategory(BaseModel):
    category: str
    revenue: float
    expenses: float
    net: float

class PnlReport(BaseModel):
    revenue: float
    expenses: float
    gross_margin: float
    categories: List[PnlCategory]

class MonthlyPnlPoint(BaseModel):
    month: str
    revenue: float
    expenses: float

# --- DSS (yield prediction) Schemas ---
# Crops the model is trained on; mirrors ml/dataset.CROPS. Literal gives a clean
# 422 (with the allowed values) when an unknown crop is sent.
DSSCrop = Literal["maize", "rice", "sorghum", "soybean", "cassava"]

class DSSPredictRequest(BaseModel):
    # Bounds mirror ml/dataset.BOUNDS so out-of-range inputs are rejected with a
    # clean 422 before they ever reach the model.
    rainfall: float = Field(..., ge=300, le=2000, description="Seasonal rainfall (mm)")
    fertilizer_used: float = Field(..., ge=0, le=120, description="Nitrogen applied (kg/ha)")
    soil_ph: float = Field(..., ge=4.5, le=8.5, description="Soil pH")
    crop: DSSCrop = Field(..., description="Crop to forecast yield for")

class DSSInterval(BaseModel):
    lower: float
    upper: float

class DSSPredictResponse(BaseModel):
    prediction: float
    unit: str
    confidence: float
    interval: DSSInterval
    feature_importances: Dict[str, float]

# --- DSS (Tier 1: deterministic decision support) Schemas ---
# Metrics derived directly from the farm's real ledger (no model, no synthetic
# inputs). See services/dss_service.py and Chapter 3 §3.6.5.
class YieldByUnit(BaseModel):
    """One unit's worth of a crop's recorded yield. `unit` is None for rows
    saved without a unit (historical free-text entry allowed it)."""
    unit: Optional[str] = None
    quantity: float


class DSSCropMetrics(BaseModel):
    crop: str
    revenue: float
    expenses: float
    gross_margin: float
    # The crop's total yield — but ONLY when a single unit is in play. 0.0 when
    # nothing is recorded, and **None when the crop's yields span two or more
    # units**, because no honest single total exists in that case. Quantities in
    # different units are never summed together; yield_by_unit always carries
    # the real per-unit figures.
    yield_quantity: Optional[float] = None
    yield_unit: Optional[str] = None
    yield_by_unit: List[YieldByUnit] = []
    # None when the crop has no recorded yield quantity (no division by zero),
    # and also None when the yield spans mixed units — a unit cost needs a
    # single denominator. Denominator is the crop's harvest unit (e.g. bags).
    unit_cost_of_production: Optional[float] = None
    # ADDITIVE (ticket 08): Marketable Mass (kg) across the crop's non-reversed
    # drying runs, and a second unit cost denominated per kg of that marketable
    # mass. Both None when the crop has no non-reversed drying runs; the per-kg
    # cost is also None when marketable mass is 0 (no division by zero). These do
    # NOT change unit_cost_of_production — they sit beside it, each with one unit.
    marketable_mass_kg: Optional[float] = None
    unit_cost_per_kg_marketable: Optional[float] = None
    # Break-even yield: the quantity that would have covered this crop's costs
    # at the price actually realised (revenue / yield_quantity). RETROSPECTIVE —
    # it reports what was needed at the achieved price, not a forecast. None
    # whenever no unit price can be derived: mixed units, no yield, or no
    # revenue. `break_even_unit` mirrors yield_unit so the number is never read
    # in the wrong unit.
    break_even_yield: Optional[float] = None
    break_even_unit: Optional[str] = None

class DSSOverall(BaseModel):
    revenue: float
    expenses: float
    gross_margin: float

class DSSDecisionSupport(BaseModel):
    crops: List[DSSCropMetrics]
    overall: DSSOverall

# --- Maintenance Log Schemas ---
class MaintenanceLogBase(BaseModel):
    equipment_id: int
    description: Optional[str] = None
    cost: Optional[float] = None

class MaintenanceLogCreate(MaintenanceLogBase):
    pass

class MaintenanceLog(MaintenanceLogBase):
    id: int
    service_date: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Investor share-link Schemas (ticket 05) ---
class ShareLinkCreate(BaseModel):
    label: Optional[str] = None

class ShareLink(BaseModel):
    """Owner-facing metadata for a share link. Never carries the token — only
    its hash is stored, so an existing link's secret cannot be re-read."""
    id: int
    label: Optional[str] = None
    revoked: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ShareLinkMinted(ShareLink):
    """The mint response — the ONLY place the raw token is ever returned."""
    token: str

# The public, read-only report an investor sees. P&L reuses the standard report;
# crops reuse the deterministic per-crop metrics (for the yield figures).
class InvestorReport(BaseModel):
    farm_name: str
    generated_at: datetime
    pnl: PnlReport
    crops: List[DSSCropMetrics]


# --- Bioprocess read / aggregate responses (ticket 08, Phase 4) ---
# Every field here is derived on read from the stored DryingParams payload by
# bioprocess_service; nothing below is persisted.
class DryingMetrics(BaseModel):
    dry_matter_kg: float
    mass_out_expected_kg: float
    process_loss_kg: float
    process_loss_pct: float
    process_loss_warning: bool
    water_removed_kg: float
    drying_rate_kg_h: float
    specific_drying_rate: float
    moisture_initial_db: float
    moisture_final_db: float
    moisture_ratio_final: float
    newton_k: float
    # Page fit ({n, k, r2_linear, n_used, n_dropped}) or null below 3 usable
    # readings. Dict[str, Any] keeps the integer counts from being coerced.
    page: Optional[Dict[str, Any]] = None
    safe_storage: Optional[bool] = None
    safe_storage_threshold_wb: Optional[float] = None


class BioprocessDetail(BaseModel):
    id: int
    crop: Optional[str] = None
    params: DryingParams
    metrics: DryingMetrics


class BioprocessCropSummary(BaseModel):
    crop: str
    drying_runs: int
    total_mass_in_kg: float
    total_marketable_mass_kg: float
    total_water_removed_kg: float
    mean_drying_rate_kg_h: float
    mean_newton_k_by_method: Dict[str, float]
    # Fraction of this crop's runs at or below the safe-storage threshold; null
    # when the crop is outside the storage table (unknown, never assumed unsafe).
    safe_storage_share: Optional[float] = None


class BioprocessSummary(BaseModel):
    crops: List[BioprocessCropSummary]


# --- Enterprise economics responses (Phase 4) -----------------------------
# Every field below is derived on read by enterprise_service from ledger rows;
# nothing here is persisted, and the depreciation overlay in particular is never
# posted to the ledger. Reversal logs and reversed logs are excluded from every
# aggregation, so neither reaches a numerator or a denominator.


class CostStructure(BaseModel):
    """Section 4.1 for one crop, or farm-wide."""
    variable_cost: float
    # Reported on its own line rather than folded silently into the variable
    # pool: Repairs are genuinely semi-variable, and the reader must be able to
    # see the assumption. It IS part of cash_cost for computation.
    semi_variable_cost: float
    # Recorded FIXED cost — a DEPRECIATION row actually posted to the ledger.
    # Distinct from the allocated-fixed overlay, which is never a ledger entry.
    fixed_cost_recorded: float
    # Cost carrying no Cost Subtype: every legacy row, and every category
    # outside the taxonomy. Never defaulted into a behaviour bucket.
    unclassified_cost: float
    total_recorded_cost: float
    cash_cost: float
    # None when total_recorded_cost is 0 — not 100, not 0. There is no coverage
    # of nothing, and a vacuous 100 would read as "fully classified".
    classification_coverage_pct: Optional[float] = None


class CropCostStructure(CostStructure):
    crop: str


class CostStructureResponse(BaseModel):
    crops: List[CropCostStructure]
    farm: CostStructure


class CropBreakEvenPrice(BaseModel):
    """Section 4.4 for one crop. The two prices do NOT share a cost base."""
    crop: str
    # Short-run continuation threshold: classified variable + semi-variable cost
    # only. Below it, each additional kilogram sold loses money outright.
    break_even_price_cash_ngn_per_kg: Optional[float] = None
    # Long-run survival threshold: EVERY recorded cost (unclassified included)
    # plus the allocated fixed overlay. Always strictly above the cash figure.
    break_even_price_total_ngn_per_kg: Optional[float] = None
    # The four cost lines, reported separately rather than collapsed into two,
    # because unclassified cost sits inside the total figure and outside the
    # cash one and so inflates the gap between them.
    variable_and_semi_variable_cost_ngn: float
    total_recorded_cost_ngn: float
    allocated_fixed_ngn: Optional[float] = None
    total_cost_ngn: float
    # None when the crop has no non-reversed drying run; both prices are then
    # None too — undefined, never a fabricated zero.
    marketable_mass_kg: Optional[float] = None
    classification_coverage_pct: Optional[float] = None


class BreakEvenPriceResponse(BaseModel):
    crops: List[CropBreakEvenPrice]
    # The overlay the allocation was drawn from, so a partial overlay is visible
    # rather than being read as a small true fixed cost.
    period_days: float
    period_fixed_cost_ngn: float
    equipment_count: int
    equipment_unrated_count: int
    total_direct_cost_all_crops: float


class SensitivityRow(BaseModel):
    percentage: int
    marketable_mass_kg: Optional[float] = None
    break_even_price_cash_ngn_per_kg: Optional[float] = None
    break_even_price_total_ngn_per_kg: Optional[float] = None


class CropSensitivity(BaseModel):
    crop: str
    # CONDITIONAL, never predictive: the matrix answers "if you harvest this
    # much, what price covers your costs". It forecasts neither yield nor price,
    # and the interface copy must carry that explicitly.
    conditional: bool
    baseline_marketable_mass_kg: Optional[float] = None
    cash_cost_ngn: float
    total_cost_ngn: float
    rows: List[SensitivityRow]


class SensitivityResponse(BaseModel):
    crops: List[CropSensitivity]


class PartialBudgetRequest(BaseModel):
    """Four quantities, all required and all non-negative: the sign of the
    appraisal lives in which slot a quantity occupies, not in the number."""
    added_revenue_ngn: float = Field(..., ge=0)
    reduced_cost_ngn: float = Field(..., ge=0)
    lost_revenue_ngn: float = Field(..., ge=0)
    added_cost_ngn: float = Field(..., ge=0)


class PartialBudgetResponse(PartialBudgetRequest):
    benefits_ngn: float
    costs_ngn: float
    # Signed and unclamped. A negative net change is a valid and useful answer —
    # it says the change is not worth making.
    net_change_ngn: float


class CropYieldBaseline(BaseModel):
    crop: str
    # Discards exactly ONE maximum observation and ONE minimum instance, so a
    # tied extreme is not removed twice. None below three seasons.
    olympic_average_kg: Optional[float] = None
    grand_average_kg: Optional[float] = None
    n_seasons: int
    n_used: int
    n_discarded: int
    unit: Optional[str] = None
    # Why a figure is null, in words. A bare null leaves the reader unable to
    # tell "too few seasons" from "mixed units" from "nothing recorded".
    reason: Optional[str] = None


class YieldBaselineResponse(BaseModel):
    crops: List[CropYieldBaseline]
