import { describe, it, expect } from 'vitest';
import {
  MAX_NAIRA, MAX_QUANTITY, validateAmount, validateQuantity, validateRecord,
} from './recordBounds';

// These bounds are duplicated from the backend because an offline client cannot
// ask the server what its limits are. The duplication is only safe while the
// two agree, so the first block asserts the constants against the documented
// server values (backend/app/schemas/schemas.py). If someone raises MAX_NAIRA
// on one side only, this fails here rather than as records stranded in a
// farmer's offline queue.

describe('bounds match the server', () => {
  it('uses the same naira ceiling', () => {
    expect(MAX_NAIRA).toBe(1_000_000_000);
  });
  it('uses the same quantity ceiling', () => {
    expect(MAX_QUANTITY).toBe(1_000_000);
  });
});

describe('validateAmount', () => {
  it('accepts an ordinary entry', () => {
    expect(validateAmount('25000')).toBeNull();
  });

  it('accepts kobo', () => {
    expect(validateAmount('1234.56')).toBeNull();
  });

  it('accepts zero — sun drying with the farm’s own labour costs nothing', () => {
    expect(validateAmount('0')).toBeNull();
  });

  it('accepts the ceiling itself', () => {
    expect(validateAmount(String(MAX_NAIRA))).toBeNull();
  });

  it('accepts a large but real purchase', () => {
    expect(validateAmount('200000000')).toBeNull();
  });

  it('rejects a negative amount, and says why', () => {
    const error = validateAmount('-1000');
    expect(error).toBeTruthy();
    // The message has to explain the mechanism, or a farmer trying to record a
    // refund will simply retype the minus sign.
    expect(error).toMatch(/Expense\/Income/);
  });

  it('rejects an empty field', () => {
    expect(validateAmount('')).toBeTruthy();
    expect(validateAmount('   ')).toBeTruthy();
  });

  it('rejects text that is not a number', () => {
    // Number('12abc') is NaN, and JSON.stringify turns NaN into null — which the
    // server answers 422 to, permanently, on every retry from the queue.
    expect(validateAmount('12abc')).toBeTruthy();
    expect(validateAmount('abc')).toBeTruthy();
  });

  it('rejects a non-finite literal', () => {
    expect(validateAmount('Infinity')).toBeTruthy();
    expect(validateAmount('-Infinity')).toBeTruthy();
    expect(validateAmount('NaN')).toBeTruthy();
  });

  it('rejects an absurd magnitude', () => {
    expect(validateAmount('1e308')).toBeTruthy();
    expect(validateAmount(String(MAX_NAIRA * 2))).toBeTruthy();
  });
});

describe('validateQuantity', () => {
  it('treats an empty quantity as valid — it is optional', () => {
    expect(validateQuantity('')).toBeNull();
    expect(validateQuantity('  ')).toBeNull();
  });

  it('accepts a real harvest', () => {
    expect(validateQuantity('1880')).toBeNull();
  });

  it('accepts zero — a failed harvest is a recordable result', () => {
    expect(validateQuantity('0')).toBeNull();
  });

  it('rejects a negative quantity', () => {
    // A negative yield makes unit cost of production negative, and unit cost is
    // the figure a farmer prices against.
    expect(validateQuantity('-50')).toBeTruthy();
  });

  it('rejects an absurd quantity', () => {
    expect(validateQuantity(String(MAX_QUANTITY * 10))).toBeTruthy();
  });

  it('rejects a non-finite quantity', () => {
    expect(validateQuantity('Infinity')).toBeTruthy();
  });
});

describe('validateRecord', () => {
  it('passes a well-formed record', () => {
    expect(validateRecord({ amount: '25000', quantity: '100' })).toBeNull();
  });

  it('reports the amount problem first', () => {
    const error = validateRecord({ amount: '-1', quantity: '-1' });
    expect(error).toMatch(/Amount/);
  });

  it('reports a quantity problem when the amount is fine', () => {
    const error = validateRecord({ amount: '25000', quantity: '-1' });
    expect(error).toMatch(/Quantity/);
  });

  it('passes a record with no quantity at all', () => {
    expect(validateRecord({ amount: '25000', quantity: '' })).toBeNull();
  });
});
