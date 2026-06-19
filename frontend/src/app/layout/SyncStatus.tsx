import type { FC } from 'react';
import { WifiOff } from 'lucide-react';

// Sidebar footer indicator: shown only when offline or when logs are queued.
export const SyncStatus: FC<{ isOnline: boolean; pendingCount: number }> = ({ isOnline, pendingCount }) => {
  if (isOnline && pendingCount === 0) return null;

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
    </div>
  );
};
