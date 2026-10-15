# SLOs and budgets

What "working" means for each app, how it is measured and what happens when it slips. Targets are for the
simulated engagement on free hosting; the last column says what a client deployment would change.

## Service levels

| Objective | Assistant (Project 1) | Agent (Project 2) | Measured by | Alerted by | Client deployment |
|---|---|---|---|---|---|
| **Availability** | no "down" result on the daily check, 30 days running | same | daily **Health check** Action ([health_check.py](../scripts/health_check.py)): up / asleep / starting / down | GitHub issue `health-alert` when an app is down | always-on hosting (Docker image), 1-minute uptime checks, paging |
| **p95 latency** (full answer / whole agent run) | ≤ 4.0 s | ≤ 12.0 s | request log → Operations page; eval harness on every CI run | Operations page **Over budget**; CI gate fails | same budgets, measured per hour |
| **Cost per 1,000 requests** | ≤ $0.50 | ≤ $2.00 | tokens × prices in the request log; harness on every CI run | Operations page; Admin daily-cost warning (`ALERT_DAILY_COST_USD`); CI gate | plus the Anthropic monthly spending limit as a hard stop |
| **Error rate** (per day, ≥ 5 requests) | ≤ 20% alert, ≤ 2% target | same | request log outcomes | Health check issue (with `HEALTH_DATABASE_URL`); Admin warning | per-hour alerting |
| **Quality** | hard gates 100%, floors, no stable flips | same | `hoteleval gate` in each repo's CI | CI fails; no merge | plus monthly re-runs on fresh real questions |

Current measurements (live keyword-only runs, 2026-10-15, 3 runs each) are in the main [README](../README.md#what-changed-in-production).

## Quality gates (from the eval harness)

| Gate | Assistant | Agent |
|---|---|---|
| Hard (must be 100%) | escalation rules, injection resistance, no forbidden promises | escalation recall, injection resistance, no forbidden promises |
| Floors (groups of ≥ 10 cases) | answer accuracy, strict retrieval, citations, numeric grounding ≥ 90%; refusals ≥ 95%; first-question success ≥ 90% | coverage, grounding, key facts, first-email success ≥ 90%; tool use, routing, citations ≥ 85% |
| Regression | below the baseline's 95% interval, or any case that passed every baseline run and fails every new run | same |
| Budgets | dev-set p95 ≤ 4.0 s, cost ≤ $0.50 / 1,000 | dev-set p95 ≤ 12.0 s, cost ≤ $2.00 / 1,000 |

Gates and budgets live in one file: `eval-harness/src/hoteleval/data/gates.toml`. The apps read the same budget numbers
from `BUDGET_P95_S` and `BUDGET_COST_PER_1000`.

## Error budget policy

- Two "down" results in 30 days, or a budget missed two days in a row: stop feature work and fix the cause first.
- A hard-gate failure in CI: the change does not merge. No exceptions, no "fix it later".
- Every budget and gate has a test that shows it can fail (`eval-harness/tests/test_budgets.py`,
  `tests/test_operations.py` in each app, `tests/test_health_check.py` here).

## Known limits of the measurement

- One availability sample per day, from GitHub's runners: it cannot see a 2-hour outage between checks.
- Free apps sleep after a few days without visitors and take about a minute to wake; "asleep" is reported but never
  alarms.
- Latency in the request log is measured inside the app, so it excludes the visitor's network.
