from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.enums import Category, TransactionType
from .database import Base


class Farm(Base):
    """A tenant. Every domain record belongs to exactly one farm, and a user
    only ever sees rows carrying their own farm_id (the data boundary of
    Objective 3). Pre-auth records are backfilled into a seeded "Legacy Farm"
    by the auth migration so no historical data is lost or leaked."""
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="farm")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    # bcrypt hash via passlib — the plaintext password is never stored.
    hashed_password = Column(String, nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    farm = relationship("Farm", back_populates="users")


class ShareToken(Base):
    """A revocable, read-only capability granting an investor/lender access to a
    single farm's P&L + yield report without an account (ticket 05).

    Only a SHA-256 hash of the token is stored — the raw token is shown to the
    owner exactly once, at mint time. A database compromise therefore cannot
    reveal a usable share link (sha256 is preimage-resistant), which is the
    point of a trusted data-sharing story: the secret lives only in the URL the
    owner chooses to share.

    The token is bound to a farm solely by this row's farm_id; the public report
    endpoint derives the farm from the token and never accepts a farm from the
    caller, so a token cannot address any farm but its own.
    """
    __tablename__ = "share_tokens"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, index=True)
    # SHA-256 hex digest of the opaque token; unique so lookup is exact.
    token_hash = Column(String, unique=True, nullable=False, index=True)
    label = Column(String, nullable=True)  # optional note, e.g. "First Bank"
    revoked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    farm = relationship("Farm")


class OperationalLog(Base):
    __tablename__ = "operational_logs"

    id = Column(Integer, primary_key=True, index=True)
    # Owning tenant. NOT NULL: every log is stamped with the author's farm at
    # creation, and all reads are filtered by it (see services/ledger_service).
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, index=True)
    activity_type = Column(Enum(Category), nullable=False)
    description = Column(Text)
    quantity = Column(Float)
    unit = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Bioprocess parameters or custom data
    extra_data = Column(JSON, nullable=True) # e.g., {"drying_time": 48, "humidity": 12.5}

    # Crop this activity belongs to (e.g. "maize"). Nullable: pre-existing logs
    # and app-entered records without a crop fall into the "Unspecified" bucket
    # of the Tier-1 decision-support report. Indexed for per-crop grouping.
    crop = Column(String, nullable=True, index=True)

    client_id = Column(String, unique=True, nullable=True, index=True)

    # Link to financial transaction
    financial_transaction_id = Column(Integer, ForeignKey("financial_transactions.id"), nullable=True)
    financial_transaction = relationship("FinancialTransaction", back_populates="operational_log")

class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"

    id = Column(Integer, primary_key=True, index=True)
    # Owning tenant. The P&L / monthly / DSS reports query this table directly,
    # so it carries farm_id in its own right rather than only via its log.
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, index=True)
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
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    model = Column(String)
    purchase_date = Column(DateTime)
    purchase_price = Column(Float)
    depreciation_rate = Column(Float)  # Annual percentage

class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"))
    service_date = Column(DateTime, server_default=func.now())
    description = Column(Text)
    cost = Column(Float)

    equipment = relationship("Equipment")
