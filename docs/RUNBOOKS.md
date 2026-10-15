# Runbooks

Step-by-step responses for the eight situations most likely to come up. Each one says how you notice it, what to do,
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
