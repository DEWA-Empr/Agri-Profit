import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { AuthProvider } from './AuthProvider'
import { useAuth } from './useAuth'
import { purgeApiReadCache } from '../../lib/apiCache'

// Ticket 09: the offline-read cache is farm-scoped, so it MUST be purged on every
// auth change or a previous account's cached reads could be served to the next
// one on a shared device. These tests pin that AuthProvider actually calls the
// purge on both login and logout (the two auth transitions).

// Replace the real cache helper with a spy so we assert the call, not the
// browser Cache Storage behaviour (covered by apiCache.test.ts).
vi.mock('../../lib/apiCache', () => ({
  purgeApiReadCache: vi.fn().mockResolvedValue(undefined),
}))

// Stub the network layer: login resolves with a token; setUnauthorizedHandler is
// called by the provider on mount. Nothing here touches a real server.
vi.mock('../../lib/apiClient', () => ({
  authService: {
    login: vi.fn().mockResolvedValue({
      data: { access_token: 'test-token', token_type: 'bearer' },
    }),
    register: vi.fn(),
  },
  setUnauthorizedHandler: vi.fn(),
}))

// A minimal consumer that exposes the two auth transitions as buttons.
function Harness() {
  const { login, logout } = useAuth()
  return (
    <>
      <button onClick={() => login('farmer@test.example', 'secret-password')}>login</button>
      <button onClick={() => logout()}>logout</button>
    </>
  )
}

describe('AuthProvider purges the offline-read cache on auth changes', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('purges on login', async () => {
    render(
      <AuthProvider>
        <Harness />
      </AuthProvider>,
    )

    fireEvent.click(screen.getByText('login'))

    await waitFor(() => expect(purgeApiReadCache).toHaveBeenCalled())
  })

  it('purges on logout', () => {
    render(
      <AuthProvider>
        <Harness />
      </AuthProvider>,
    )

    fireEvent.click(screen.getByText('logout'))

    expect(purgeApiReadCache).toHaveBeenCalled()
  })
})
