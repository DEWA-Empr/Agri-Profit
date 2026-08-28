import { createContext, useContext } from 'react';
import type { CurrentUser } from '../../lib/apiClient';

// WHO the signed-in user is and WHAT their role admits — as distinct from
// useAuth, which only knows whether a token exists.
//
// WHY THIS IS A CONTEXT AND NOT A HOOK EACH CONSUMER CALLS. GET /auth/me was
// previously fetched inside Sidebar alone, so the answer existed in exactly one
// component and the route table could not see it. Two consumers now need it —
// the nav, to hide links, and the router, to decide where a role may go — and a
// second independent fetch would mean two requests and two moments at which the
// app holds different opinions about the same user.
//
// The permission list is the SERVER's, computed from its own role table
// (core/roles.py) and handed over by /auth/me. Nothing here decides access:
// every operation behind these permissions is independently refused server-side.
// This exists so the interface does not offer a door that is going to be shut.

export type IdentityState =
  /** The identity call has not answered yet. Consumers must not decide anything
   *  irreversible — routing included — while this is the state. */
  | { status: 'loading' }
  | { status: 'ready'; user: CurrentUser }
  /** The call failed. Treated as "no permissions", never as "all permissions". */
  | { status: 'error' };

export const IdentityContext = createContext<IdentityState | null>(null);

export const useIdentity = (): IdentityState => {
  const ctx = useContext(IdentityContext);
  if (!ctx) {
    throw new Error('useIdentity must be used within an IdentityProvider');
  }
  return ctx;
};

/**
 * The caller's permissions, or `null` while the answer is unknown.
 *
 * `null` is not the same as `[]` and the difference matters: `visibleSections`
 * and the route guard both treat null as "don't decide yet", which is what
 * stops the nav flashing links and the router bouncing a manager to /records
 * for the one frame before their role arrives. An ERROR collapses to `[]` —
 * a known-empty set — because at that point there is a decision to make and
 * failing closed is the safe half.
 */
export function permissionsOf(state: IdentityState): string[] | null {
  if (state.status === 'ready') return state.user.permissions ?? [];
  if (state.status === 'error') return [];
  return null;
}
