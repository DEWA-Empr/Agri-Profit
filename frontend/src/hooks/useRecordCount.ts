import { useCallback, useEffect, useState } from 'react';
import { ledgerService } from '../lib/apiClient';

// The number of operational logs on record, surfaced as the Farm Records nav
// badge. `count` is null until the first fetch resolves (so the badge stays
// hidden rather than flashing a stale or zero value), and `refresh` lets a
// caller re-pull after logging a new record so the badge stays truthful.
export function useRecordCount(): { count: number | null; refresh: () => void } {
  const [count, setCount] = useState<number | null>(null);

  const refresh = useCallback(() => {
    ledgerService.getLogs()
      .then((res) => setCount(res.data.length))
      .catch(() => { /* keep the last known count on a failed fetch */ });
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  return { count, refresh };
}
