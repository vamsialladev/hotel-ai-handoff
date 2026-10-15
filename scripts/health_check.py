"""Daily health check for the live apps (run by .github/workflows/health-check.yml).

For each app it answers one question: up, asleep, or down?

    up       Streamlit Cloud reports the app running (status 5) and the app's own health endpoint says "ok"
    asleep   Streamlit Cloud reports the app sleeping (status 12). Free apps sleep after a few days without
             visitors; the first visitor wakes them. Not an alarm.
    starting Streamlit Cloud reports another state (booting, updating). Not an alarm on its own.
    down     the app is missing (404), the platform or the app answers with an error, or nothing answers.

With HEALTH_DATABASE_URL set (a read-only use of the apps' log database), it also checks the last 24 hours of
requests: an error rate above --max-error-rate (with at least --min-requests requests) is an alarm.

    python scripts/health_check.py                      # print the report, exit 0
    python scripts/health_check.py --alert-file alert.md   # also write an issue body when something needs a person

Never prints the database URL or any log content: counts only.
"""

import argparse
import http.cookiejar
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field

APPS = {
    "hotel-ops-assistant": "https://hotel-ops-assistant.streamlit.app",
    "guest-request-agent": "https://guest-request-agent.streamlit.app",
}
RUNNING, SLEEPING = 5, 12
TIMEOUT_S = 30


@dataclass
class Result:
    app: str
    state: str  # up | asleep | starting | down
    detail: str
    requests_24h: int | None = None
    errors_24h: int | None = None
    alerts: list[str] = field(default_factory=list)


def classify(status_http: int | None, payload: dict | None, health_http: int | None, health_body: str | None) -> tuple:
    """(state, detail) from the platform status call and the app's health call. Pure: unit-tested with recordings."""
    if status_http is None:
        return "down", "no answer from Streamlit Cloud (network error or timeout)"
    if status_http == 404:
        return "down", "app not found (404): deleted, renamed or the URL is wrong"
    if status_http >= 500:
        return "down", f"Streamlit Cloud error (HTTP {status_http})"
    if status_http != 200 or not isinstance(payload, dict) or "status" not in payload:
        return "down", f"unexpected status answer (HTTP {status_http})"
    status = payload.get("status")
    if status == SLEEPING:
        return "asleep", "sleeping on free hosting: the first visitor wakes it (click 'Yes, get this app back up')"
    if status != RUNNING:
        return "starting", f"Streamlit Cloud state {status} (booting or updating)"
    if health_http == 200 and (health_body or "").strip() == "ok":
        return "up", "running and healthy"
    return "down", f"running on Streamlit Cloud but the app's health check failed (HTTP {health_http})"


def error_alerts(requests: int | None, errors: int | None, max_rate: float, min_requests: int) -> list[str]:
    if requests is None or errors is None:
        return []
    if requests >= min_requests and errors / requests > max_rate:
        return [f"error rate {errors}/{requests} ({errors / requests:.0%}) in the last 24 h is over {max_rate:.0%}"]
    return []


def needs_a_person(results: list[Result]) -> bool:
    return any(r.state == "down" or r.alerts for r in results)


def issue_body(results: list[Result], run_url: str | None = None) -> str:
    lines = [
        "Daily health check found a problem.",
        "",
        "| App | State | Detail | Requests / errors (24 h) |",
        "|---|---|---|---|",
    ]
    for r in results:
        counts = "not checked" if r.requests_24h is None else f"{r.requests_24h} / {r.errors_24h}"
        lines.append(f"| {r.app} | **{r.state}** | {r.detail} | {counts} |")
    alerts = [f"- {r.app}: {a}" for r in results for a in r.alerts]
    if alerts:
        lines += ["", "Alerts:", *alerts]
    lines += ["", "Runbook: docs/RUNBOOKS.md → 'App asleep or down' and 'API outage'."]
    if run_url:
        lines.append(f"Workflow run: {run_url}")
    return "\n".join(lines) + "\n"


def _fetch(opener, url: str) -> tuple[int | None, str]:
    try:
        with opener.open(url, timeout=TIMEOUT_S) as resp:
            return resp.status, resp.read(200_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, ""
    except (urllib.error.URLError, TimeoutError, OSError):
        return None, ""


def check_app(app: str, base: str) -> Result:
    """Visit the app once (Streamlit Cloud sets a session cookie through a redirect), then ask for its status."""
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    opener.addheaders = [("User-Agent", "hotel-ai-handoff-health-check/1.0")]
    first, _ = _fetch(opener, base + "/")
    if first == 404:
        state, detail = classify(404, None, None, None)
        return Result(app, state, detail)
    status_http, body = _fetch(opener, base + "/api/v2/app/status")
    try:
        payload = json.loads(body) if status_http == 200 else None
    except ValueError:
        payload = None
    health_http, health_body = (None, None)
    if isinstance(payload, dict) and payload.get("status") == RUNNING:
        health_http, health_body = _fetch(opener, base + "/~/+/_stcore/health")
    state, detail = classify(status_http, payload, health_http, health_body)
    return Result(app, state, detail)


def log_counts(url: str, apps: list[str]) -> dict[str, tuple[int, int]]:
    """Requests and errors per app in the last 24 hours, from the apps' shared app_log table. Counts only."""
    import psycopg

    sql = (
        'SELECT app, COUNT(*), SUM(CASE WHEN data LIKE \'%%"outcome": "error"%%\' THEN 1 ELSE 0 END) '
        "FROM app_log WHERE stream = 'requests' AND ts >= to_char(now() at time zone 'utc' - interval '24 hours', "
        "'YYYY-MM-DD\"T\"HH24:MI:SS') AND app = ANY(%s) GROUP BY app"
    )
    with psycopg.connect(url, connect_timeout=15) as conn:
        rows = conn.execute(sql, (apps,)).fetchall()
    return {app: (int(n), int(e or 0)) for app, n, e in rows}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Daily health check for the live apps")
    parser.add_argument("--alert-file", help="write an issue body here when something needs a person")
    parser.add_argument("--max-error-rate", type=float, default=0.2)
    parser.add_argument("--min-requests", type=int, default=5)
    args = parser.parse_args(argv)

    results = [check_app(app, url) for app, url in APPS.items()]
    db_url = os.getenv("HEALTH_DATABASE_URL", "").strip()
    if db_url:
        try:
            counts = log_counts(db_url, list(APPS))
            for r in results:
                r.requests_24h, r.errors_24h = counts.get(r.app, (0, 0))
                r.alerts = error_alerts(r.requests_24h, r.errors_24h, args.max_error_rate, args.min_requests)
        except Exception as exc:  # noqa: BLE001 - reported by type only, never with the URL
            print(f"error-rate check skipped: database not reachable ({type(exc).__name__})")
    else:
        print("error-rate check skipped: HEALTH_DATABASE_URL is not set")

    for r in results:
        counts = "" if r.requests_24h is None else f" · 24 h: {r.requests_24h} requests, {r.errors_24h} errors"
        print(f"{r.app}: {r.state} · {r.detail}{counts}")
        for a in r.alerts:
            print(f"  ALERT {a}")
    if needs_a_person(results):
        print("needs a person: yes")
        if args.alert_file:
            run_url = None
            if os.getenv("GITHUB_RUN_ID"):
                server, repo = os.getenv("GITHUB_SERVER_URL"), os.getenv("GITHUB_REPOSITORY")
                run_url = f"{server}/{repo}/actions/runs/{os.getenv('GITHUB_RUN_ID')}"
            with open(args.alert_file, "w", encoding="utf-8") as f:
                f.write(issue_body(results, run_url))
    else:
        print("needs a person: no")
    return 0


if __name__ == "__main__":
    sys.exit(main())
