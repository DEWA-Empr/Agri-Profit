import { BrowserRouter as Router } from 'react-router-dom';
import { useOnlineStatus } from './hooks/useOnlineStatus';
import { usePendingSync } from './hooks/usePendingSync';
import { useRecordCount } from './hooks/useRecordCount';
import { AppShell } from './app/layout/AppShell';
import { AuthProvider } from './features/auth/AuthProvider';
import { useAuth } from './features/auth/useAuth';
import { Login } from './features/auth/Login';

// The authenticated application. Rendered only once a token is present; every
// API request it makes carries the bearer token via the axios interceptor.
const AuthenticatedApp = () => {
  const isOnline = useOnlineStatus();
  const pendingCount = usePendingSync();
  const { count: recordCount, refresh: refreshRecordCount } = useRecordCount();

  return (
    <Router>
      <AppShell
        isOnline={isOnline}
        pendingCount={pendingCount}
        recordCount={recordCount}
        onRecordChange={refreshRecordCount}
      />
    </Router>
  );
};

// The gate: an unauthenticated visitor sees the Login screen; a token (fresh or
// restored from localStorage on reload) swaps in the full app.
const Gate = () => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <AuthenticatedApp /> : <Login />;
};

const App = () => (
  <AuthProvider>
    <Gate />
  </AuthProvider>
);

export default App;
