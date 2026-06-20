import Dexie, { type Table } from 'dexie';
import type { OperationalLogCreate } from '../types/domain';

export interface PendingLog {
  id?: number;
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
  }
}

export const db = new AgriProfitDB();
