// Money and percentage formatting for the enterprise-economics panels.
//
// Two naira formatters, deliberately. `naira` abbreviates a TOTAL (₦267.7K) —
// nobody reads a cost pool to the kobo. `nairaPerKg` does not abbreviate, ever,
// because a per-kilogram rate rounded to the naira collapses exactly the gap
// the two break-even prices exist to show: ₦41.67 and ₦42.37 both become "₦42",
// and the whole point of reporting two numbers disappears.

export const naira = (n: number): string => {
  const abs = Math.abs(n);
  const body =
    abs >= 1_000_000 ? `${(abs / 1_000_000).toFixed(2)}M`
    : abs >= 1_000 ? `${(abs / 1_000).toFixed(1)}K`
    : abs.toLocaleString(undefined, { maximumFractionDigits: 0 });
  // A minus sign (U+2212), not a hyphen: it aligns with digits.
  return `${n < 0 ? '−' : ''}₦${body}`;
};

export const nairaPerKg = (n: number): string =>
  `${n < 0 ? '−' : ''}₦${Math.abs(n).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;

// Exact naira, no abbreviation — for the partial budget, where the user typed
// the inputs and expects to see them back unrounded.
export const nairaExact = (n: number): string =>
  `${n < 0 ? '−' : ''}₦${Math.abs(n).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;

// One decimal place. A coverage of 92.1553978333956% is not more honest for
// being longer, but it must not round to a flat 92 either — 99.96 and 100 are
// different claims and the reader has to be able to tell them apart.
export const pct = (n: number): string => `${n.toFixed(1)}%`;

// The em dash stands for "undefined", and it is used everywhere the backend
// returned null. It is never a zero: a break-even price over no marketable mass
// is not ₦0.00, it is a question with no answer.
export const DASH = '—';
