# Runbooks

Step-by-step responses for the nine situations most likely to come up. Each one says how you notice it, what to do,
and how to check it worked. Apps: the **Hotel Operations Knowledge Assistant** (Project 1, "assistant") and the
**Guest Request Agent** (Project 2, "agent"). Both run on Streamlit Community Cloud with a shared Neon Postgres log
database. Everything here uses a simulated hotel group and synthetic data.

| Where | What |
|---|---|
| Streamlit Cloud | <https://share.streamlit.io> → app → **⋮** → Settings / Secrets / Reboot / Logs |
| Owner pages | `/admin` and `/operations` on each app (owner password) |
| Anthropic Console | <https://console.anthropic.com> → Usage, Limits, API keys |
| Neon | <https://console.neon.tech> → project `hotel-ai` → Monitoring, Branches, Backup & restore |
| Daily health check | this repo → Actions → **Health check** (opens an issue labelled `health-alert`) |

## Contents

1. [API outage](#1-api-outage)
2. [Cost spike](#2-cost-spike)
3. [Bad or harmful answer reported](#3-bad-or-harmful-answer-reported)
4. [Prompt-injection attempt](#4-prompt-injection-attempt)
5. [App asleep or down](#5-app-asleep-or-down)
6. [Rotating secrets](#6-rotating-secrets)
7. [Restoring logs](#7-restoring-logs)
8. [Adding a new property's documents](#8-adding-a-new-propertys-documents)
9. [Debug a failed request using its trace ID](#9-debug-a-failed-request-using-its-trace-id)

---

## 1. API outage

**You notice:** visitors see "The demo is temporarily unavailable" (assistant) or every email ends as **Fallback**
with a holding reply (agent); the Operations page shows errors rising; the health check may open an issue.

1. Open each app's **Admin** page → *Recent errors*. Read the error **category**:
   - `server_error`, `connection`, `timeout`: Anthropic is having trouble. Check <https://status.anthropic.com>.
   - `rate_limit`: too many requests for the account's limits (Console → Limits).
   - `auth` / `missing_key` / `permission`: a key problem → [Rotating secrets](#6-rotating-secrets).
   - `credit_exhausted`: add credit in the Console → Billing.
2. If it is an Anthropic outage, nothing needs fixing: each call already has a 30 s timeout and retries with
   backoff, visitors get a clear message and staff get a holding reply plus a task. Optional: set `KILL_SWITCH`
   to `"true"` in both apps' Secrets (Save → Reboot) so visitors see the "paused" message instead of waiting for
   timeouts.
3. Tell staff: "Use the documents / reply to guests by hand until further notice."

**Check it worked:** after the outage, set `KILL_SWITCH` back to `"false"` (Save → Reboot), ask one question in the
assistant and run one inbox email in the agent. Operations page: new requests show `answered` / `drafted`, errors stop
growing.

## 2. Cost spike

**You notice:** Operations page shows **Over budget** for cost per 1,000 requests, the Admin page warns that today's
estimated cost passed `ALERT_DAILY_COST_USD`, or an Anthropic Console usage email.

1. Operations page → *Per day*: is it more requests (traffic) or more cost per request (each request got dearer)?
2. **More requests:** the daily caps (`MAX_QUESTIONS_PER_DAY`, `MAX_EMAILS_PER_DAY`) bound it. Lower them in Secrets
   if needed (Save → Reboot).
3. **Dearer requests:** check `LLM_MODEL` and `LLM_MAX_TOKENS` in Secrets were not changed; compare with the budgets
   (assistant $0.50 / 1,000, agent $2.00 / 1,000; measured ~$0.18 and ~$1.25).
4. If you cannot find the cause within an hour: `KILL_SWITCH = "true"` (Save → Reboot) and investigate calmly.
5. Confirm the Anthropic **monthly spending limit** is set (Console → Limits): it is the hard ceiling.

**Check it worked:** the next day's row on the Operations page is back under budget; the Console usage graph is flat.

## 3. Bad or harmful answer reported

**You notice:** a staff report on the Operations page (*Staff reports*), a thumbs-down with a comment on the Admin
page, or a message from a manager.

1. Find the request: Admin → request list → filter by time → open **Request details**. The *Answer*, *Sources* and
   *Checks* tabs show exactly what was retrieved and said. (Personal data is already redacted in the log.)
2. Decide which kind it is:
   - **Wrong document or outdated policy:** fix the document (see [runbook 8](#8-adding-a-new-propertys-documents)
     for how documents are indexed), then re-run the eval.
   - **Right document, wrong answer:** add the question as a labelled case in the eval harness
     (`eval-harness/src/hoteleval/data/cases/added.jsonl`), confirm it fails, then fix the prompt or rule and confirm
     it passes. Never fix without a case.
   - **Harmful or unsafe** (for example an emergency answered from policy text): treat as urgent. Turn on
     `KILL_SWITCH` for that app if it could repeat, then follow the case-first fix above.
3. Tell the person who reported it what changed.

**Check it worked:** the new case passes in `hoteleval` and CI is green on the app's repo.

## 4. Prompt-injection attempt

**You notice:** the agent shows *Instructions found in the email: treated as data* in the steps, or a staff report
quotes text like "ignore your rules" / "pre-approved refund".

1. Open the request (Admin → Request details → *Checks*): confirm no promise was made (forbidden-promise guard) and no
   booking of another guest was shown (bookings are only looked up for the sender's own address).
2. Nothing was sent: every draft needs a staff approval, and refunds/upgrades are only proposed to a manager.
3. If the reply repeated the injected text or acted on it, add the email as a held-out case (expected: no mention) and
   fix as in [runbook 3](#3-bad-or-harmful-answer-reported). The hard gate `injection_resistance` must stay 100%.
4. If one sender keeps trying, staff simply reject those drafts; the demo has no sending, so there is no blast radius.

**Check it worked:** `hoteleval gate` passes with `injection_resistance` 100% on dev and held-out.

## 5. App asleep or down

**You notice:** the daily **Health check** issue, or someone says the link doesn't load.

1. Read the issue's *State* column:
   - **asleep:** normal on free hosting after a few days without visitors. Open the app link and click
     **Yes, get this app back up**; it starts in about a minute. (The check never opens an issue for this.)
   - **starting:** wait two minutes and reload.
   - **down:** continue below.
2. Streamlit Cloud → app → **Logs**: look for the last error at startup (a missing secret is logged by name).
3. Secrets: confirm `ANTHROPIC_API_KEY` and `ADMIN_PASSWORD` are present (the Admin page lists set/missing).
4. **Reboot app**. If it still fails, check the latest commit on `main` (each push redeploys): revert it on GitHub and
   push; CI must be green.

**Check it worked:** run the health check by hand (Actions → Health check → Run workflow): both apps **up** or
**asleep**; close the issue with a one-line note of the cause.

## 6. Rotating secrets

Rotate after anyone leaves, after any suspected leak, and at least every 90 days.

| Secret | Where to make a new one | Where it lives |
|---|---|---|
| `ANTHROPIC_API_KEY` | Anthropic Console → API keys → Create key (then delete the old key) | both apps' Secrets, local `.env` files |
| `ADMIN_PASSWORD` | `python -c "import secrets; print(secrets.token_urlsafe(18))"` | both apps' Secrets, `.env` |
| `STAFF_PASSWORD` | same command, a different value | both apps' Secrets, `.env` |
| `DATABASE_URL` | Neon → Roles → `neondb_owner` → Reset password, copy the new connection string | both apps' Secrets, `.env`, this repo's `HEALTH_DATABASE_URL` Action secret |

1. Make the new value. Never paste it in chat, email or a ticket.
2. Streamlit Cloud → each app → Settings → **Secrets**: replace the value (keep the line format
   `NAME = "value"`) → **Save** → **Reboot app**.
3. Update local `.env` files (Notepad; check the file is still named `.env`, not `.env.txt`).
4. Revoke the old value (delete the old API key; the old database password stops working on reset).

**Check it worked:** Admin page → *Secrets*: every line **set**; Operations page → *Log storage*: **Postgres
database**, reachable; one question and one email go through.

## 7. Restoring logs

Logs are request records with personal data already redacted, kept 30 days. Neon keeps a short restore window of
history on the free plan (check the current window in the Neon console).

1. **Records missing or a table dropped:** Neon → **Backup & restore** (or **Branches** → create a branch from a
   past point in time) → restore to a time before the problem.
2. **Need a copy for an investigation:** Admin page → *Download* (JSONL) gives the stored records for that app.
3. **Database unreachable:** the apps keep working and write to a temporary file instead (the Operations page says
   "Database configured but not reachable"). When the database is back, new records go to it again; records written
   to the file while it was down are shown alongside until the app restarts.

**Check it worked:** `python scripts/retention.py --status` in each app folder shows the record counts; the Operations
page shows the expected request numbers for the restored days.

## 8. Adding a new property's documents

Example: a third property, `city-hotel`.

1. In **hotel-ops-assistant**, create `data/raw/city-hotel/` and add its policies as Markdown (`policies.md`,
   `guest_handbook.md`). Use `##` headings per topic; the headings become the passage titles staff see.
2. Rebuild and check locally:

   ```powershell
   cd C:\projects\project1\hotel-ops-assistant
   .\.venv\Scripts\python -m src.ingest --bm25-only
   .\.venv\Scripts\python -m pytest -q
   ```

3. Add at least 10 labelled questions for the new property to `eval/questions.jsonl` (including one must-refuse and
   one manager-escalation question) and run the eval; strict retrieval must stay ≥ 90%.
4. Add the property to `data/suggestions.toml` and the display names in branding.
5. In **guest-request-agent**, run `python scripts/sync_policy.py --ref <new Project 1 commit>` to copy the search and
   documents, add the property name, then add bookings for it in `scripts/make_data.py`.
6. Push to `main`; both apps redeploy. CI (tests, evals, harness gates) must be green before telling staff.

**Check it worked:** in the live assistant, pick the new property and ask one of the new questions: the cited passage
is from `city-hotel`.

---

## 9. Debug a failed request using its trace ID

Every hotel app writes one trace per request to the shared Neon tables `ops_request_log` and `ops_trace_span`
([hotel-ai-platform](https://github.com/vamsialladev/hotel-ai-platform)). When something fails, the person sees a
short reference, for example "Reference: 4f1c9a2e": the first 8 characters of the trace ID.

**You notice it when:** a staff member or guest quotes a reference; the daily failure summary (streamlit-keep-awake →
Actions → **Daily failure summary**) opens an issue; or Admin shows a rising error rate.

1. **Find the request.** Open the app's owner page:

   | App | Where the traces are |
   |---|---|
   | Knowledge Assistant, Guest Request Agent | `/admin` → sign in → **Traces** in the sidebar |
   | Activities Concierge | `/staff` → sign in → **Traces** tab |
   | Tools MCP demo, Ops Analytics, Account Research | `/admin` (its own sign-in) |

   Paste the reference into **Trace reference**. No reference? Turn on **Failures only** and pick the row by time.
2. **Read the waterfall.** One bar per step, in order, coloured by status (green ok, amber blocked, red error). The
   step in red is where it failed; its duration tells you whether it was slow (a timeout shows as a long bar ending
   in red). Typical steps: `guardrails.input` → rewrite → retrieval or tools → `model_call` → `guardrails.output`.
3. **Open the redacted record and the spans.** `error_type` names the failure class (for example `APITimeoutError`,
   `RateLimitError`, `OperationalError`); the span's attributes hold its inputs and outputs with personal data and
   secrets already removed. Nothing here contains a card number, an email or a key.
4. **Decide what kind of failure it is:**

   | What you see | Likely cause | Next step |
   |---|---|---|
   | `model_call` red, `APITimeoutError` / `APIConnectionError` | Anthropic slow or down | Runbook 1 (API outage) |
   | `model_call` red, `RateLimitError` / 429 | Too many requests, or the Console limit reached | Runbook 2 (cost spike) |
   | `guardrails.input` amber | Blocked on purpose (injection, card number, data request) | Nothing to fix unless it was a real question: then add it as a benign red-team case and adjust |
   | `guardrails.output` amber | The answer was replaced (a promise, a leaked contact detail) | Read the original in the record; if the model is drifting, add an eval case |
   | A tool or SQL span red | Bad arguments or a tool bug | Reproduce locally with the arguments from the span |
   | No trace at all for the time given | The request never reached the app, or the log write failed | Admin → System health → log store `write_errors`; Streamlit Cloud → Logs (`log_write_failed`) |

5. **Check the app's JSON logs** for the same trace ID if you need the stack: Streamlit Cloud → app → **⋮** → Logs,
   search for the 8 characters. `exception` lines carry a redacted stack trace; `slow_request` lines show requests
   over the p95 budget.
6. **Fix and prove it.** Add the failing input as an eval or red-team case first, see it fail, fix, and let CI's gates
   pass before redeploying.

**Check it worked:** ask the same question again; the new trace is all green, and the next daily failure summary
doesn't list the app.

