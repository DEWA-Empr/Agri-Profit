import { db } from './db';
import { ledgerService } from './apiClient';
import { currentOwnerKey } from './queueOwner';
import type { OperationalLog, OperationalLogCreate } from '../types/domain';

// A discriminated union rather than a bare string: a record that reached the
// server carries the created log back, which is what a caller needs to read
// server-computed follow-ups (e.g. a drying run's metrics from /bioprocess/{id}).
// A queued record has no id yet, and the type makes that impossible to forget.
//
// 'unauthenticated' exists because a queued row must name its owner (see
// lib/queueOwner). With no signed-in account there is nobody to attribute the
// row to, and queueing it unattributed is precisely the leak the owner key
// closes — so the save is refused and said so, rather than silently becoming a
// record that would flush into whichever account signs in next.
export type LogSaveResult =
  | { status: 'saved'; log: OperationalLog }
  | { status: 'offline' }
  | { status: 'queued' }
  | { status: 'unauthenticated' };

// Offline-first save of an operational log (with its paired financial
// transaction). The caller passes the payload WITHOUT a client_id — a fresh
// idempotency key is generated here so the queued copy and any later server
// retry are deduped server-side.
//
// - 'saved'   : persisted to the server now
// - 'offline' : no connection, queued in IndexedDB for later sync
// - 'queued'  : online but the request failed, queued to retry
export async function saveOperationalLog(
  payload: Omit<OperationalLogCreate, 'client_id'>,
  isOnline: boolean,
): Promise<LogSaveResult> {
  const clientId = crypto.randomUUID();
  const full: OperationalLogCreate = { ...payload, client_id: clientId };

  // Read once, before the request: the owner stamped on the row is the account
  // that captured the record, not whoever happens to be signed in when it later
  // flushes.
  const ownerKey = currentOwnerKey();

  const queue = () =>
    db.pendingLogs.add({
      ownerKey: ownerKey!,
      clientId,
      payload: full,
      status: 'pending',
      failCount: 0,
      createdAt: Date.now(),
    });

  if (!isOnline) {
    if (!ownerKey) return { status: 'unauthenticated' };
    await queue();
    return { status: 'offline' };
  }
  try {
    const res = await ledgerService.createLog(full);
    return { status: 'saved', log: res.data };
  } catch {
    if (!ownerKey) return { status: 'unauthenticated' };
    await queue();
    return { status: 'queued' };
  }
}
