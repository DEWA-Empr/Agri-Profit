import type { PartialBudgetRequest, PartialBudgetResponse } from '../../types/domain';

// The partial budget, computed on the device.
//
// WHY THIS EXISTS ALONGSIDE THE ENDPOINT. POST /dss/partial-budget is the
// canonical home of this arithmetic and is what the form calls whenever it can
// reach the network. But the appraisal touches no ledger row, reads nothing and
// writes nothing — it is four numbers the user just typed — so requiring a
// round trip would make the one screen on this platform that has no reason to
// need connectivity the one screen that stops working without it. A farmer
// standing in a field deciding whether to hire a thresher is exactly the case
// the offline-first design is for.
//
// The duplication is one subtraction, and it is bounded: this file must mirror
// enterprise_service.partial_budget and nothing else. If that function ever
// grows a term, this goes with it or the fallback starts lying — which is why
// the fallback is LABELLED in the UI rather than being silently substituted.

export const partialBudgetLocal = (input: PartialBudgetRequest): PartialBudgetResponse => {
  const benefits = input.added_revenue_ngn + input.reduced_cost_ngn;
  const costs = input.lost_revenue_ngn + input.added_cost_ngn;
  return {
    ...input,
    benefits_ngn: benefits,
    costs_ngn: costs,
    // Signed and unclamped, exactly as the backend returns it. A negative
    // result says the change is not worth making, which is the answer the
    // farmer most needs and the one a Math.max would destroy.
    net_change_ngn: benefits - costs,
  };
};
