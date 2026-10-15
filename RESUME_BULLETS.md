# Resume bullets (Projects 4 and 5)

Measured numbers only, from saved runs in [eval-harness](https://github.com/vamsialladev/eval-harness/tree/main/reports)
(live, Claude Haiku 5.5, 3 runs, 2026-10-15). No projections. Simulated client engagement, synthetic data.

## Two bullets

- **Hardened two live LLM apps (a RAG assistant and a tool-using agent) for production**, fixing four gaps found by
  held-out evals with cases written before each fix: held-out answer accuracy 67% → 85% and new cases 62% → 100%
  (Spanish questions, emergency escalation), wrong-hotel replies 0/6 → 6/6; added a Postgres request log with personal
  data redacted before storage and 30-day retention, a staff role, a kill switch, and p95 latency and cost budgets
  gated in CI (p95 2.9 s, $0.18 per 1,000 questions).
- **Delivered a client handoff package** for three AI systems: architecture with data flows and secret handling,
  eight step-by-step runbooks, SLOs, staff and admin guides, a readiness checklist with evidence and a 30/60/90-day
  plan, plus a daily GitHub Actions health check that tells a sleeping free-tier app from an outage; total API spend
  for both stages under $1.

## Every number that changed (for updating the resume PDF)

| Project | Before (published) | After (2026-10-15) | Why |
|---|---|---|---|
| Hotel Ops Assistant: answer accuracy (54 questions, live keyword-only) | 98% | **100%** (162/162) | Spanish question q37 now answered (decision 51) |
| Hotel Ops Assistant: strict retrieval | 98% (44/45) | **100%** (45/45) | same |
| Hotel Ops Assistant: full answer p95 | 2.49 s | **2.93 s** | new measurement (different day, same model) |
| Hotel Ops Assistant: cost per 1,000 questions | $0.17 | **$0.18** | new measurement |
| Hotel Ops Assistant: held-out (13 cases added in Project 3) | 67% | **85%** | Spanish + emergency fixes |
| Hotel Ops Assistant: tests / coverage | 307 / 97% | **378** (+8 Postgres tests in CI) / 97% | Project 4 tests |
| Hotel Ops Assistant: decisions | 50 | **57** | Project 4 |
| Hotel Ops Assistant: first-question success | 43% → 100% | 100% (unchanged) | – |
| Guest Request Agent: hard gates (escalation, injection, no promises) | 100% | 100% (unchanged) | – |
| Guest Request Agent: correct tool use | 96% | **100%** | booking looked up first (decision 18) |
| Guest Request Agent: citation accuracy | 94% | **100%** | same |
| Guest Request Agent: cost per 1,000 emails | $1.30 | **$1.24** | new measurement |
| Guest Request Agent: p50 / p95 | 4.6 s / 8.4 s | **4.2 s / 8.3 s** | new measurement |
| Guest Request Agent: tests / coverage | 237 / 98% | **276** (+8 in CI) / **97%** | Project 4 tests |
| Guest Request Agent: decisions | 17 | **23** | Project 4 |
| Eval Harness: labelled cases | 181 | **195** | 14 added in Project 4 |
| Eval Harness: tests / coverage / decisions | 87 / 93% / 21 | **92** / 93% / **24** | budgets, run-file gate |
| Eval Harness: judge kappa | 0.29 | 0.29 (unchanged, still not trusted) | – |
