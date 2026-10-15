# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/). Versions follow [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-10-15

### Added

- Handoff package for the simulated hotel group's three AI systems: README, architecture, decision index, eight
  runbooks, SLOs and budgets, staff guides for both apps, an admin guide, a security and privacy summary, a readiness
  checklist with evidence links and a 30/60/90-day plan.
- Daily health check (GitHub Action) that tells "asleep" (free hosting) from "down" and opens one `health-alert`
  issue when an app needs a person; optional 24-hour error-rate check from the log database.
- CI: markdown lint, link check, health-check tests.
