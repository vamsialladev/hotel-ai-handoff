# Admin guide

For the person who owns and operates both apps. Covers settings, the owner pages, daily and monthly checks, and
deploys. The runbooks ([RUNBOOKS.md](RUNBOOKS.md)) cover incidents.

## Access

| Role | How | Can |
|---|---|---|
| Visitor (Demo mode) | open link, no sign-in | ask questions / run emails within the session and daily caps |
| Staff | sidebar → Staff sign-in (`STAFF_PASSWORD`) | everything in Demo mode, report an answer or draft for review, no per-session cap |
| Owner | `/admin` (`ADMIN_PASSWORD`) | Admin and Operations pages, downloads |

Both passwords are compared in constant time; five wrong tries lock that browser session for 15 minutes; idle
sessions sign out after 30 minutes. These are demo-grade controls: a client deployment would sit behind the client's
SSO (see [SECURITY_PRIVACY.md](SECURITY_PRIVACY.md#access-and-sign-in)).

## Settings (Streamlit Cloud → app → ⋮ → Settings → Secrets)

Format: one `NAME = "value"` per line, top level, value in double quotes. After **Save**, click **Reboot app**.
`python scripts/make_secrets.py` in each app folder builds the full block from your local `.env` (it prints only which
settings are set or missing, never values).

| Setting | Required | Default | What it does |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | yes | – | model access |
| `ADMIN_PASSWORD` | yes | – | owner pages; without it they don't exist |
| `DATABASE_URL` | no | – (temporary files) | persistent, redacted request log (Neon Postgres) |
| `STAFF_PASSWORD` | no | – (Demo mode only) | staff sign-in |
| `RETENTION_DAYS` | no | 30 | older log records are deleted daily |
| `BUDGET_P95_S` | no | 4.0 (assistant) / 12.0 (agent) | p95 latency budget on the Operations page |
| `BUDGET_COST_PER_1000` | no | 0.50 / 2.00 | cost budget per 1,000 requests |
| `KILL_SWITCH` | no | false | `true` pauses every model call |
| `MAX_QUESTIONS_PER_DAY` / `MAX_EMAILS_PER_DAY` | no | 200 / 150 | daily caps for the public demo |
| `PRICE_IN_PER_M` / `PRICE_OUT_PER_M` | no | unset (assistant) / 0.10 and 0.50 (agent) | USD per million tokens, for cost estimates; the assistant shows "not configured" until set |

## Owner pages

- **Admin** (`/admin`): health (uptime, errors, secrets set/missing with likely causes), usage, the full request log
  (filters, request details in 7 tabs, JSONL/CSV downloads) and feedback. The log note says where records are kept
  ("Stored in the database (postgres), kept for 30 days, personal data redacted" when the database is set).
- **Operations** (`/operations`, after signing in on Admin): requests, errors, p50/p95 latency, cost per day,
  refusals/fallbacks, escalations, **budget status**, log storage, kill switch state and **staff reports**.

## Routine

| When | Check |
|---|---|
| Daily (automatic) | the **Health check** Action in this repo; an issue appears only when an app is down or errors are high |
| Weekly | Operations page, 7-day window: within budget, no open staff reports |
| Monthly | Anthropic Console usage and the **monthly spending limit**; Neon storage; Dependabot PRs in each repo |
| Every 90 days | [rotate secrets](RUNBOOKS.md#6-rotating-secrets) |

## Deploys

Every push to `main` redeploys that app on Streamlit Cloud and runs CI (lint, tests with coverage, evals, harness
gates incl. budgets). Rules: change through a pull request, CI green before merge, then open the live app and run
one question / one email. The harness gate must pass: hard gates at 100%, no metric below its floor or baseline
interval, no stable flip, latency and cost within budget.

## Local run

```powershell
cd C:\projects\project1\hotel-ops-assistant
docker compose up --build
```

Opens <http://localhost:8501> with its own Postgres (the same for the agent's folder). Without Docker, see each repo's
README → *Run it locally*.
