# 07 — Inbound USSD/SMS activity-log entry

Status: ready-for-agent

## What to build

A farmer on a feature phone, with no smartphone or data, can record a farm activity by SMS/USSD — directly serving the socio-technical adoption barrier the project exists to overcome. The `UssdPage` is currently a ComingSoon stub.

End-to-end behaviour to land:

- An inbound webhook endpoint that accepts an SMS/USSD message (sender phone number + text), parses a simple structured log syntax (activity type, quantity, amount, debit/credit), and creates a paired Operational Log + Financial Transaction by reusing the existing ledger service — so a phone-entered record is indistinguishable from an app-entered one and shows up in the same P&L.
- The sender's phone number maps to a farm (registered against the farm/user), so the inbound message lands in the right farm's ledger and nowhere else.
- A confirmation reply payload (the text the gateway would send back) acknowledging the recorded entry or explaining a parse error.
- The `UssdPage` stub is replaced with owner-side UI to register/verify the phone number(s) allowed to submit by SMS, and a short syntax reference.

## Acceptance criteria

- [ ] Webhook endpoint parses the agreed SMS/USSD syntax and creates a paired log + transaction via the ledger service
- [ ] Sender phone number is resolved to a farm; an unregistered number is rejected
- [ ] Malformed messages return a clear confirmation/error reply payload without creating a record
- [ ] Phone-entered records appear in the same P&L as app-entered ones (test proves it)
- [ ] `UssdPage` lets an owner register/verify allowed numbers; the ComingSoon stub is gone

## Blocked by

- 04 — Authentication + per-farm data boundary
