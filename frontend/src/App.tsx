import { BrowserRouter as Router } from 'react-router-dom';
import { useOnlineStatus } from './hooks/useOnlineStatus';
import { usePendingSync } from './hooks/usePendingSync';
import { AppShell } from './app/layout/AppShell';

const App = () => {
  const isOnline = useOnlineStatus();
  const pendingCount = usePendingSync();

  return (
    <Router>
      <AppShell isOnline={isOnline} pendingCount={pendingCount} />
    </Router>
  );
};

export default App;
