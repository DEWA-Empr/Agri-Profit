// Client-side mirror of the server's money and quantity bounds.
//
// WHY THIS EXISTS AT ALL, given the server already enforces them. Because of
// the offline queue. A record entered with no connection is held in IndexedDB
// and POSTed later; if the server will answer 422, it will answer 422 on every
// retry, and the row transitions to `failed` after three attempts and sits
// there. The farmer's entry is lost at the moment they can least afford it —
// in a field, with no feedback. `DryingFields` already validates before
// queueing for exactly this reason (see FarmRecordCreateForm.handleSubmit);
// money and quantity had no such guard.
//
// THIS IS NOT THE ENFORCEMENT POINT. The server rejects these values
// independently (backend/app/schemas/schemas.py: Money, Quantity), and a
// request that bypasses this file entirely is still refused. What this buys is
// that a farmer finds out immediately, while the record is still on screen and
// still editable.
//
// The constants are duplicated from the backend rather than fetched, and that
// is a deliberate trade: an offline client cannot ask the server what its
// bounds are, and a bound that only applies when online is not a bound. They
// are asserted against the documented server values in recordBounds.test.ts, so
// a drift shows up as a failing test rather than as a stuck queue.

/** ₦1bn — matches backend schemas.MAX_NAIRA. */
export const MAX_NAIRA = 1_000_000_000;
/** 1,000 t in one record — matches backend schemas.MAX_QUANTITY. */
export const MAX_QUANTITY = 1_000_000;

const naira = (value: number) =>
  `₦${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

/**
 * Check one money field as the user typed it.
 * Returns an error message, or null when the value is acceptable.
 */
export function validateAmount(raw: string): string | null {
  const trimmed = raw.trim();
  if (trimmed === '') return 'Enter an amount.';

  const value = Number(trimmed);
  // Number('') is 0 and Number('12abc') is NaN — the trim check above handles
  // the first, this handles the second, and both must be caught here because
  // JSON.stringify turns NaN into null and the server would answer 422.
  if (!Number.isFinite(value)) return 'Enter a valid number.';
  if (value < 0) {
    // Named specifically rather than "must be positive": the reason is not
    // arbitrary. Direction is carried by the debit/credit choice, so a negative
    // expense would be a cost that increases profit.
    return 'Amount cannot be negative. Use the Expense/Income setting to record direction.';
  }
  if (value > MAX_NAIRA) return `Amount cannot exceed ${naira(MAX_NAIRA)}.`;
  return null;
}

/**
 * Check the optional quantity field. An empty value is valid — quantity is not
 * required on every activity type.
 */
export function validateQuantity(raw: string): string | null {
  const trimmed = raw.trim();
  if (trimmed === '') return null;

  const value = Number(trimmed);
  if (!Number.isFinite(value)) return 'Enter a valid quantity.';
  if (value < 0) return 'Quantity cannot be negative.';
  if (value > MAX_QUANTITY)
    return `Quantity cannot exceed ${MAX_QUANTITY.toLocaleString()}.`;
  return null;
}

/** The first problem with the record, or null when it is ready to send. */
export function validateRecord(fields: { amount: string; quantity: string }): string | null {
  return validateAmount(fields.amount) ?? validateQuantity(fields.quantity);
}
