import { BrowserRouter as Router } from 'react-router-dom';
import { useOnlineStatus } from './hooks/useOnlineStatus';
import { usePendingSync } from './hooks/usePendingSync';
import { useRecordCount } from './hooks/useRecordCount';
import { AppShell } from './app/layout/AppShell';

const App = () => {
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

export default App;
