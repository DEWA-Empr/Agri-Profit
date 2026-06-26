from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Any, Dict, List, Literal
from ..core.enums import Category, TransactionType

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
