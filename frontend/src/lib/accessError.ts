// Was this rejection the server refusing the caller's ROLE, rather than a
// network fault or a missing record?
//
// WHY THIS EXISTS. Dashboard panels used to end every fetch in
// `.catch((err) => console.error(err))`, which turned a 403 into an empty chart
// with no explanation: a worker opening a finance panel saw zeros and had no
// way to tell "you may not see this" from "your farm has no data". Zeros are a
// worse answer than a refusal, because zeros look like a fact about the farm.
//
// 403 specifically, never 401. A 401 means the token is gone or expired, and
// the axios response interceptor already handles that by logging the user out
// (see apiClient). Treating 401 as "no permission" here would render a denial
// panel for a moment on the way to the login screen.
export function isForbidden(err: unknown): boolean {
  return (err as { response?: { status?: number } })?.response?.status === 403;
}
