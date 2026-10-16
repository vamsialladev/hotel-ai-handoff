# Security and privacy summary

Scope: the Hotel Operations Knowledge Assistant, the Guest Request Agent and the Eval Harness dashboard, as delivered
for a simulated hotel group with synthetic data. No real guest data has been processed.

## Data handled

| Data | Where it comes from | Stored? | Where |
|---|---|---|---|
| Hotel documents (policies, handbooks) | synthetic files in the assistant repo | yes, in git | GitHub |
| Synthetic bookings (80) and inbox emails (30) | generated (seed 42) | yes, in git | GitHub |
| Questions and emails typed by visitors | the public demo | yes, **redacted**, 30 days | Neon Postgres (`app_log`) |
| Answers, drafts, citations, timings, tokens, cost | the apps | yes, **redacted**, 30 days | Neon Postgres |
| Staff reports and approve/reject decisions | staff | yes, **redacted**, 30 days | Neon Postgres |
| Secrets (API key, passwords, database URL) | owner | never in git or logs | Streamlit Secrets, local `.env` |
| Analytics | none in the apps | – | – |

## Redaction before storage

Every record passes two filters before it is written anywhere (database or fallback file):

1. **Secrets:** any configured secret value (API key, passwords, the database URL) and anything shaped like an
   Anthropic key is replaced with `[redacted]`.
2. **Personal data** (`src/pii.py`, same code in both apps): emails → `[email]`, phone numbers → `[phone]`, card-like
   numbers → `[card]`, names in sign-offs, greetings and "my name is" phrases → `[name]`, the sender's name wherever
   it appears → `[name]`, booking IDs → a stable hash (`BK-1a2b3c4d`) so one booking can still be followed across
   records without revealing it.

Tests plant personal data in every field of a real record and fail if any of it reaches storage; a second test turns
redaction off and shows the check catches it.

## Retention

Records older than **30 days** (`RETENTION_DAYS`) are deleted by the apps once a day and on demand with
`python scripts/retention.py`. Without `DATABASE_URL` the apps keep logs only in temporary files that reset on restart.

**Live since 2026-10-16:** both live apps log to Neon Postgres. Checked that day: a visitor request with a planted name, email and phone was stored with all three replaced by `[name]`, `[email]`, `[phone]`, and the Operations page reads it.

## Access and sign-in

| Who | Control |
|---|---|
| Visitors | open Demo mode; session and daily caps; no write actions that affect others |
| Staff | `STAFF_PASSWORD`, constant-time compare, 5 tries → 15-minute lockout, 30-minute idle sign-out |
| Owner | `ADMIN_PASSWORD`, same controls; Admin and Operations pages only exist when it is set |
| Database | one Neon role; the connection string lives only in Secrets/`.env`; the health check uses it read-only for counts |

**For a real client:** shared passwords are not enough. Put both apps behind the client's identity provider with
OpenID Connect (Streamlit supports `st.login` with OIDC providers such as Microsoft Entra ID, Okta or Google), map an
IdP group to the Staff role and another to Owner, and remove the shared passwords. The role checks are already in one
place (`src/roles.py`), so the switch replaces the password check, not the pages.

## Model and prompt safety

- Documents and emails are **data, not instructions**: the prompts say so, the agent flags instruction-like text, and
  the eval harness gates prompt-injection resistance at 100%.
- **Human approval** before anything leaves: the agent never sends; refunds, upgrades and exceptions are only proposed
  to a manager.
- **Emergencies** (fire, smoke, gas, injuries, someone unresponsive; English and Spanish) never reach the model in the
  assistant: a fixed safety message and the manager note, because no readable emergency procedure exists.
- **Kill switch** (`KILL_SWITCH`) stops all model calls at once.

## Known limitations

- Name redaction is pattern-based: a bare name in free text without a cue ("tell Maria the pool is open") can survive.
  The demo asks visitors not to type personal details; a client deployment should add an NER-based redactor and test
  it on their own data.
- The public demo is open to anyone; the caps and the Anthropic monthly spending limit are the cost controls.
- Free hosting: apps sleep, and Streamlit Community Cloud is not a client-grade host (no SLA, no private network).
- The LLM judge in the eval harness is not trusted (best kappa 0.29 against owner labels) and is not used for any gate.
- Neon's free plan keeps a short restore window; a client would set backups and retention to their own policy.

## Reporting a vulnerability

Email <vamsialla.dev@gmail.com>. Please don't open a public issue for security problems.
