# Handoff readiness checklist

Every item links to its evidence. Items that need the owner's own accounts or passwords are marked **owner** and are
checked by the owner, never by the builder. Status as of 2026-10-15.

## Systems

- [x] Assistant live with the Project 4 fixes (v1.6.0) — [release](https://github.com/vamsialladev/hotel-ops-assistant/releases/tag/v1.6.0), [changelog](https://github.com/vamsialladev/hotel-ops-assistant/blob/main/CHANGELOG.md)
- [x] Agent live with the Project 4 fixes (v1.1.0) — [release](https://github.com/vamsialladev/guest-request-agent/releases/tag/v1.1.0), [changelog](https://github.com/vamsialladev/guest-request-agent/blob/main/CHANGELOG.md)
- [x] Eval harness gates both apps in CI, budgets included (v1.2.0) — [gates.toml](https://github.com/vamsialladev/eval-harness/blob/main/src/hoteleval/data/gates.toml), [release](https://github.com/vamsialladev/eval-harness/releases/tag/v1.2.0)
- [x] Docker compose (app + Postgres) for both apps — [assistant](https://github.com/vamsialladev/hotel-ops-assistant/blob/main/docker-compose.yml), [agent](https://github.com/vamsialladev/guest-request-agent/blob/main/docker-compose.yml)

## Quality

- [x] The four Project 4 backlog gaps fixed, each with cases written before the fix and a before → after — [README](../README.md#what-changed-in-production)
- [x] Hard gates at 100% on the release runs — [assistant report](https://github.com/vamsialladev/eval-harness/blob/main/reports/p1-v1.6.0-2026-10-15.md), [agent report](https://github.com/vamsialladev/eval-harness/blob/main/reports/p2-v1.1.0-2026-10-15.md)
- [x] Every new check shown able to fail (budgets, redaction, false alarms, health check) — [SLOS.md](SLOS.md#error-budget-policy)

## Operations

- [x] Runbooks for the eight likely incidents — [RUNBOOKS.md](RUNBOOKS.md)
- [x] SLOs and budgets, how each is measured and alerted — [SLOS.md](SLOS.md)
- [x] Daily health check (asleep vs down) with tests — [workflow](../.github/workflows/health-check.yml), [tests](../tests/test_health_check.py)
- [x] Kill switch and Operations page in both apps — [ADMIN_GUIDE.md](ADMIN_GUIDE.md#owner-pages)
- [x] Staff guides (plain language) and an admin guide — [assistant](STAFF_GUIDE_ASSISTANT.md), [agent](STAFF_GUIDE_AGENT.md), [admin](ADMIN_GUIDE.md)

## Security and privacy

- [x] Personal data redacted before storage, tested on every field — [SECURITY_PRIVACY.md](SECURITY_PRIVACY.md#redaction-before-storage)
- [x] 30-day retention, daily and on demand — [SECURITY_PRIVACY.md](SECURITY_PRIVACY.md#retention)
- [x] Secrets only in Streamlit Secrets / `.env`; full-history secret scans clean before every push — [ARCHITECTURE.md](ARCHITECTURE.md#where-secrets-live)
- [x] Secret scanning and push protection on every repo — GitHub → Settings → Code security
- [x] SSO (OIDC) path documented for a client — [SECURITY_PRIVACY.md](SECURITY_PRIVACY.md#access-and-sign-in)

## Owner (needs the owner's accounts)

- [ ] **owner** Neon database created and `DATABASE_URL` + `STAFF_PASSWORD` added to both apps' Secrets — then the
  Operations page shows "Postgres database, reachable" and a question appears in the log after a reboot
- [ ] **owner** Live staff sign-in checked on both apps with the real `STAFF_PASSWORD`
- [ ] **owner** Live Admin and Operations pages checked by hand
- [ ] **owner** `HEALTH_DATABASE_URL` added as an Actions secret here (enables the error-rate check)
- [ ] **owner** Anthropic monthly spending limit confirmed
