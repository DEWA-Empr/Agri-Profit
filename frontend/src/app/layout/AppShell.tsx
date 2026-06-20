import type { FC } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { AppRoutes } from '../router';
import { colors } from '../../styles/theme';

// The single application frame: sidebar + header + routed main content.
export const AppShell: FC<{ isOnline: boolean; pendingCount: number }> = ({ isOnline, pendingCount }) => (
  <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden', backgroundColor: colors.appBg }}>
    <Sidebar isOnline={isOnline} pendingCount={pendingCount} />

    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <Header />
      <main style={{ flex: 1, padding: '22px', overflowY: 'auto' }} className="scroll-container">
        <AppRoutes isOnline={isOnline} pendingCount={pendingCount} />
      </main>
    </div>
  </div>
);
