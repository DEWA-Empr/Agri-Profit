import { db } from './db';
import { ledgerService } from './apiClient';
import type { OperationalLog, OperationalLogCreate } from '../types/domain';

// A discriminated union rather than a bare string: a record that reached the
// server carries the created log back, which is what a caller needs to read
// server-computed follow-ups (e.g. a drying run's metrics from /bioprocess/{id}).
// A queued record has no id yet, and the type makes that impossible to forget.
export type LogSaveResult =
  | { status: 'saved'; log: OperationalLog }
  | { status: 'offline' }
  | { status: 'queued' };

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

  const queue = () =>
    db.pendingLogs.add({ clientId, payload: full, status: 'pending', failCount: 0, createdAt: Date.now() });

  if (!isOnline) {
    await queue();
    return { status: 'offline' };
  }
  try {
    const res = await ledgerService.createLog(full);
    return { status: 'saved', log: res.data };
  } catch {
    await queue();
    return { status: 'queued' };
  }
}
