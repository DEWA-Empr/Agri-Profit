import { useEffect, useState, type FC } from 'react';
import { useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { AppRoutes } from '../router';
import { useMediaQuery, MOBILE_QUERY } from '../../hooks/useMediaQuery';
import { colors } from '../../styles/theme';

// The single application frame: sidebar + header + routed main content.
//
// Responsive behaviour: above 768px the sidebar is a permanent 220px rail.
// Below it, the rail would leave ~140px for content, so it becomes a
// dismissible drawer opened from a hamburger in the header and the main column
// takes the full viewport width. A drawer rather than a bottom bar because the
// sidebar also carries the sync status and the signed-in identity, neither of
// which a bottom bar can host, and because a permanent bar would cost vertical
// space on a 640px-tall screen.
interface AppShellProps {
  isOnline: boolean;
  pendingCount: number;
  recordCount: number | null;
  onRecordChange: () => void;
}

export const AppShell: FC<AppShellProps> = ({ isOnline, pendingCount, recordCount, onRecordChange }) => {
  const location = useLocation();
  const isMobile = useMediaQuery(MOBILE_QUERY);
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Two things deliberately NOT handled with effects:
  //  - closing on navigation: NavItem calls onNavigate on click (below), which
  //    is the only way to navigate from inside the drawer.
  //  - closing when the viewport grows: the drawer is rendered from
  //    `isMobile && drawerOpen`, so crossing the breakpoint hides it without
  //    any state to reconcile.

  // Escape closes, matching the other dismissible surfaces in the app.
  useEffect(() => {
    if (!drawerOpen) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setDrawerOpen(false); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [drawerOpen]);

  const sidebar = (
    <Sidebar
      isOnline={isOnline}
      pendingCount={pendingCount}
      recordCount={recordCount}
      onNavigate={() => setDrawerOpen(false)}
    />
  );

  return (
    <div style={{
      display: 'flex',
      // dvh tracks the real viewport as mobile browsers show/hide their URL
      // bar; the vh line above it is the fallback for older engines.
      height: '100vh',
      maxHeight: '100dvh',
      width: '100%',
      overflow: 'hidden',
      backgroundColor: colors.appBg,
    }}>
      {/* Desktop: permanent rail. Mobile: drawer + scrim, mounted only when open. */}
      {!isMobile && sidebar}

      {isMobile && drawerOpen && (
        <div
          className="modal-backdrop"
          onClick={() => setDrawerOpen(false)}
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.45)', zIndex: 60 }}
        >
          <div
            className="nav-drawer"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-label="Navigation"
            style={{ height: '100%', width: 'min(82vw, 260px)', boxShadow: '18px 0 48px -12px rgba(15,31,9,0.35)' }}
          >
            {sidebar}
          </div>
        </div>
      )}

      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Header isMobile={isMobile} onOpenNav={() => setDrawerOpen(true)} />
        <main
          style={{ flex: 1, padding: isMobile ? '14px' : '22px', overflowY: 'auto', overflowX: 'hidden' }}
          className="scroll-container"
        >
          {/* key by path so the content replays its entrance on each navigation */}
          <div key={location.pathname} className="fade-in-up">
            <AppRoutes isOnline={isOnline} pendingCount={pendingCount} onRecordChange={onRecordChange} />
          </div>
        </main>
      </div>
    </div>
  );
};
