import Dexie, { type Table } from 'dexie';
import type { OperationalLogCreate } from '../types/domain';
import { currentOwnerKey } from './queueOwner';

export interface PendingLog {
  id?: number;
  // Which account queued this write (see lib/queueOwner). IndexedDB is shared by
  // every account that signs in on this browser, so without it a row captured
  // offline by one farm could be flushed into the next account to sign in.
  ownerKey: string;
  clientId: string;
  payload: OperationalLogCreate;
  status: 'pending' | 'failed';
  failCount: number;
  createdAt: number;
}

class AgriProfitDB extends Dexie {
  pendingLogs!: Table<PendingLog>;

  constructor() {
    super('agriprofit');
    this.version(1).stores({
      pendingLogs: '++id, clientId, status, createdAt',
    });
    // v2 adds the owner partition. `[ownerKey+status]` is the compound index
    // every read path now uses — the queue is always read as "this account's
    // pending rows", never as "all pending rows".
    this.version(2)
      .stores({
        pendingLogs: '++id, clientId, status, createdAt, ownerKey, [ownerKey+status]',
      })
      .upgrade(async (tx) => {
        const table = tx.table<PendingLog>('pendingLogs');
        const owner = currentOwnerKey();
        if (owner) {
          // Someone is signed in, and a v1 row can only have been queued by the
          // session that is still holding this device's token. Attribute them.
          await table.toCollection().modify({ ownerKey: owner });
          return;
        }
        // No token, so these rows cannot be attributed to anybody. They are
        // exactly the rows the defect would have flushed into whichever account
        // signed in next, and there is no owner to hand them back to, so they
        // are dropped rather than left as a loaded gun. This runs once, on the
        // first load after upgrading while signed out.
        await table.clear();
      });
  }
}

export const db = new AgriProfitDB();
