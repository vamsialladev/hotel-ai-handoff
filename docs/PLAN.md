# Plan (Projects 4 and 5)

Written at the start of the work, 2026-10-15. One run, no approval round; defaults chosen here are recorded as
decisions in the app repos and in [DECISIONS.md](DECISIONS.md).

**Goal.** Make the two live apps production-ready without breaking them, then hand the whole system over in a form a
hotel group's IT and operations teams could run.

**Order (by value, and so a stop at any point leaves something whole):**

1. Fix the four gaps the eval harness found (Spanish questions blocked, emergencies missed, English replies to Spanish
   emails, wrong-hotel answers). New held-out cases are written **before** the fixes and committed first, so they can't
   be tuned to. Before → after from saved runs.
2. Persistence (Neon Postgres, SQLite fallback), personal-data redaction before storage, 30-day retention, staff
   sign-in, budgets, kill switch, timeouts, Operations pages, daily health check, Docker compose.
3. This handoff package.
4. Portfolio case study, resume bullets, one video, LinkedIn kit.

**Defaults chosen:**

- Every new setting is optional. Missing = the app behaves exactly as before ("not configured", never a crash).
- One database, one table (`app_log`) for both apps, separated by app name: one free Neon project is enough.
- Redaction is deterministic regular expressions (no model, no API call) and runs before any write.
- Spanish support: a glossary from the documents' own topics into the query, answers in the guest's language; no
  translation call.
- Emergencies skip the model entirely (no readable emergency procedure exists).
- Staff sign-in is a shared password with the Admin gate's protections; SSO (OIDC) is documented as the client path.
- Budgets: assistant p95 ≤ 4.0 s and ≤ $0.50 / 1,000; agent p95 ≤ 12.0 s and ≤ $2.00 / 1,000 (about 25–60% above
  the measured values, so normal variation never fails CI but a real regression does).
- API spend cap for the whole run: $3.

**Done means:** fixes live with tests and before → after numbers; harness gates green; logs persist with redaction
(verified live once the database is connected); runbooks, SLOs, guides and checklist complete with CI green; site
updated and audited.
