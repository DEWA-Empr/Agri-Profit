import { Lightbulb } from 'lucide-react';
import { colors, accents, cardShadow, type AccentKey } from '../../../styles/theme';
import { SectionHeader } from './SectionHeader';

interface Decision { tone: AccentKey; title: string; body: string; }

// NOTE: illustrative content — the rules engine that would derive these from
// the ledger and field data isn't built yet. Layout/visual pattern is real.
const DECISIONS: Decision[] = [
  { tone: 'alert', title: 'East Paddock margin at 11%', body: 'Below the 15% threshold. Review soybean input mix and irrigation before the next cycle.' },
  { tone: 'opportunity', title: 'Fertilizer down 8% this month', body: 'Favourable pre-buy window for spring nitrogen. Locking now saves an est. ₦14,200.' },
  { tone: 'insight', title: 'Maize outperforming soybean', body: 'Maize fields are running ~6 pts higher margin this season across 540 acres.' },
  { tone: 'window', title: 'Planting window opens in 6 days', body: 'South Flats reaches optimal soil temperature & moisture for the next rotation.' },
];

export const DecisionSupport = () => (
  <div style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, boxShadow: cardShadow, padding: '20px', display: 'flex', flexDirection: 'column' }}>
    <SectionHeader
      icon={<Lightbulb size={15} color={colors.primary} />}
      title="Decision support"
      subtitle={`${DECISIONS.length} active signals`}
    />

    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      {DECISIONS.map((d) => {
        const a = accents[d.tone];
        return (
          <div key={d.title} style={{ background: a.bg, borderLeft: `3px solid ${a.bar}`, borderRadius: '7px', padding: '11px 13px' }}>
            <span style={{ fontSize: '9px', fontWeight: 800, letterSpacing: '0.08em', textTransform: 'uppercase', color: a.fg }}>{a.label}</span>
            <p style={{ fontSize: '12px', fontWeight: 700, color: colors.textStrong, marginTop: '3px' }}>{d.title}</p>
            <p style={{ fontSize: '11px', color: colors.textMuted, marginTop: '3px', lineHeight: 1.5 }}>{d.body}</p>
          </div>
        );
      })}
    </div>
  </div>
);
