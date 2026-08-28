import { useEffect, useState } from 'react';
import { liveQuery } from 'dexie';
import { db } from '../lib/db';
import { currentOwnerKey } from '../lib/queueOwner';

// Reactive count of operational logs queued offline and awaiting sync, for the
// signed-in account only. The owner key is read inside the query rather than
// captured outside it, so the count follows the current session instead of the
// one that happened to mount this hook.
export function usePendingSync(): number {
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    const sub = liveQuery(() => {
      const owner = currentOwnerKey();
      if (!owner) return Promise.resolve(0);
      return db.pendingLogs.where('[ownerKey+status]').equals([owner, 'pending']).count();
    }).subscribe({ next: setPendingCount, error: () => {} });
    return () => sub.unsubscribe();
  }, []);

  return pendingCount;
}
