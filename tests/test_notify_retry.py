from types import SimpleNamespace

import pytest
import requests

from stock_strategies import notify


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")
    sleeps = []
    monkeypatch.setattr(notify.time, "sleep", lambda s: sleeps.append(s))
    return sleeps


def _sequence(monkeypatch, outcomes):
    calls = []

    def fake_post(*_args, **kwargs):
        calls.append(kwargs.get("timeout"))
        outcome = outcomes[len(calls) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(notify.requests, "post", fake_post)
    return calls


def test_first_fails_second_succeeds(monkeypatch, _env):
    ok = SimpleNamespace(ok=True, text="", status_code=200)
    calls = _sequence(monkeypatch, [requests.exceptions.ConnectionError("reset"), ok])

    assert notify.send_telegram("hi") is True
    assert calls == [10, 10]
    assert _env == [2]


def test_all_retries_fail_does_not_raise(monkeypatch, _env, capsys):
    err = requests.exceptions.ConnectionError("reset")
    calls = _sequence(monkeypatch, [err, err, err, err])

    assert notify.send_telegram("hi") is False
    assert calls == [10, 10, 10, 10]
    assert _env == [2, 4, 8]
    assert "::warning::" in capsys.readouterr().err


def test_5xx_is_retried(monkeypatch, _env):
    bad = SimpleNamespace(ok=False, text="gateway", status_code=502)
    ok = SimpleNamespace(ok=True, text="", status_code=200)
    calls = _sequence(monkeypatch, [bad, ok])

    assert notify.send_telegram("hi") is True
    assert len(calls) == 2
