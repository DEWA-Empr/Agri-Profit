// Which crops the entry form offers.
//
// THE BUG THIS REPLACES. The form carried a literal list —
// `['maize','rice','sorghum','soybean','cassava']` — copied from the yield
// model's training crops. That list answers "what can the Tier-2 predictor
// forecast", which is a different question from "what does this farm grow", and
// the two had drifted: cowpea and tomato were seeded with full ledgers, appear
// in /dss/decision-support, and could not be selected in the form that creates
// their records (docs/STATE_REPORT_2026-08-25.md Sections 7.4 and 10.3).
//
// THERE IS NO CROP TABLE. `OperationalLog.crop` is a nullable free-text column
// (models.py) — the backend has no crop entity, enum or registry endpoint to
// read. So the options are assembled from the two API sources that do exist:
//
//   1. the farm's OWN recorded crops, from GET /dss/decision-support — the
//      authoritative answer to what this farm actually grows;
//   2. the predictor's crops, from GET /dss/model — kept because selecting one
//      of these is what makes a yield forecast available for the record.
//
// Union, not either alone: (1) is empty for a farm on its first day, and (2)
// can never grow to include a crop the farmer took up this season.
//
// NORMALISED to trimmed lower case before deduping. The units field learned this
// the hard way — free text turned "kg", "Kg" and "kilos" into three units for
// one thing, and the live database still shows rice yields split across `kg`,
// `bags` and a distinct ` Kg` with a leading space. Crop grouping in the DSS is
// an exact string match on this column, so "Maize" and "maize" would be two
// crops on every panel.

export const normaliseCrop = (crop: string): string => crop.trim().toLowerCase();

/**
 * Merge the farm's recorded crops with the predictor's, normalised, deduped and
 * sorted. Either input may be missing — a failed fetch degrades to the other
 * rather than emptying the selector.
 */
export function buildCropOptions(
  recorded: readonly (string | null | undefined)[] = [],
  predictor: readonly (string | null | undefined)[] = [],
): string[] {
  const seen = new Set<string>();
  for (const raw of [...recorded, ...predictor]) {
    if (raw == null) continue;            // the "Unspecified" bucket is not a crop
    const crop = normaliseCrop(raw);
    if (crop === '') continue;
    seen.add(crop);
  }
  return [...seen].sort((a, b) => a.localeCompare(b));
}
