from pydantic import BaseModel, Field, ConfigDict, EmailStr
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

class OperationalLog(OperationalLogBase):
    id: int
    timestamp: datetime
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
class DSSCropMetrics(BaseModel):
    crop: str
    revenue: float
    expenses: float
    gross_margin: float
    yield_quantity: float
    yield_unit: Optional[str] = None
    # None when the crop has no recorded yield quantity (no division by zero).
    unit_cost_of_production: Optional[float] = None

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
