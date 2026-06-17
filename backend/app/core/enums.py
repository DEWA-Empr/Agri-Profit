import enum

class TransactionType(str, enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"

class Category(str, enum.Enum):
    SEED = "seed"
    FERTILIZER = "fertilizer"
    LABOUR = "labour"
    MECHANIZATION = "mechanization"
    YIELD = "yield"
    BIOPROCESS = "bioprocess"
    OTHER = "other"
