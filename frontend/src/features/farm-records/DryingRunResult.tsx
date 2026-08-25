import { lazy, Suspense, useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, Droplets, HelpCircle } from 'lucide-react';
import { bioprocessService } from '../../lib/apiClient';
import type { BioprocessDetail } from '../../types/domain';
import { colors } from '../../styles/theme';

// Result panel for a drying run that has just been saved. Everything shown here
// is computed server-side on read (GET /bioprocess/{id}) from the parameters
// entered — nothing is stored, and nothing is recomputed in the browser, so the
// figures a farmer sees are the same ones the DSS uses.

// Lazy, like the dashboard's charts: recharts is by far the heaviest thing on
// this route, and a farmer entering a seed cost should not download a charting
// library to do it. The chunk arrives only when a drying run is actually shown.
const DryingCurveChart = lazy(() =>
  import('./DryingCurveChart').then((m) => ({ default: m.DryingCurveChart })),
);

const kg = (n: number) => `${n.toFixed(2)} kg`;
const pct = (n: number) => `${n.toFixed(2)}%`;

const Metric = ({ label, value, hint }: { label: string; value: string; hint?: string }) => (
  <div style={{ background: colors.surfaceMuted, border: `0.5px solid ${colors.border}`, borderRadius: '10px', padding: '12px' }}>
    <div style={{ fontSize: '10px', fontWeight: 600, color: colors.labelText, textTransform: 'uppercase', letterSpacing: '0.4px' }}>{label}</div>
    <div style={{ fontSize: '16px', fontWeight: 700, color: colors.textStrong, marginTop: '4px' }}>{value}</div>
    {hint && <div style={{ fontSize: '10px', color: colors.textMuted, marginTop: '3px' }}>{hint}</div>}
  </div>
);

// Pass / fail / unknown. An unknown crop shows as unknown — never as a failure,
// because the backend returns null rather than assuming a threshold.
const SafeStorageChip = ({ safe, threshold }: { safe?: boolean | null; threshold?: number | null }) => {
  const spec = safe === null || safe === undefined
    ? { bg: 'rgba(136,136,136,0.10)', fg: colors.textMuted, Icon: HelpCircle, text: 'No safe-storage threshold published for this crop' }
    : safe
      ? { bg: 'rgba(99,153,34,0.10)', fg: colors.primaryDark, Icon: CheckCircle2, text: `Safe to store — at or below ${threshold}% wet basis` }
      : { bg: 'rgba(192,57,43,0.08)', fg: colors.danger, Icon: AlertTriangle, text: `Not safe to store — above the ${threshold}% wet-basis threshold` };
  const { Icon } = spec;
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: spec.bg, color: spec.fg, borderRadius: '8px', padding: '10px 12px', fontSize: '12px', fontWeight: 600 }}>
      <Icon size={16} /> {spec.text}
    </div>
  );
};

export const DryingRunResult = ({ logId, onDone }: { logId: number; onDone: () => void }) => {
  const [detail, setDetail] = useState<BioprocessDetail | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    bioprocessService.getRun(logId)
      .then((res) => { if (active) setDetail(res.data); })
      .catch(() => { if (active) setError('The run was saved, but its metrics could not be loaded.'); });
    return () => { active = false; };
  }, [logId]);

  const card: React.CSSProperties = { background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, padding: '18px', display: 'flex', flexDirection: 'column', gap: '14px' };
  const doneButton = (
    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
      <button type="button" onClick={onDone} style={{ padding: '8px 16px', borderRadius: '8px', border: 'none', background: colors.primaryDark, color: colors.onPrimary, fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}>
        Done
      </button>
    </div>
  );

  if (error) {
    return <div style={card}><p style={{ fontSize: '12px', color: colors.warn, margin: 0 }}>{error}</p>{doneButton}</div>;
  }
  if (!detail) {
    return <div style={card}><p style={{ fontSize: '12px', color: colors.textMuted, margin: 0 }}>Computing drying metrics…</p></div>;
  }

  const m = detail.metrics;
  const p = detail.params;

  return (
    <div style={card} className="fade-in-up">
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Droplets size={16} color={colors.primaryDark} />
        <h3 style={{ fontSize: '13px', fontWeight: 700, color: colors.textStrong, margin: 0 }}>
          Drying run saved{detail.crop ? ` — ${detail.crop}` : ''}
        </h3>
      </div>

      <SafeStorageChip safe={m.safe_storage} threshold={m.safe_storage_threshold_wb} />

      <div className="grid-3" style={{ gap: '10px' }}>
        {/* A water balance (water in − water out), NOT the mass difference: with
            process loss the two diverge, and the difference is dry matter that
            left the system rather than water that evaporated. */}
        <Metric label="Water removed" value={kg(m.water_removed_kg)} hint="water in − water out" />
        <Metric label="Drying rate" value={`${m.drying_rate_kg_h.toFixed(3)} kg/h`} hint="water removed ÷ hours" />
        <Metric
          label="Process loss"
          value={`${kg(m.process_loss_kg)} (${pct(m.process_loss_pct)})`}
          hint={`vs ${kg(m.mass_out_expected_kg)} predicted by dry-matter balance`}
        />
      </div>

      {m.process_loss_warning && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(160,92,0,0.07)', color: colors.warn, borderRadius: '8px', padding: '10px 12px', fontSize: '11px' }}>
          <AlertTriangle size={15} />
          Process loss is over 5% of the predicted outlet mass. Check the weights and moisture readings — this is usually a measurement problem, not lost grain.
        </div>
      )}

      {/* The drying curve, when there is one to draw. With no intermediate
          readings the only points are the run's start and end, and joining two
          points would draw a straight line that asserts a linear fall nobody
          measured — so the panel says what is missing instead of drawing it.
          Same rule as the Page fit hint below. */}
      {(p.readings?.length ?? 0) > 0 ? (
        <div>
          <div style={{ fontSize: '10px', fontWeight: 600, color: colors.labelText, textTransform: 'uppercase', letterSpacing: '0.4px', marginBottom: '6px' }}>
            Drying curve · measured
          </div>
          <Suspense fallback={<div style={{ height: 190, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', color: colors.textMuted }}>Loading chart…</div>}>
            <DryingCurveChart params={p} />
          </Suspense>
          <div style={{ fontSize: '10px', color: colors.textFaint, marginTop: '2px' }}>
            Start, your {p.readings!.length} reading{p.readings!.length === 1 ? '' : 's'}, and the final moisture — measured points only, no fitted model.
          </div>
        </div>
      ) : (
        <div style={{ fontSize: '11px', color: colors.textMuted, background: colors.surfaceMuted, border: `0.5px solid ${colors.border}`, borderRadius: '10px', padding: '12px', lineHeight: 1.5 }}>
          No drying curve: this run has no intermediate moisture readings. Add a reading each time you check the
          meter and the curve — and the Page-model fit — appear here.
        </div>
      )}

      <div className="grid-3" style={{ gap: '10px' }}>
        <Metric label="Dry matter" value={kg(m.dry_matter_kg)} hint="conserved through drying" />
        <Metric label="Moisture ratio" value={m.moisture_ratio_final.toFixed(4)} hint={`${m.moisture_initial_db.toFixed(2)}% → ${m.moisture_final_db.toFixed(2)}% dry basis`} />
        <Metric
          label="Newton k"
          value={`${m.newton_k.toFixed(6)} /h`}
          hint={m.page ? `Page: n=${m.page.n.toFixed(4)}, k=${m.page.k.toFixed(4)} (R²=${m.page.r2_linear.toFixed(4)})` : 'Page fit needs 3+ intermediate readings'}
        />
      </div>

      {doneButton}
    </div>
  );
};
