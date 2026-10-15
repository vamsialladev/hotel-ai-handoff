"""The daily health check must tell "asleep" (free hosting, not an alarm) from "down" (an alarm). Status answers are
the shapes recorded from the live apps on 2026-10-15 (status 12 = sleeping, 5 = running, 404 = no such app)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import health_check as hc  # noqa: E402

RUNNING = {"status": 5, "platformStatus": 0, "isOwner": False}
SLEEPING = {"status": 12, "platformStatus": 0, "isOwner": False}


def test_running_and_healthy_is_up():
    assert hc.classify(200, RUNNING, 200, "ok")[0] == "up"


def test_sleeping_is_asleep_not_down():
    state, detail = hc.classify(200, SLEEPING, None, None)
    assert state == "asleep" and "wakes" in detail


def test_missing_app_is_down():
    assert hc.classify(404, None, None, None)[0] == "down"


def test_platform_errors_and_silence_are_down():
    assert hc.classify(503, None, None, None)[0] == "down"
    assert hc.classify(None, None, None, None)[0] == "down"
    assert hc.classify(200, {"unexpected": True}, None, None)[0] == "down"


def test_running_but_unhealthy_is_down():
    assert hc.classify(200, RUNNING, 500, "")[0] == "down"
    assert hc.classify(200, RUNNING, None, None)[0] == "down"


def test_other_platform_states_are_starting():
    assert hc.classify(200, {"status": 3}, None, None)[0] == "starting"


def test_asleep_apps_never_open_an_issue():
    results = [hc.Result("a", "asleep", "x"), hc.Result("b", "up", "y"), hc.Result("c", "starting", "z")]
    assert not hc.needs_a_person(results)


def test_down_opens_an_issue_with_the_runbook():
    results = [hc.Result("a", "asleep", "sleeping"), hc.Result("b", "down", "app not found (404)")]
    assert hc.needs_a_person(results)
    body = hc.issue_body(results, "https://github.com/x/y/actions/runs/1")
    assert "| b | **down** | app not found (404) |" in body and "RUNBOOKS.md" in body and "actions/runs/1" in body


def test_error_rate_alert_needs_enough_requests():
    assert hc.error_alerts(10, 3, 0.2, 5)  # 30% of 10
    assert not hc.error_alerts(10, 2, 0.2, 5)  # 20% is not over 20%
    assert not hc.error_alerts(3, 3, 0.2, 5)  # too few requests to judge
    assert not hc.error_alerts(None, None, 0.2, 5)  # not checked


def test_error_rate_alone_opens_an_issue():
    r = hc.Result("a", "up", "running", 10, 5, hc.error_alerts(10, 5, 0.2, 5))
    assert hc.needs_a_person([r]) and "error rate 5/10" in hc.issue_body([r])


def test_check_app_end_to_end_with_a_fake_server(monkeypatch):
    answers = {
        "https://x.streamlit.app/": (200, "<html>"),
        "https://x.streamlit.app/api/v2/app/status": (200, '{"status": 12}'),
    }
    monkeypatch.setattr(hc, "_fetch", lambda opener, url: answers.get(url, (None, "")))
    assert hc.check_app("x", "https://x.streamlit.app").state == "asleep"
    answers["https://x.streamlit.app/api/v2/app/status"] = (200, '{"status": 5}')
    answers["https://x.streamlit.app/~/+/_stcore/health"] = (200, "ok")
    assert hc.check_app("x", "https://x.streamlit.app").state == "up"
    answers["https://x.streamlit.app/"] = (404, "")
    assert hc.check_app("x", "https://x.streamlit.app").state == "down"


def test_main_writes_an_alert_only_when_needed(monkeypatch, tmp_path, capsys):
    monkeypatch.delenv("HEALTH_DATABASE_URL", raising=False)
    monkeypatch.setattr(hc, "check_app", lambda app, url: hc.Result(app, "asleep", "sleeping"))
    alert = tmp_path / "alert.md"
    assert hc.main(["--alert-file", str(alert)]) == 0 and not alert.exists()
    monkeypatch.setattr(hc, "check_app", lambda app, url: hc.Result(app, "down", "app not found (404)"))
    hc.main(["--alert-file", str(alert)])
    assert alert.exists() and "needs a person: yes" in capsys.readouterr().out
