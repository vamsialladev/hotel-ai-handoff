# Security

This repository holds documentation and a health-check script; it has no secrets and processes no personal data.
The health check reads `HEALTH_DATABASE_URL` from GitHub Actions secrets (optional) and prints counts only.

The systems it documents, their data handling, redaction and known limitations: [docs/SECURITY_PRIVACY.md](docs/SECURITY_PRIVACY.md).

Report a vulnerability by email to <vamsialla.dev@gmail.com>, not in a public issue.

## Threat model and OWASP Top 10 for LLM applications (2025)

For the two apps this package hands over. Each control is built and tested in the app's repo.

| # | Risk | Control |
|---|---|---|
| LLM01 | Prompt injection | Guest email and document text treated as data; planted instructions quarantined (agent); injection cases are 100% CI gates in both apps |
| LLM02 | Sensitive information disclosure | Personal data redacted and booking IDs hashed before any log write; sender-scoped booking lookup; 30-day retention |
| LLM03 | Supply chain | Pinned dependencies, pip-audit and gitleaks in CI, Dependabot, secret scanning with push protection |
| LLM04 | Data and model poisoning | Policy documents edited by named owners; index fingerprint; eval re-run after document changes ([runbooks](docs/RUNBOOKS.md)) |
| LLM05 | Improper output handling | Answers escaped before display; typed tool schemas; no model output is executed |
| LLM06 | Excessive agency | The agent only proposes; refunds, comps, upgrades and changes need a manager; nothing is sent without staff approval |
| LLM07 | System prompt leakage | No secrets in prompts; secrets only in the host's secrets store |
| LLM08 | Vector and embedding weaknesses | Retrieval filtered by property; keyword-only on the live demo |
| LLM09 | Misinformation | Citations required; numeric and fact grounding checks; refuse when the documents don't say |
| LLM10 | Unbounded consumption | Per-session and daily caps, 30 s timeouts, p95 and cost budgets in CI, kill switch |
