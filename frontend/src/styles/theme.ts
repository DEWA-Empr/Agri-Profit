// Shared design tokens — the single source of truth for colours, spacing and
// radii used across the app's inline styles. Tailwind is deliberately not used
// (it is not part of the build); instead, repeated values live here so a brand
// tweak is a one-line change rather than a find-and-replace across every file
// (see STRUCTURE.md §3).
//
// Adopt these in components via `import { colors } from '../styles/theme'` and
// reference `colors.primary` instead of hardcoding a hex string.

export const colors = {
  // --- Brand greens ---
  primary: '#639922',
  primaryDark: '#3B6D11',
  primaryDarker: '#27500A',
  primaryDarkest: '#1e3d0a',
  primaryLight: '#97C459',
  primaryTint: '#c0dd97', // chart "expenses" bar / light accent
  primarySurface: '#f0f7e8', // green-tinted surface (icon chips, banners)
  primaryBorderTint: '#c8dfa8', // green-tinted border on highlighted cards
  onPrimary: '#EAF3DE', // text/icons sitting on a dark-green fill
  sidebarBg: '#0f1f09',
  sidebarHeading: '#2d5010', // section heading text in the nav rail
  sidebarText: '#4a7a1a', // inactive nav-item text

  // --- App surfaces ---
  appBg: '#f7f9f4',
  surface: '#ffffff',
  surfaceMuted: '#fafbf8',

  // --- Borders & dividers ---
  border: '#e8ede4',
  borderInput: '#d0d8c8',
  divider: '#f0f0f0',
  dividerLight: '#f5f5f5',

  // --- Text ---
  textStrong: '#111111',
  text: '#222222',
  textBody: '#333333',
  textMuted: '#888888',
  textFaint: '#aaaaaa',
  labelText: '#555555', // form field labels

  // --- Status ---
  danger: '#c0392b', // expense red (amounts)
  dangerAlt: '#b33333',
  dangerStrong: '#C13434', // failed-sync alert
  warn: '#a05c00', // offline / pending amber (text)
  warnAccent: '#BA7517',
  info: '#185FA5',
  infoAlt: '#378ADD',
} as const;

// Semantic accent set for Decision Support cards (and similar callouts). Each
// has a foreground (text/icon), a soft background tint, and a left-border bar.
export const accents = {
  alert: { fg: '#C0392B', bg: 'rgba(192,57,43,0.06)', bar: '#C0392B', label: 'Alert' },
  opportunity: { fg: '#A05C00', bg: 'rgba(160,92,0,0.07)', bar: '#D4A843', label: 'Opportunity' },
  insight: { fg: '#3B6D11', bg: 'rgba(99,153,34,0.08)', bar: '#639922', label: 'Insight' },
  window: { fg: '#185FA5', bg: 'rgba(24,95,165,0.06)', bar: '#378ADD', label: 'Window' },
} as const;

export type AccentKey = keyof typeof accents;

// Ordered palette for the cost-breakdown segmented bar (greens → earth tones),
// applied to operating-cost categories in order of size.
export const categoryColors = [
  '#3B6D11', '#639922', '#97C459', '#C0DD97', '#D4A843', '#BA7517', '#A05C00',
] as const;

// Crop pill tints for the field-performance table.
export const cropTints: Record<string, { bg: string; fg: string }> = {
  maize: { bg: '#eaf3da', fg: '#3B6D11' },
  soybean: { bg: '#e3eed9', fg: '#5a7a2a' },
  wheat: { bg: '#f6ecd6', fg: '#9a6a16' },
  default: { bg: '#eef1ea', fg: '#5a6650' },
};

// Soft elevation used by content cards in the #04 look.
export const cardShadow = '0 1px 2px rgba(15,31,9,0.04), 0 1px 3px rgba(15,31,9,0.03)';

export const radius = {
  sm: '6px',
  md: '8px',
  lg: '12px',
  pill: '50%',
} as const;

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '12px',
  lg: '18px',
  xl: '22px',
} as const;

export const theme = { colors, radius, spacing } as const;
