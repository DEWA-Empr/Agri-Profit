import { useState } from 'react';
import type { FC, FormEvent } from 'react';
import axios from 'axios';
import { useAuth } from './useAuth';
import { colors, cardShadow } from '../../styles/theme';

// The unauthenticated gate: sign in to an existing farm, or register a new one.
// On success the AuthContext stores the JWT and the app swaps to the AppShell.
export const Login: FC = () => {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [farmName, setFarmName] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const isRegister = mode === 'register';

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      if (isRegister) {
        await register(email, password, farmName || undefined);
      } else {
        await login(email, password);
      }
    } catch (err) {
      // Surface the server's message (e.g. "Email already registered",
      // "Incorrect email or password") when present, else a generic fallback.
      const detail = axios.isAxiosError(err) ? err.response?.data?.detail : null;
      setError(
        typeof detail === 'string'
          ? detail
          : isRegister
            ? 'Could not create your account. Please try again.'
            : 'Sign in failed. Check your email and password.',
      );
    } finally {
      setBusy(false);
    }
  };

  const switchMode = () => {
    setError('');
    setMode(isRegister ? 'login' : 'register');
  };

  const inputStyle = {
    width: '100%',
    padding: '10px 12px',
    borderRadius: '8px',
    border: `1px solid ${colors.borderInput}`,
    fontSize: '13px',
    boxSizing: 'border-box' as const,
  };

  return (
    <div style={{ minHeight: '100vh', width: '100vw', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: colors.appBg, padding: '20px' }}>
      <div style={{ width: '100%', maxWidth: '380px', background: colors.surface, borderRadius: '14px', border: `0.5px solid ${colors.border}`, boxShadow: cardShadow, padding: '32px' }}>
        <div style={{ marginBottom: '24px' }}>
          <h1 style={{ fontSize: '22px', fontWeight: '600', color: colors.primaryDark, letterSpacing: '-0.4px' }}>AgriProfit</h1>
          <p style={{ fontSize: '12px', color: colors.textMuted, marginTop: '4px' }}>
            {isRegister ? 'Create your farm account' : 'Sign in to your farm'}
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {isRegister && (
            <div>
              <label style={{ display: 'block', fontSize: '11px', fontWeight: '600', color: colors.labelText, marginBottom: '6px' }}>FARM NAME (OPTIONAL)</label>
              <input type="text" value={farmName} onChange={(e) => setFarmName(e.target.value)} placeholder="e.g. Sunrise Farm" style={inputStyle} />
            </div>
          )}
          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: '600', color: colors.labelText, marginBottom: '6px' }}>EMAIL</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="username" style={inputStyle} />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: '600', color: colors.labelText, marginBottom: '6px' }}>PASSWORD</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={isRegister ? 8 : undefined}
              autoComplete={isRegister ? 'new-password' : 'current-password'}
              style={inputStyle}
            />
            {isRegister && (
              <p style={{ fontSize: '10px', color: colors.textFaint, marginTop: '5px' }}>At least 8 characters.</p>
            )}
          </div>

          {error && (
            <div style={{ fontSize: '11px', color: colors.danger, backgroundColor: 'rgba(192,57,43,0.06)', border: `0.5px solid rgba(192,57,43,0.2)`, borderRadius: '8px', padding: '8px 10px' }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={busy}
            style={{ backgroundColor: colors.primaryDark, color: colors.onPrimary, padding: '11px', borderRadius: '8px', border: 'none', fontWeight: '600', fontSize: '13px', cursor: busy ? 'default' : 'pointer', opacity: busy ? 0.7 : 1, marginTop: '4px' }}
          >
            {busy ? 'Please wait…' : isRegister ? 'Create account' : 'Sign in'}
          </button>
        </form>

        <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '12px', color: colors.textMuted }}>
          {isRegister ? 'Already have an account?' : 'New to AgriProfit?'}{' '}
          <button onClick={switchMode} style={{ background: 'none', border: 'none', color: colors.primary, fontWeight: '600', cursor: 'pointer', fontSize: '12px', padding: 0 }}>
            {isRegister ? 'Sign in' : 'Create a farm account'}
          </button>
        </div>
      </div>
    </div>
  );
};
