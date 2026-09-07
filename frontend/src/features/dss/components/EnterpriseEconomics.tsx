import { useEffect, useMemo, useState, type CSSProperties } from 'react';
import { Sprout } from 'lucide-react';
import { colors } from '../../../styles/theme';
import { dssService } from '../../../lib/apiClient';
import { CostStructurePanel } from './CostStructurePanel';
import { BreakEvenPricePanel } from './BreakEvenPricePanel';
import { SensitivityTable } from './SensitivityTable';
import { PartialBudgetForm } from './PartialBudgetForm';
import { YieldBaselinePanel } from './YieldBaselinePanel';
import type {
  CostStructureResponse, BreakEvenPriceResponse, SensitivityResponse,
  YieldBaselineResponse,
} from '../../../types/domain';

// Enterprise economics, on the DSS view.
//
// WHY THIS SITS BEHIND ITS OWN HEADING. Everything above it on this page is
// Tier 2 — a Random Forest trained on generated data that has never seen this
// farm — and the page already goes to some length to say so beside the R² and
// the MAE. Everything below is Tier 1: arithmetic over the farm's own ledger,
// with no model anywhere near it. Running the two together without a break
// would put a measured cost structure and a synthetic forecast in one visual
// column and invite the reader to grant them the same standing. The divider and
// its sentence are the whole point of the separation.
//
// All three reads are fetched once, unfiltered, and the crop is chosen on the
// client. The farm-wide cost structure is computed over every crop regardless
// of any filter, so a filtered fetch would buy nothing and cost a round trip
// per crop switch on exactly the connection least able to afford one.

// The farm-wide selection. A sentinel rather than a nullable crop because the
// selector's value has to be a string either way, and a sentinel that cannot
// collide with a crop name is cheaper to read than an empty string that also
// has to mean "nothing chosen yet".
const FARM = '__farm__';

export const EnterpriseEconomics = ({ card }: { card: CSSProperties }) => {
  const [structure, setStructure] = useState<CostStructureResponse | null>(null);
  const [breakEven, setBreakEven] = useState<BreakEvenPriceResponse | null>(null);
  const [sensitivity, setSensitivity] = useState<SensitivityResponse | null>(null);
  const [baseline, setBaseline] = useState<YieldBaselineResponse | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [failed, setFailed] = useState(false);
  // ONLY the user's explicit choice is state. The selection actually shown is
  // derived below — a default that lives in state has to be synchronised into
  // it by an effect, and an effect that sets state on data arriving is a
  // cascading render for something the render already knows.
  const [chosen, setChosen] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      dssService.getCostStructure(),
      dssService.getBreakEvenPrice(),
      dssService.getSensitivity(),
      dssService.getYieldBaseline(),
    ])
      .then(([cs, be, se, yb]) => {
        setStructure(cs.data);
        setBreakEven(be.data);
        setSensitivity(se.data);
        setBaseline(yb.data);
      })
      .catch(() => setFailed(true))
      .finally(() => setLoaded(true));
  }, []);

  const crops = useMemo(() => structure?.crops.map((c) => c.crop) ?? [], [structure]);

  // The page opens farm-wide. Not a fallback but the default reading: the farm
  // is the enterprise the reader came for, and any single crop picked for them
  // would be an arbitrary one. The user's choice wins once made, guarded
  // against a stale crop surviving a reload that no longer has it.
  const selection = (chosen != null && (chosen === FARM || crops.includes(chosen))) ? chosen : FARM;
  const isFarm = selection === FARM;

  // Rendered AS RECEIVED from /dss/cost-structure. The farm block is the
  // service's own aggregation over every crop's cost entries — not these panels
  // re-adding the per-crop rows, which would average averages and produce a
  // coverage and a ratio that are not the farm's.
  const selectedStructure = isFarm
    ? structure?.farm
    : structure?.crops.find((c) => c.crop === selection);
  const selectedBreakEven = isFarm ? undefined : breakEven?.crops.find((c) => c.crop === selection);
  const selectedSensitivity = isFarm ? undefined : sensitivity?.crops.find((c) => c.crop === selection);
  // The yield baseline is keyed on crops that have recorded YIELD, so a
  // cost-only crop (tomato, sorghum) legitimately has no row here while it does
  // have a cost structure. Absent means absent — the panel is not rendered
  // rather than rendered full of dashes.
  const selectedBaseline = isFarm ? undefined : baseline?.crops.find((c) => c.crop === selection);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      {/* The Tier 1 / Tier 2 divider. */}
      <div style={{ borderTop: `1px solid ${colors.border}`, paddingTop: '18px' }}>
        <h2 style={{ fontSize: '14px', fontWeight: 800, color: colors.text, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sprout size={16} color={colors.primary} /> Enterprise economics
        </h2>
        <p style={{ fontSize: '11px', color: colors.textMuted, marginTop: '6px', lineHeight: 1.65, maxWidth: '78ch' }}>
          Everything below is worked out from <strong>your own records</strong> — the operations you logged and the
          money you entered against them. No model is involved and nothing here is a forecast, which is the opposite
          of the yield prediction above.
        </p>
      </div>

      {!loaded ? (
        <p style={{ fontSize: '12px', color: colors.textMuted }}>Loading your cost figures…</p>
      ) : failed ? (
        <div style={card}>
          <p style={{ fontSize: '12px', color: colors.warn, fontWeight: 600 }}>Your cost figures could not be loaded.</p>
          <p style={{ fontSize: '11px', color: colors.textMuted, marginTop: '6px', lineHeight: 1.6 }}>
            These panels read the ledger, so they need a connection the first time. The partial budget below does not
            and still works.
          </p>
        </div>
      ) : crops.length === 0 ? (
        <div style={card}>
          <p style={{ fontSize: '12px', color: colors.textBody, fontWeight: 600 }}>No crop costs recorded yet.</p>
          <p style={{ fontSize: '11px', color: colors.textMuted, marginTop: '6px', lineHeight: 1.6 }}>
            Tag your operations with a crop and record what they cost. Cost structure, both break-even prices and the
            sensitivity table appear here as soon as there is something to compute them from.
          </p>
        </div>
      ) : (
        <>
          {/* One selector for all the ledger panels. They are several views of
              the same crop's costs and splitting the choice across them would
              let the reader compare a break-even price for one crop against a
              cost structure for another. The farm-wide option leads because it
              is the default, and because the crops under it are the parts of
              the whole it names. */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <label htmlFor="ee-crop" style={{ fontSize: '11px', fontWeight: 600, color: colors.labelText }}>Crop</label>
            <select
              id="ee-crop"
              value={selection}
              onChange={(e) => setChosen(e.target.value)}
              style={{ padding: '7px 10px', borderRadius: '7px', border: `1px solid ${colors.borderInput}`, fontSize: '12px', cursor: 'pointer', textTransform: 'capitalize', minWidth: '150px' }}
            >
              <option value={FARM}>All crops (farm-wide)</option>
              {crops.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            <span style={{ fontSize: '10.5px', color: colors.textFaint }}>
              {crops.length} crop{crops.length === 1 ? '' : 's'} in your ledger
            </span>
          </div>

          <div className="split-row">
            {selectedStructure && (
              <CostStructurePanel structure={selectedStructure} breakEven={selectedBreakEven} card={card} />
            )}
            {selectedBreakEven && breakEven && (
              <BreakEvenPricePanel crop={selectedBreakEven} meta={breakEven} card={card} />
            )}
            {/* WHY THERE IS NO FARM-WIDE BREAK-EVEN PRICE. Not an omission to
                be filled in later — the divisor does not exist. */}
            {isFarm && (
              <div style={card}>
                <p style={{ fontSize: '11.5px', color: colors.textBody, lineHeight: 1.65 }}>
                  Break-even prices are shown per crop. Both prices are per kilogram of marketable output, and
                  marketable mass belongs to a single crop — cowpea and maize cannot be added into one saleable
                  mass. Select a crop above to see its break-even prices.
                </p>
              </div>
            )}
          </div>

          {selectedSensitivity && sensitivity && (
            <SensitivityTable crop={selectedSensitivity} meta={sensitivity} card={card} />
          )}

          {selectedBaseline && <YieldBaselinePanel crop={selectedBaseline} card={card} />}
        </>
      )}

      {/* Always rendered, including when the reads above failed: it needs no
          ledger data and no connection. */}
      <PartialBudgetForm card={card} />
    </div>
  );
};
