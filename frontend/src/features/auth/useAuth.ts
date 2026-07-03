import { createContext, useContext } from 'react';

// Auth context shape + hook. Kept separate from the provider component so the
// file exports only non-components (satisfies react-refresh/only-export-components).
export interface AuthContextValue {
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, farmName?: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
};
