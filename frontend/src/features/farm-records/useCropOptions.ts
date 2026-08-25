import { useEffect, useState } from 'react';
import { dssService } from '../../lib/apiClient';
import { buildCropOptions } from './cropOptions';

// Fetches the two crop sources and merges them (see cropOptions.ts for why
// there are two and why there is no crop table to read instead).
//
// Both requests are allowed to fail independently: allSettled, not all. The
// decision-support read is served from the offline cache when there is no
// connection, the model read is not cached at all, and a farmer offline in a
// field must still be able to pick a crop — so a failure narrows the list
// rather than emptying it, and the form's free-text option covers the rest.
export function useCropOptions(): { crops: string[]; loading: boolean } {
  const [crops, setCrops] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    Promise.allSettled([dssService.getDecisionSupport(), dssService.getModel()])
      .then(([ds, model]) => {
        if (!active) return;
        const recorded = ds.status === 'fulfilled' ? ds.value.data.crops.map((c) => c.crop) : [];
        const predictor = model.status === 'fulfilled' ? (model.value.data.crops ?? []) : [];
        setCrops(buildCropOptions(recorded, predictor));
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  return { crops, loading };
}
