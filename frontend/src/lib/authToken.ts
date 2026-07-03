// Single source of truth for the persisted auth token. localStorage keeps the
// session alive across reloads; the axios interceptors (apiClient.ts) read from
// here on every request, and the AuthContext writes on login/logout.
const TOKEN_KEY = 'agriprofit_token';

export const getToken = (): string | null => localStorage.getItem(TOKEN_KEY);

export const setToken = (token: string): void => localStorage.setItem(TOKEN_KEY, token);

export const clearToken = (): void => localStorage.removeItem(TOKEN_KEY);
