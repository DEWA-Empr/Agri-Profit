# AgriProfit

An integrated farm record management and decision-support platform for Nigerian small and medium-scale farming enterprises. Unifies operational field records with a financial ledger to enable profitability analysis and stakeholder reporting.

## Language

### Operations

**Operational Log**:
A timestamped record of a physical farm activity — seed application, fertilizer, harvest, labour, post-harvest processing. The primary unit of operational data entry. Every Operational Log automatically produces a paired Financial Transaction.
_Avoid_: Logbook entry, activity record, farm log

**Physical Input**:
A tangible farm resource consumed in production: seeds, fertilizer, water, labour hours, or fuel. Physical inputs correspond to Operational Logs with Activity Category Seed, Fertilizer, Labour, or Mechanization and are recorded as expense Financial Transactions.
_Avoid_: Farm resource, farm input, consumable

**Activity Category**:
The classification shared by an Operational Log and its paired Financial Transaction. One of: Seed, Fertilizer, Labour, Mechanization, Yield, Bioprocess, Other.
_Avoid_: Activity type, log type, transaction type

**Yield**:
The measurable output from a crop or livestock production cycle. Recorded as an Operational Log with Activity Category "Yield" and paired with a revenue Financial Transaction.
_Avoid_: Harvest, output, produce

**Bioprocess**:
A post-harvest processing step applied to Yield before it reaches market (drying, starch hydrolysis, storage conditioning). Recorded as an Operational Log with Activity Category "Bioprocess" and optional structured parameters (e.g. drying time, humidity).
_Avoid_: Post-harvest activity, processing step

### Finance

**Financial Transaction**:
The monetary record automatically created alongside every Operational Log. Classified as either an expense (debit) or revenue (credit), tagged with an Activity Category and an optional Tax Category. The ledger is single-entry: there is no enforced debit/credit pairing.
_Avoid_: Ledger entry, accounting record, double-entry record

**Gross Margin**:
Total revenue (sum of credit Financial Transactions) minus total expenses (sum of debit Financial Transactions). The primary financial health metric of the farm.
_Avoid_: Profit, net income, net margin

**Tax Category**:
A free-text label on a Financial Transaction classifying it for regulatory tax reporting (e.g. "Agriculture Inputs", "Sales Revenue").
_Avoid_: Tax code, tax classification

**Depreciation**:
The annual reduction in an Equipment's book value, expressed as a percentage rate of purchase price.
_Avoid_: Wear-and-tear (wear-and-tear is a physical phenomenon; depreciation is its financial expression)

### Equipment

**Equipment**:
A piece of farm machinery tracked for acquisition cost, Depreciation, and maintenance history.
_Avoid_: Machine, asset, vehicle

**Maintenance Log**:
A record of a service or repair event on a specific piece of Equipment, including date, description, and cost.
_Avoid_: Service record, repair log, maintenance record

### Intelligence

**Predictive DSS**:
A two-tier decision-support system. **Tier 1 (deterministic rule-based):** computes unit cost of production and per-crop Gross Margin directly from the farm's real Operational Logs and Financial Transactions. **Tier 2 (statistical forecast, optional):** a RandomForest yield model trained on representative _synthetic_ data (`backend/app/ml/dataset.py`), used while a farm accumulates enough real historical records to retrain on later. The forecast tier does **not** learn from the farm's own records in this release.
_Avoid_: AI system, self-learning model, neural network
