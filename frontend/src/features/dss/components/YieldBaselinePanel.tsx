import type { CSSProperties } from 'react';
import { LineChart } from 'lucide-react';
import { colors } from '../../../styles/theme';
import type { CropYieldBaseline } from '../../../types/domain';

// Yield baseline for one crop: the Olympic average and the grand average, side
// by side, with the season count that decides whether either exists.
//
// The endpoint (GET /dss/yield-baseline) has been implemented, tested and
// cached by the service worker since the enterprise-economics work; nothing in
// the interface ever read it, so the Olympic average was computed and served
// and no user could see it (docs/STATE_REPORT_2026-08-25.md Sections 3.9, 10.3).
//
// EVERY VALUE HERE COMES OFF THE RESPONSE. Nothing is recomputed, and in
// particular the panel never derives an average of its own to fill a null: a
// null Olympic average is rendered as the backend's own `reason` sentence,
// because one season, mixed units and nothing recorded are three different
// nulls and a dash would collapse them into one (ADR-0002 section 3).

const DASH = '—';

const kg = (value: number, unit?: string | null) =>
  `${value.toLocaleString(undefined, { maximumFractionDigits: 1 })} ${unit ?? 'kg'}`;

const Figure = ({
  label, value, note, strong,
}: { label: string; value: string; note: string; strong?: boolean }) => (
  <div style={{ background: colors.surfaceMuted, border: `0.5px solid ${colors.border}`, borderRadius: '10px', padding: '12px' }}>
    <p style={{ fontSize: '10px', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: colors.textMuted }}>
      {label}
    </p>
    <p style={{ fontSize: strong ? '18px' : '15px', fontWeight: 800, color: value === DASH ? colors.textFaint : colors.textStrong, marginTop: '4px' }}>
      {value}
    </p>
    <p style={{ fontSize: '10px', color: colors.textFaint, marginTop: '4px', lineHeight: 1.5 }}>{note}</p>
  </div>
);

export const YieldBaselinePanel = ({
  crop, card,
}: { crop: CropYieldBaseline; card: CSSProperties }) => {
  const olympic = crop.olympic_average_kg;
  const grand = crop.grand_average_kg;

  return (
    <div style={card}>
      <h3 style={{ fontSize: '12px', fontWeight: 700, color: colors.text, display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '0.5px solid #eee', paddingBottom: '10px', marginBottom: '12px' }}>
        <LineChart size={15} color={colors.primary} /> Yield baseline
      </h3>

      <div className="grid-2" style={{ gap: '11px' }}>
        <Figure
          label="Olympic average"
          value={olympic == null ? DASH : kg(olympic, crop.unit)}
          note="Your seasons with the best one and the worst one set aside, so a freak year does not set the baseline."
          strong
        />
        <Figure
          label="Grand average"
          value={grand == null ? DASH : kg(grand, crop.unit)}
          note="Every season you recorded, including the extremes."
        />
      </div>

      {/* The season count, in every case — including the ones that return no
          average at all. A null standing without its count cannot be read
          either way: one season and ten seasons are different reasons for it. */}
      <div style={{ marginTop: '13px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '10px' }}>
          <span style={{ fontSize: '11px', color: colors.textMuted }}>
            Seasons recorded <span style={{ color: colors.textFaint }}>— a season is a calendar year of yield</span>
          </span>
          <span style={{ fontSize: '11px', fontWeight: 700, color: colors.textBody }}>{crop.n_seasons}</span>
        </div>
        {crop.n_discarded > 0 && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '10px' }}>
            <span style={{ fontSize: '11px', color: colors.textMuted }}>
              Used in the Olympic average <span style={{ color: colors.textFaint }}>— {crop.n_discarded} set aside</span>
            </span>
            <span style={{ fontSize: '11px', fontWeight: 700, color: colors.textBody }}>{crop.n_used}</span>
          </div>
        )}
      </div>

      {/* The backend's own words for why a figure is missing, shown verbatim
          rather than reworded, so the interface cannot soften a refusal into
          something that reads like a number being loaded. */}
      {crop.reason && (
        <p style={{ fontSize: '11.5px', color: colors.textBody, marginTop: '11px', lineHeight: 1.6, background: colors.surfaceMuted, borderRadius: '8px', padding: '10px 12px' }}>
          {crop.reason}
        </p>
      )}

      <p style={{ fontSize: '10px', color: colors.textFaint, marginTop: '10px', lineHeight: 1.55 }}>
        A baseline is a record of what you have already harvested, not a forecast of what you will.
      </p>
    </div>
  );
};
