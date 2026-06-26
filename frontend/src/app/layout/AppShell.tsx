import type { FC } from 'react';
import { useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { AppRoutes } from '../router';
import { colors } from '../../styles/theme';

// The single application frame: sidebar + header + routed main content.
interface AppShellProps {
  isOnline: boolean;
  pendingCount: number;
  recordCount: number | null;
  onRecordChange: () => void;
}

export const AppShell: FC<AppShellProps> = ({ isOnline, pendingCount, recordCount, onRecordChange }) => {
  const location = useLocation();
  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden', backgroundColor: colors.appBg }}>
      <Sidebar isOnline={isOnline} pendingCount={pendingCount} recordCount={recordCount} />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Header />
        <main style={{ flex: 1, padding: '22px', overflowY: 'auto' }} className="scroll-container">
          {/* key by path so the content replays its entrance on each navigation */}
          <div key={location.pathname} className="fade-in-up">
            <AppRoutes isOnline={isOnline} pendingCount={pendingCount} onRecordChange={onRecordChange} />
          </div>
        </main>
      </div>
    </div>
  );
};
