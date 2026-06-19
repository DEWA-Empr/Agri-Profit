import { useEffect, useState } from 'react';
import { liveQuery } from 'dexie';
import { db } from '../lib/db';

// Reactive count of operational logs queued offline and awaiting sync.
export function usePendingSync(): number {
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    const sub = liveQuery(() =>
      db.pendingLogs.where('status').equals('pending').count()
    ).subscribe({ next: setPendingCount, error: () => {} });
    return () => sub.unsubscribe();
  }, []);

  return pendingCount;
}
