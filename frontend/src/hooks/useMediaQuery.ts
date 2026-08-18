import { useCallback, useSyncExternalStore } from 'react';

/**
 * Subscribe to a CSS media query from React.
 *
 * Layout that is purely visual lives in index.css as media queries; this hook
 * exists for the cases where the *behaviour* differs, not just the styling —
 * chiefly the sidebar, which is a permanent rail on desktop and a dismissible
 * drawer on mobile, and therefore needs open/close state that CSS cannot hold.
 *
 * Built on useSyncExternalStore rather than useState + useEffect: matchMedia is
 * exactly the external mutable source that API exists for. It reads the current
 * value during render (no first-paint flash at the wrong breakpoint) and needs
 * no setState inside an effect.
 */
export function useMediaQuery(query: string): boolean {
  const subscribe = useCallback((onChange: () => void) => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
      return () => {};
    }
    const mql = window.matchMedia(query);
    mql.addEventListener('change', onChange);
    return () => mql.removeEventListener('change', onChange);
  }, [query]);

  const getSnapshot = useCallback(
    () =>
      typeof window !== 'undefined' && typeof window.matchMedia === 'function'
        ? window.matchMedia(query).matches
        : false,
    [query],
  );

  // Server snapshot: assume desktop, matching the pre-hydration markup.
  return useSyncExternalStore(subscribe, getSnapshot, () => false);
}

/** The app's single layout breakpoint. Mirrors the media query in index.css. */
export const MOBILE_QUERY = '(max-width: 768px)';
