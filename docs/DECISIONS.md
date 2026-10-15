# Decision index

Every decision is recorded in its own repo with context, decision, trade-off and result. This page is the map: the
decisions an operator or a new engineer is most likely to need, then every Project 4 decision, then the handoff
package's own.

Repos: [hotel-ops-assistant](https://github.com/vamsialladev/hotel-ops-assistant/blob/main/docs/DECISIONS.md) (57) ·
[guest-request-agent](https://github.com/vamsialladev/guest-request-agent/blob/main/docs/DECISIONS.md) (23) ·
[eval-harness](https://github.com/vamsialladev/eval-harness/blob/main/docs/DECISIONS.md) (24).

## Key decisions from Projects 1–3

| Topic | Decision | Where |
|---|---|---|
| Safety of answers | Refuse rather than guess; one fixed refusal sentence | P1 #4 |
| Data isolation | Filter by property before searching | P1 #2 |
| Prompt injection | Document and email text is data, not instructions; security lives in the tools | P1 #11, P2 #5 |
| Manager rules | "Check with a manager" rules quoted word for word from the documents | P1 #22 |
| Cost | Off-topic questions refused before the API; per-session and daily caps | P1 #23, #25 |
| Model choice | Claude Haiku 5.5: same quality as Haiku 4.5 at about a fifth of the cost | P1 #26 |
| Hosting | Streamlit Cloud runs keyword-only search (PyTorch doesn't fit) | P1 #28 |
| Safe deploys | Never mix old and new code after an in-place update | P1 #47 |
| Visitors first | Measure what visitors type first, not only what the documents answer | P1 #48 |
| Agent loop | Manual tool loop, ≤ 6 turns, timeout + retry, deterministic fallback | P2 #2, #3 |
| Human approval | Nothing is sent; refunds and exceptions only proposed to a manager | P2 #6, #12 |
| Evaluation | Recorded mode by default; projects' own metrics at pinned commits | eval-harness #2, #5 |
| Gates | Hard 100%, floors on groups ≥ 10, baseline interval, stable flips | eval-harness #7, #15 |
| Judge | No judge metric is trusted or gated (best kappa 0.29) | eval-harness #17, #21 |

## Project 4 decisions (production hardening)

| # | Decision | Repo |
|---|---|---|
| P1 51 | Spanish questions: Spanish vocabulary into the search, answers in the guest's language | hotel-ops-assistant |
| P1 52 | Emergencies in other words and in Spanish, with a zero-false-alarm test | hotel-ops-assistant |
| P1 53 | Emergencies never wait for the model | hotel-ops-assistant |
| P1 54 | Demo mode and a Staff role; SSO (OIDC) is the client path | hotel-ops-assistant |
| P1 55 | Persistent request log with personal data redacted before storage | hotel-ops-assistant |
| P1 56 | Kill switch, timeouts and retries | hotel-ops-assistant |
| P1 57 | Latency and cost budgets, checked in CI | hotel-ops-assistant |
| P2 18 | The sender's booking is looked up before the model and pins the hotel (E12) | guest-request-agent |
| P2 19 | Reply in the guest's language: detected up front, one rewrite, Spanish holding replies | guest-request-agent |
| P2 20 | Planted instructions quarantined before the model reads the email; policy statements aren't promises | guest-request-agent |
| P2 21 | The same redacted, persistent log as Project 1, separated by app name | guest-request-agent |
| P2 22 | Demo mode and a Staff role (report a draft for review) | guest-request-agent |
| P2 23 | Kill switch, budgets and an Operations page | guest-request-agent |
| EH 22 | Latency and cost budgets in the gate; `--run-file` for saved runs; a01 label widened | eval-harness |
| EH 23 | A failed model call is a failed answer, never a crashed run | eval-harness |
| EH 24 | New pins and baselines at the Project 4 releases; added cases still reported, not gated | eval-harness |

## Handoff package decisions (Project 5)

| # | Decision | Trade-off |
|---|---|---|
| H1 | The handoff is Markdown in its own repo, built from the real repos and linking to them | No separate document tool to maintain; reads well on GitHub |
| H2 | The daily health check lives here and calls Streamlit Cloud's status API, so "asleep" is never an alarm | One sample a day; documented in [SLOS.md](SLOS.md) |
| H3 | The error-rate check needs a separate, optional `HEALTH_DATABASE_URL` Actions secret | Without it, only availability is checked (stated in the run log) |
| H4 | Budgets and gates have one source of truth (`gates.toml`, mirrored by the app defaults) | Changing a budget is a reviewed change in the harness repo |
