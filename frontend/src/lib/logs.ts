import { db } from './db';
import { ledgerService } from './apiClient';
import type { OperationalLogCreate } from '../types/domain';

export type LogSaveResult = 'saved' | 'offline' | 'queued';

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
    return 'offline';
  }
  try {
    await ledgerService.createLog(full);
    return 'saved';
  } catch {
    await queue();
    return 'queued';
  }
}
