import { BrowserRouter as Router, useMatch } from 'react-router-dom';
import { useOnlineStatus } from './hooks/useOnlineStatus';
import { usePendingSync } from './hooks/usePendingSync';
import { useRecordCount } from './hooks/useRecordCount';
import { AppShell } from './app/layout/AppShell';
import { AuthProvider } from './features/auth/AuthProvider';
import { useAuth } from './features/auth/useAuth';
import { Login } from './features/auth/Login';
import PublicInvestorReport from './features/investors/PublicInvestorReport';

// The authenticated application. Rendered only once a token is present; every
// API request it makes carries the bearer token via the axios interceptor.
const AuthenticatedApp = () => {
  const isOnline = useOnlineStatus();
  const pendingCount = usePendingSync();
  const { count: recordCount, refresh: refreshRecordCount } = useRecordCount();

  return (
    <AppShell
      isOnline={isOnline}
      pendingCount={pendingCount}
      recordCount={recordCount}
      onRecordChange={refreshRecordCount}
    />
  );
};

// The gate: an unauthenticated visitor sees the Login screen; a token (fresh or
// restored from localStorage on reload) swaps in the full app.
const Gate = () => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <AuthenticatedApp /> : <Login />;
};

// The public investor report (/investor/:token) is reachable without a login and
// bypasses the gate entirely. We check for it with useMatch before the gate so
// the existing AppShell/AppRoutes tree is left untouched (no nested <Routes>).
const Root = () => {
  const shareMatch = useMatch('/investor/:token');
  if (shareMatch?.params.token) {
    return <PublicInvestorReport token={shareMatch.params.token} />;
  }
  return <Gate />;
};

const App = () => (
  <AuthProvider>
    <Router>
      <Root />
    </Router>
  </AuthProvider>
);

export default App;
