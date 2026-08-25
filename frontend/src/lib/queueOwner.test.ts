import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { ownerKeyFor, currentOwnerKey } from './queueOwner'
import { setToken, clearToken } from './authToken'

// The owner key partitions the offline write queue by account
// (docs/STATE_REPORT_2026-08-25.md §9.13). Everything downstream — the flush,
// the retry, the counters, the logout purge — treats null as "touch nothing",
// so the cases that must return null matter as much as the one that must not.

// A JWT is three base64url segments; only the middle one is read here, and the
// signature is deliberately never verified (it is a local label, not a claim).
const jwt = (payload: Record<string, unknown>): string => {
  const b64url = (value: string) =>
    btoa(value).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
  return `${b64url('{"alg":"HS256","typ":"JWT"}')}.${b64url(JSON.stringify(payload))}.not-a-real-signature`
}

describe('ownerKeyFor', () => {
  it('reads the sub claim into a namespaced owner key', () => {
    expect(ownerKeyFor(jwt({ sub: '26', exp: 4102444800 }))).toBe('user:26')
  })

  it('accepts a numeric sub as well as a string one', () => {
    // The backend issues `sub` as a string (core/security.create_access_token),
    // but a number must not silently become null and disable the partition.
    expect(ownerKeyFor(jwt({ sub: 26 }))).toBe('user:26')
  })

  it('gives two accounts two different keys', () => {
    expect(ownerKeyFor(jwt({ sub: '1' }))).not.toBe(ownerKeyFor(jwt({ sub: '2' })))
  })

  it('survives base64url payloads that plain base64 would reject', () => {
    // A payload whose base64 contains - and _ must still decode; getting this
    // wrong would return null for real tokens and quietly freeze the queue.
    const key = ownerKeyFor(jwt({ sub: '26', farm: 'a?b>c?d>e' }))
    expect(key).toBe('user:26')
  })

  it.each([
    ['no token', null],
    ['empty string', ''],
    ['not a JWT', 'nonsense'],
    ['a JWT with no payload segment', 'header'],
    ['a payload that is not base64', 'header.!!!!.sig'],
    ['a payload that is not JSON', `header.${btoa('not json')}.sig`],
  ])('returns null for %s', (_label, token) => {
    expect(ownerKeyFor(token as string | null)).toBeNull()
  })

  it.each([
    ['a missing sub', {}],
    ['a null sub', { sub: null }],
    ['an empty sub', { sub: '' }],
  ])('returns null for %s', (_label, payload) => {
    expect(ownerKeyFor(jwt(payload))).toBeNull()
  })
})

describe('currentOwnerKey', () => {
  beforeEach(() => clearToken())
  afterEach(() => clearToken())

  it('is null while signed out, so no queue read matches anything', () => {
    expect(currentOwnerKey()).toBeNull()
  })

  it('follows the persisted token', () => {
    setToken(jwt({ sub: '26' }))
    expect(currentOwnerKey()).toBe('user:26')
  })

  it('changes when a different account signs in on the same browser', () => {
    setToken(jwt({ sub: '26' }))
    const first = currentOwnerKey()
    setToken(jwt({ sub: '31' }))
    expect(currentOwnerKey()).not.toBe(first)
    expect(currentOwnerKey()).toBe('user:31')
  })
})
