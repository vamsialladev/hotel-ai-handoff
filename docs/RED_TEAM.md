# Red team

This repo is the handoff package (runbooks, service levels, guides, checklist) plus a health-check script. It has
no app and no model of its own, so there's nothing to attack here. `scripts/health_check.py` only reads the two apps'
public status (Streamlit's status API and each app's health check) and, if `HEALTH_DATABASE_URL` is set, counts
errors in the request log with read-only access.

The two apps it hands over were red-teamed in their own repos, after the production fixes:

| App | Red-team results |
|---|---|
| Knowledge Assistant (v1.6.0 and later) | [hotel-ops-assistant](https://github.com/vamsialladev/hotel-ops-assistant), `docs/RED_TEAM.md` |
| Guest Request Agent (v1.1.0 and later) | [guest-request-agent](https://github.com/vamsialladev/guest-request-agent), `docs/RED_TEAM.md` |
| Shared corpus (48 cases) | [hotel-ai-platform](https://github.com/vamsialladev/hotel-ai-platform), `docs/RED_TEAM.md` |

What the client's team should do when someone tries a prompt injection is runbook 4,
[Prompt-injection attempt](RUNBOOKS.md#4-prompt-injection-attempt).
