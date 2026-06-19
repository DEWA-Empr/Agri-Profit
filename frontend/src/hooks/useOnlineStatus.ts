import { useEffect, useState } from 'react';
import { flushPendingLogs, registerSyncListener } from '../lib/sync';

// Tracks browser online/offline status and flushes the offline queue whenever
// connectivity is regained. Returns the current online state.
export function useOnlineStatus(): boolean {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const onOnline = () => { setIsOnline(true); flushPendingLogs(); };
    const onOffline = () => setIsOnline(false);
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
    const cleanupSync = registerSyncListener();
    return () => {
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
      cleanupSync();
    };
  }, []);

  return isOnline;
}
