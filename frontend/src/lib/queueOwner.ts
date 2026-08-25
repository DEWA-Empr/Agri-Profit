import { getToken } from './authToken';

// Who a queued offline write belongs to.
//
// The offline write queue lives in IndexedDB, which is shared by every account
// that signs in on this browser. Before this module existed, a row carried no
// identity at all: `flushPendingLogs` read every pending row and POSTed it under
// whatever token happened to be current, so a record captured offline by one
// farm could be flushed into the next account to sign in. The owner key is the
// partition that closes that.
//
// NOT AUTHORISATION. The key is read from the token's `sub` claim WITHOUT
// verifying the signature, because it is only a local partition label — the
// server still authenticates every POST the queue makes, and a forged key can
// at worst hide a device's own rows from itself. Verifying a signature here
// would need the server secret in the browser, which is strictly worse.
//
// The `user:` prefix keeps the namespace explicit, so a future partition on
// something other than a user id (a farm, a device) is additive rather than
// ambiguous against a bare numeric id.
const OWNER_PREFIX = 'user:';

/** Decode a JWT's `sub` into an owner key, or null if there isn't one. */
export function ownerKeyFor(token: string | null | undefined): string | null {
  if (!token) return null;
  const payload = token.split('.')[1];
  if (!payload) return null;
  try {
    // base64url -> base64 before atob; JWT payloads are base64url-encoded.
    const json = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    const sub = (JSON.parse(json) as { sub?: unknown }).sub;
    if (sub === undefined || sub === null || sub === '') return null;
    return `${OWNER_PREFIX}${String(sub)}`;
  } catch {
    // A malformed or non-JWT token has no identity we can trust. Null means
    // "unattributable", and every caller treats that as "do not touch the
    // queue" rather than as "touch all of it".
    return null;
  }
}

/** The owner key for the token currently persisted, or null when signed out. */
export function currentOwnerKey(): string | null {
  return ownerKeyFor(getToken());
}
