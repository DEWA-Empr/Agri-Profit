import { useCallback, useEffect, useMemo, useState } from 'react';
import type { FC, ReactNode } from 'react';
import { authService, setUnauthorizedHandler } from '../../lib/apiClient';
import { getToken, setToken as persistToken, clearToken } from '../../lib/authToken';
import { purgeApiReadCache } from '../../lib/apiCache';
import { AuthContext, type AuthContextValue } from './useAuth';

// Auth state for the whole app. The token lives in localStorage (see
// lib/authToken) so a reload restores the session; this provider mirrors it in
// React state and exposes login/register/logout. On a 401 anywhere, the axios
// response interceptor clears the token and calls back here to log out.
export const AuthProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [token, setTokenState] = useState<string | null>(() => getToken());

  const applyToken = useCallback((value: string) => {
    // Drop any offline-read cache left by a previous account before this farm's
    // requests can be served from it (see lib/apiCache).
    void purgeApiReadCache();
    persistToken(value);
    setTokenState(value);
  }, []);

  const logout = useCallback(() => {
    // Clear this farm's cached reads so they can't be served to the next account.
    void purgeApiReadCache();
    clearToken();
    setTokenState(null);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { data } = await authService.login({ email, password });
    applyToken(data.access_token);
  }, [applyToken]);

  const register = useCallback(async (email: string, password: string, farmName?: string) => {
    const { data } = await authService.register({ email, password, farm_name: farmName });
    applyToken(data.access_token);
  }, [applyToken]);

  // Let the axios 401 interceptor drop us back to the login screen.
  useEffect(() => {
    setUnauthorizedHandler(() => setTokenState(null));
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ isAuthenticated: Boolean(token), login, register, logout }),
    [token, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
