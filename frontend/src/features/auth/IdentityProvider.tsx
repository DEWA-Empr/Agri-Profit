import { useEffect, useMemo, useState, type FC, type ReactNode } from 'react';
import { authService } from '../../lib/apiClient';
import { IdentityContext, type IdentityState } from './useIdentity';

// Fetches GET /auth/me once for the authenticated session and shares it.
//
// MOUNTED INSIDE THE AUTHENTICATED TREE (see App.tsx), so it runs only when a
// token exists and it remounts when the account changes — logging out unmounts
// the whole authenticated app, which is what guarantees the next user does not
// inherit the previous user's permissions from this state.
export const IdentityProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [state, setState] = useState<IdentityState>({ status: 'loading' });

  useEffect(() => {
    let cancelled = false;
    authService.me()
      .then((res) => { if (!cancelled) setState({ status: 'ready', user: res.data }); })
      // No retry and no error surface. A failure here degrades to the
      // unrestricted subset of the app (Farm Records), which is the same place
      // a worker legitimately lives — so the fallback is a usable app, not an
      // error screen. A 401 is handled by the axios interceptor instead, which
      // logs the session out from under this.
      .catch(() => { if (!cancelled) setState({ status: 'error' }); });
    return () => { cancelled = true; };
  }, []);

  const value = useMemo(() => state, [state]);
  return <IdentityContext.Provider value={value}>{children}</IdentityContext.Provider>;
};
