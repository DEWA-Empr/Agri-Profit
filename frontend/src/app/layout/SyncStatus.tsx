import { useEffect, useState, type FC } from 'react';
import { liveQuery } from 'dexie';
import { WifiOff, AlertTriangle, RefreshCw } from 'lucide-react';
import { db } from '../../lib/db';
import { retryFailedLogs } from '../../lib/sync';

// Sidebar footer indicator: shown only when offline, when logs are queued, or
// when logs have failed to sync. Failed logs are surfaced here (with a Retry
// action) so they are never silently stranded in IndexedDB.
export const SyncStatus: FC<{ isOnline: boolean; pendingCount: number }> = ({ isOnline, pendingCount }) => {
  const [failedCount, setFailedCount] = useState(0);
  const [retrying, setRetrying] = useState(false);

  useEffect(() => {
    const sub = liveQuery(() =>
      db.pendingLogs.where('status').equals('failed').count()
    ).subscribe({ next: setFailedCount, error: () => {} });
    return () => sub.unsubscribe();
  }, []);

  if (isOnline && pendingCount === 0 && failedCount === 0) return null;

  const onRetry = async () => {
    setRetrying(true);
    try {
      await retryFailedLogs();
    } finally {
      setRetrying(false);
    }
  };

  return (
    <div style={{ padding: '10px 18px', borderTop: '0.5px solid rgba(99,153,34,0.12)', display: 'flex', flexDirection: 'column', gap: '5px' }}>
      {!isOnline && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '5px 8px', backgroundColor: 'rgba(160,92,0,0.15)', borderRadius: '6px' }}>
          <WifiOff size={11} color="#BA7517" />
          <span style={{ color: '#BA7517', fontSize: '10px', fontWeight: '600' }}>Offline</span>
        </div>
      )}
      {pendingCount > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '5px 8px', backgroundColor: 'rgba(160,92,0,0.1)', borderRadius: '6px' }}>
          <span style={{ color: '#BA7517', fontSize: '10px' }}>⏳ {pendingCount} pending sync</span>
        </div>
      )}
      {failedCount > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '6px', padding: '5px 8px', backgroundColor: 'rgba(193,52,52,0.12)', borderRadius: '6px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertTriangle size={11} color="#C13434" />
            <span style={{ color: '#C13434', fontSize: '10px', fontWeight: '600' }}>{failedCount} failed to sync</span>
          </div>
          <button
            onClick={onRetry}
            disabled={retrying || !isOnline}
            title={isOnline ? 'Retry failed logs' : 'Reconnect to retry'}
            style={{
              display: 'flex', alignItems: 'center', gap: '4px', border: 'none', cursor: retrying || !isOnline ? 'default' : 'pointer',
              background: 'transparent', color: '#C13434', fontSize: '10px', fontWeight: '700', padding: 0, opacity: retrying || !isOnline ? 0.5 : 1,
            }}
          >
            <RefreshCw size={10} /> Retry
          </button>
        </div>
      )}
    </div>
  );
};
