import { useEffect, useState, type FC } from 'react';
import { liveQuery } from 'dexie';
import { WifiOff, AlertTriangle, RefreshCw } from 'lucide-react';
import { db } from '../../lib/db';
import { retryFailedLogs } from '../../lib/sync';
import { currentOwnerKey } from '../../lib/queueOwner';
import { colors } from '../../styles/theme';

// Sidebar footer indicator: shown only when offline, when logs are queued, or
// when logs have failed to sync. Failed logs are surfaced here (with a Retry
// action) so they are never silently stranded in IndexedDB.
export const SyncStatus: FC<{ isOnline: boolean; pendingCount: number }> = ({ isOnline, pendingCount }) => {
  const [failedCount, setFailedCount] = useState(0);
  const [retrying, setRetrying] = useState(false);

  useEffect(() => {
    // Scoped to the signed-in account, like every other queue read — another
    // farm's stranded rows are not this farm's problem to see or to retry.
    const sub = liveQuery(() => {
      const owner = currentOwnerKey();
      if (!owner) return Promise.resolve(0);
      return db.pendingLogs.where('[ownerKey+status]').equals([owner, 'failed']).count();
    }).subscribe({ next: setFailedCount, error: () => {} });
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
          <WifiOff size={11} color={colors.warnAccent} />
          {/* Reads are served from the service-worker cache while offline
              (ticket 06), so tell the farmer the figures are saved, not live. */}
          <span style={{ color: colors.warnAccent, fontSize: '10px', fontWeight: '600' }}>Offline · showing saved data</span>
        </div>
      )}
      {pendingCount > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '5px 8px', backgroundColor: 'rgba(160,92,0,0.1)', borderRadius: '6px' }}>
          <span style={{ color: colors.warnAccent, fontSize: '10px' }}>⏳ {pendingCount} pending sync</span>
        </div>
      )}
      {failedCount > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '6px', padding: '5px 8px', backgroundColor: 'rgba(193,52,52,0.12)', borderRadius: '6px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertTriangle size={11} color={colors.dangerStrong} />
            <span style={{ color: colors.dangerStrong, fontSize: '10px', fontWeight: '600' }}>{failedCount} failed to sync</span>
          </div>
          <button
            onClick={onRetry}
            disabled={retrying || !isOnline}
            title={isOnline ? 'Retry failed logs' : 'Reconnect to retry'}
            style={{
              display: 'flex', alignItems: 'center', gap: '4px', border: 'none', cursor: retrying || !isOnline ? 'default' : 'pointer',
              background: 'transparent', color: colors.dangerStrong, fontSize: '10px', fontWeight: '700', padding: 0, opacity: retrying || !isOnline ? 0.5 : 1,
            }}
          >
            <RefreshCw size={10} /> Retry
          </button>
        </div>
      )}
    </div>
  );
};
