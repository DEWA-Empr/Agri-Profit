import type { CSSProperties, ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { ClipboardList, BrainCircuit, Sprout, ArrowRight } from 'lucide-react';
import { colors, cardShadow } from '../../../styles/theme';

// First-run experience for the dashboard. The KPI tiles and field/cost cards
// only mean something once there's activity in the ledger, so before any record
// exists we show this instead — a welcome plus the two concrete next steps that
// get a new farm from zero to a populated dashboard.
interface Step {
  to: string;
  icon: ReactNode;
  title: string;
  body: string;
  cta: string;
}

const STEPS: Step[] = [
  {
    to: '/records',
    icon: <ClipboardList size={18} color={colors.primary} />,
    title: 'Log your first activity',
    body: 'Record a planting, input purchase or sale. Each entry updates your profit, costs and reports automatically.',
    cta: 'Add a record',
  },
  {
    to: '/dss',
    icon: <BrainCircuit size={18} color={colors.primary} />,
    title: 'Forecast a yield',
    body: 'Try the decision-support model: pick a crop and field conditions to predict yield before you commit inputs.',
    cta: 'Open DSS Predict',
  },
];

export const DashboardOnboarding = () => {
  const card: CSSProperties = { background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, boxShadow: cardShadow };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      {/* Welcome hero */}
      <div style={{ ...card, padding: '28px', display: 'flex', alignItems: 'center', gap: '20px', background: colors.primarySurface, border: `0.5px solid ${colors.primaryBorderTint}` }}>
        <div style={{ background: colors.surface, borderRadius: '50%', padding: '16px', display: 'flex' }}>
          <Sprout size={30} color={colors.primary} />
        </div>
        <div>
          <h2 style={{ fontSize: '18px', fontWeight: 800, color: colors.primaryDarker }}>Welcome to AgriProfit</h2>
          <p style={{ fontSize: '13px', color: colors.textBody, marginTop: '4px', maxWidth: '560px', lineHeight: 1.5 }}>
            Your dashboard is empty for now. As you log farm activity, this page fills with your real profit, costs and field
            performance. Here's how to get started.
          </p>
        </div>
      </div>

      {/* Next steps */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '18px' }}>
        {STEPS.map((s, i) => (
          <Link key={s.to} to={s.to} style={{ textDecoration: 'none', color: 'inherit' }}>
            <div style={{ ...card, padding: '22px', display: 'flex', flexDirection: 'column', gap: '10px', height: '100%' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ background: colors.primarySurface, borderRadius: '10px', padding: '10px', display: 'flex' }}>{s.icon}</div>
                <span style={{ fontSize: '10px', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: colors.textMuted }}>Step {i + 1}</span>
              </div>
              <h3 style={{ fontSize: '14px', fontWeight: 700, color: colors.text }}>{s.title}</h3>
              <p style={{ fontSize: '12px', color: colors.textMuted, lineHeight: 1.5, flex: 1 }}>{s.body}</p>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 700, color: colors.primary, marginTop: '2px' }}>
                {s.cta} <ArrowRight size={14} />
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};
