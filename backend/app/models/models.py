from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.enums import Category, TransactionType
from .database import Base

class OperationalLog(Base):
    __tablename__ = "operational_logs"

    id = Column(Integer, primary_key=True, index=True)
    activity_type = Column(Enum(Category), nullable=False)
    description = Column(Text)
    quantity = Column(Float)
    unit = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Bioprocess parameters or custom data
    extra_data = Column(JSON, nullable=True) # e.g., {"drying_time": 48, "humidity": 12.5}
    
    # Link to financial transaction
    financial_transaction_id = Column(Integer, ForeignKey("financial_transactions.id"), nullable=True)
    financial_transaction = relationship("FinancialTransaction", back_populates="operational_log")

class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    category = Column(Enum(Category), nullable=False)
    description = Column(Text)
    tax_category = Column(String)  # For automated tax categorization
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    operational_log = relationship("OperationalLog", back_populates="financial_transaction", uselist=False)

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    model = Column(String)
    purchase_date = Column(DateTime)
    purchase_price = Column(Float)
    depreciation_rate = Column(Float)  # Annual percentage

class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"))
    service_date = Column(DateTime, server_default=func.now())
    description = Column(Text)
    cost = Column(Float)
    
    equipment = relationship("Equipment")
