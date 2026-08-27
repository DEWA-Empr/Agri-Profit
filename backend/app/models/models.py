from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean,
    UniqueConstraint,
)
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
    # What this account may do within its farm — one of core.roles.Role. A
    # string rather than a database enum so adding a role later is a code change
    # rather than a type rewrite. NOT NULL with a default of "owner": every
    # account that predates authorization was the sole user of its own farm, so
    # owner is what each already was (migration a8d4e1c60b27).
    role = Column(String, nullable=False, default="owner", server_default="owner")
    # Access is withdrawn by clearing this, never by deleting the row — the
    # records the user entered must keep their author, and the ledger does not
    # delete. Checked in api/deps.get_current_user, so a deactivated account's
    # existing token stops working on its next request rather than at expiry.
    is_active = Column(Boolean, nullable=False, default=True, server_default="1")
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
    # When the capability stops working on its own. NULL means "never" and is
    # reserved for tokens minted before expiry existed (migration f7b3c2d94e15) —
    # the service gives every NEW token a real expiry, so an unrevoked link
    # cannot outlive the assessment it was shared for. Read only by
    # share_service.get_report_by_token, which treats expired exactly as it
    # treats revoked: a 404, with no hint that the token was ever valid.
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    farm = relationship("Farm")


class OperationalLog(Base):
    __tablename__ = "operational_logs"
    __table_args__ = (
        # Idempotency is per tenant, so uniqueness is too. NULL client_ids are
        # exempt in both Postgres and SQLite (NULLs are never equal), which is
        # what lets every non-offline log leave the column empty.
        UniqueConstraint("farm_id", "client_id", name="uq_operational_logs_farm_client"),
    )

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

    # Client-generated idempotency key for offline writes. Unique PER FARM, not
    # globally: `ledger_service._find_by_client_id` has always matched a replay
    # within the author's own farm, and a global unique index contradicted that
    # — two farms using the same key (the seed script's fixed keys, or any two
    # devices that agree on a scheme) collided at the index, missed the
    # farm-scoped recovery lookup, and surfaced as a 500. The global index
    # predates tenancy: it was written in 544b85dc2d20, before farm_id existed.
    # See migration e6a2b4c7d130.
    client_id = Column(String, nullable=True, index=True)

    # Reversal link (ticket 10): a reversing entry points at the log it offsets
    # (self-referential FK). Ledger records are immutable — a mistaken log is
    # never deleted or edited; a reversal creates an offsetting paired
    # transaction so the full history stays visible and the P&L nets to zero.
    reverses_id = Column(Integer, ForeignKey("operational_logs.id"), nullable=True, index=True)

    # Audit columns (ticket 10). created_at is the immutable record birth and
    # updated_at is stamped on any future mutation — distinct from `timestamp`,
    # which is the domain event time the farmer is recording.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

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

    # Audit columns (ticket 10) — see OperationalLog. The financial ledger is
    # append-only: a transaction is corrected by an offsetting reversal, never
    # deleted or edited.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    operational_log = relationship("OperationalLog", back_populates="financial_transaction", uselist=False)

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    model = Column(String)
    purchase_date = Column(DateTime)
    purchase_price = Column(Float)
    # Annual percentage: 10.0 means 10%/yr, the unit the farmer enters and
    # reads. It is converted to a fraction exactly once, in
    # dss_service.depreciation_rate_as_fraction, where equipment rows are
    # assembled into the depreciation overlay's input. Nowhere else divides.
    # Nullable: an asset entered without a rate is excluded from the overlay
    # and counted there, never charged at zero.
    depreciation_rate = Column(Float)
    # Stamped when the asset is corrected; NULL means "as originally entered".
    # A correction moves the depreciation overlay and therefore both break-even
    # prices, so the fact that one happened must be visible rather than silent
    # (migration b9e5f30c74a1). Not `onupdate=`: that would fire on any flush
    # touching the row, and only a deliberate correction should be recorded.
    updated_at = Column(DateTime(timezone=True), nullable=True)

class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"))
    service_date = Column(DateTime, server_default=func.now())
    description = Column(Text)
    cost = Column(Float)

    equipment = relationship("Equipment")
