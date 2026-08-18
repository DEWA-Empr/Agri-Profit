from pydantic import BaseModel, Field, ConfigDict, EmailStr, model_validator, ValidationError
from datetime import datetime
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
    def _validate_bioprocess_payload(self) -> "OperationalLogCreate":
        # Structured validation applies ONLY to Bioprocess logs. Every other
        # activity type keeps extra_data as an arbitrary, unvalidated dict —
        # exactly as before. A Bioprocess log must carry a valid drying payload;
        # a missing or malformed one is a 422 at the edge, never a 500 (the
        # nested ValidationError is re-raised as a ValueError so Pydantic folds
        # it into this model's own validation error).
        if self.activity_type == Category.BIOPROCESS:
            try:
                DryingParams.model_validate(self.extra_data)
            except ValidationError as exc:
                raise ValueError(f"Invalid Bioprocess drying parameters: {exc}") from exc
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
