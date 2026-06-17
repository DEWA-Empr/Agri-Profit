import Dexie, { type Table } from 'dexie';

export interface PendingLog {
  id?: number;
  clientId: string;
  payload: Record<string, unknown>;
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
