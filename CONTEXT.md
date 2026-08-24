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

**Mechanization**:
The use of powered machinery or hired machine services in production — land preparation, spraying, threshing, transport. Recorded as an Operational Log with Activity Category Mechanization; a cost-bearing Mechanization log carries a Cost Subtype.
_Avoid_: Mechanisation, machine work, tractor work

**Bioprocess**:
A post-harvest processing step applied to Yield before it reaches market (drying, starch hydrolysis, storage conditioning). Recorded as an Operational Log with Activity Category "Bioprocess" and optional structured parameters (e.g. drying time, humidity). The first implemented process type is the Drying Run. A cost-bearing Bioprocess log carries a Cost Subtype.
_Avoid_: Post-harvest activity, processing step

**Drying Run**:
A single post-harvest drying operation on one crop lot, recorded as an Operational Log with Activity Category Bioprocess, carrying the lot's inlet and outlet mass, inlet and outlet moisture content, duration, air temperature and drying method.
_Avoid_: Drying session, dry-down, batch

**Moisture Content**:
The mass fraction of water in a crop lot, entered on a **wet basis** (mass of water ÷ total mass) because that is what field moisture meters report and what buyers price against. Converted to dry basis internally for drying-kinetics modelling.
_Avoid_: Humidity, water content, moisture level

**Marketable Mass**:
The outlet mass of a crop after its Drying Runs; the quantity the farm can actually sell. Where a crop has Drying Runs, unit cost of production is also reported against Marketable Mass, alongside the harvest-unit figure.
_Avoid_: Net weight, final yield, saleable yield

**Process Loss**:
The difference between the outlet mass predicted by dry-matter conservation and the outlet mass actually recorded, attributable to spillage, handling and over-drying. A data-quality and efficiency signal, not a financial entry.
_Avoid_: Shrinkage, wastage, drying loss

### Finance

**Financial Transaction**:
The monetary record automatically created alongside every Operational Log. Classified as either an expense (debit) or revenue (credit), tagged with an Activity Category and an optional Tax Category. The ledger is single-entry: there is no enforced debit/credit pairing. Financial Transactions are **immutable** — once recorded they are never edited or deleted; a mistaken entry is corrected only by a Reversal.
_Avoid_: Ledger entry, accounting record, double-entry record

**Reversal**:
The correction mechanism for a mistaken Operational Log. Rather than deleting the log (records are immutable), a Reversal posts a new Operational Log paired with a *contra* Financial Transaction — the **same** type (debit or credit), amount and Activity Category as the original — linked back to it. The reports subtract a Reversal from the same pile its type feeds, so a reversed expense returns that category's expenses to their prior value (and a reversed income returns its revenue), leaving the opposite pile *and* Gross Margin correct — not just the margin. Both the original and the Reversal remain visible in the audit trail. A Reversal carries no crop or quantity, so it corrects the finances without distorting yield analytics. An already-reversed log, or a Reversal itself, cannot be reversed again.
_Avoid_: Delete, void, undo, cancel

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

### Cost structure

**Cost Subtype**:
A classification carried on a cost-bearing Operational Log identifying whether the expense scales with production. For Mechanization the set is Fuel, Lubricants, Repairs, Machinery Hire and Depreciation, with equivalent sets for the other Activity Categories. Carried as a structured parameter on the Operational Log, not as a column on the Financial Transaction.
_Avoid_: Cost type, expense class, cost code

**Cost Behaviour**:
The derived property of a Cost Subtype describing how it responds to output: Variable (scales with production), Semi-variable (a fixed component plus a variable component), or Fixed (constant regardless of output). A log carrying no Cost Subtype is Unclassified and enters no behaviour bucket — it is never defaulted into one.
_Avoid_: Fixed/variable, cost nature, direct/indirect

**Classification Coverage**:
The proportion of a crop's or the farm's recorded cost that carries a Cost Subtype. Reported alongside every figure derived from Cost Behaviour, because a figure computed over partially classified cost is a weaker claim than one computed over fully classified cost and the reader must be able to see which they have.
_Avoid_: Completeness, data quality score, coverage

**Break-even Price to Cover Cash Cost**:
The price per kilogram of Marketable Mass at which a crop's classified Variable and Semi-variable cost would be recovered. The short-run continuation threshold: below it, each further kilogram sold loses money outright. A conditional figure, never a price forecast, and distinct both from Break-even Price to Cover Total Cost and from the retrospective break-even yield.
_Avoid_: Break-even, breakeven price, VC breakeven

**Break-even Price to Cover Total Cost**:
The price per kilogram of Marketable Mass at which every recorded cost plus Allocated Fixed Cost would be recovered. The long-run survival threshold. It sits at or above Break-even Price to Cover Cash Cost, and the gap between the two is the fixed-cost burden the farm carries whether or not it plants.
_Avoid_: Break-even, full cost price, TC breakeven

**Allocated Fixed Cost**:
A crop's share of the farm's periodic fixed cost, derived at report time from Equipment Depreciation and apportioned in proportion to that crop's recorded direct cost. Never a Financial Transaction.
_Avoid_: Overhead, fixed cost, indirect cost

**Partial Budget**:
An appraisal of a single proposed change, computed as (additional revenue + reduced cost) − (lost revenue + additional cost). It evaluates only the quantities the change affects, so it needs no complete enterprise budget.
_Avoid_: ROI, cost-benefit analysis, business case

**Olympic Average Yield**:
A yield baseline computed by discarding exactly one highest and one lowest observation from a crop's recorded season yields and averaging the remainder. Requires at least three seasons; undefined below that.
_Avoid_: Trimmed mean, adjusted average, normalised yield

### Intelligence

**Predictive DSS**:
A two-tier decision-support system. **Tier 1 (deterministic rule-based):** computes unit cost of production and per-crop Gross Margin directly from the farm's real Operational Logs and Financial Transactions. **Tier 2 (statistical forecast, optional):** a RandomForest yield model trained on representative _synthetic_ data (`backend/app/ml/dataset.py`), used while a farm accumulates enough real historical records to retrain on later. The forecast tier does **not** learn from the farm's own records in this release.
_Avoid_: AI system, self-learning model, neural network
