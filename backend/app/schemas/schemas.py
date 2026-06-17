from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Any, Dict
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
