# 02 — Doc & dependency hygiene

Status: ready-for-agent

## What to build

Make the repository's documentation and dependency surface match what is actually built and what the academic scope claims, so an examiner reading the docs is not misled.

End-to-end behaviour to land:

- Tailwind is fully removed from the build: it no longer loads in `postcss.config.js` and is dropped from `devDependencies`. (Tailwind was abandoned in favour of inline styles + `styles/theme.ts`; leaving it wired is dead weight and a bundle/clarity risk.)
- `CONTEXT.md` and `PRD.md` are reconciled with reality and with each other: the single-vs-double-entry ledger contradiction is resolved (the code is single-entry), and out-of-scope drift is removed or clearly marked as out-of-scope future work, since the marked project is **manual-entry only — no sensors and no external data feeds**. Specifically includes the environmental/market drift left out of the DSS-accuracy pass: **PRD.md user stories 15 (weather APIs), 16 (soil-moisture sensors / satellite imagery), and 17 (live commodity prices)**, plus the `EnvironmentalDataPipeline` and `MarketIntelligenceModule` deep modules (PRD L60–61). (The sandboxed-Python-execution claim was already removed in the DSS-accuracy documentation pass, so it is out of this ticket's scope.)
- The frontend still type-checks and builds after the Tailwind removal.

## Acceptance criteria

- [ ] `@tailwindcss/postcss` no longer referenced in `postcss.config.js`; Tailwind removed from `frontend/package.json` devDeps
- [ ] `npm run build` succeeds with no Tailwind present
- [ ] `CONTEXT.md` and `PRD.md` agree on single-entry ledger wording
- [ ] Features not in scope (IoT/soil sensors, satellite imagery, weather APIs, commodity pricing) are removed or explicitly labelled future-work in both docs — specifically PRD user stories 15/16/17 and the `EnvironmentalDataPipeline` + `MarketIntelligenceModule` modules (sandboxed Python was already removed in the DSS-accuracy pass)

## Blocked by

- None - can start immediately
