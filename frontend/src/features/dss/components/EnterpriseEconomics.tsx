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

export const EnterpriseEconomics = ({ card }: { card: CSSProperties }) => {
  const [structure, setStructure] = useState<CostStructureResponse | null>(null);
  const [breakEven, setBreakEven] = useState<BreakEvenPriceResponse | null>(null);
  const [sensitivity, setSensitivity] = useState<SensitivityResponse | null>(null);
  const [baseline, setBaseline] = useState<YieldBaselineResponse | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [failed, setFailed] = useState(false);
  // ONLY the user's explicit choice is state. The crop actually shown is
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

  // Open on a crop that actually has both prices, falling back to the first
  // crop alphabetically. Not to flatter the demo — every crop stays one click
  // away in the selector, nulls and all — but because opening on a column of em
  // dashes teaches the reader nothing about what the panels do, and the null
  // case reads as breakage before it reads as an honest refusal.
  const fallbackCrop = useMemo(() => {
    const withPrice = breakEven?.crops.find((c) => c.break_even_price_cash_ngn_per_kg != null);
    return withPrice?.crop ?? crops[0] ?? null;
  }, [breakEven, crops]);

  // The user's choice wins; the fallback fills in until they make one. Guarded
  // against a stale choice surviving a reload that no longer has that crop.
  const crop = (chosen != null && crops.includes(chosen)) ? chosen : fallbackCrop;

  const selectedStructure = structure?.crops.find((c) => c.crop === crop);
  const selectedBreakEven = breakEven?.crops.find((c) => c.crop === crop);
  const selectedSensitivity = sensitivity?.crops.find((c) => c.crop === crop);
  // The yield baseline is keyed on crops that have recorded YIELD, so a
  // cost-only crop (tomato, sorghum) legitimately has no row here while it does
  // have a cost structure. Absent means absent — the panel is not rendered
  // rather than rendered full of dashes.
  const selectedBaseline = baseline?.crops.find((c) => c.crop === crop);

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
          {/* One selector for all three ledger panels. They are three views of
              the same crop's costs and splitting the choice across them would
              let the reader compare a break-even price for one crop against a
              cost structure for another. */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <label htmlFor="ee-crop" style={{ fontSize: '11px', fontWeight: 600, color: colors.labelText }}>Crop</label>
            <select
              id="ee-crop"
              value={crop ?? ''}
              onChange={(e) => setChosen(e.target.value)}
              style={{ padding: '7px 10px', borderRadius: '7px', border: `1px solid ${colors.borderInput}`, fontSize: '12px', cursor: 'pointer', textTransform: 'capitalize', minWidth: '150px' }}
            >
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
