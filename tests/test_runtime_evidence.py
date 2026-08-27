from types import SimpleNamespace

import pandas as pd
import pytest

from stock_strategies import evaluate as evaluate_module
from stock_strategies import notify


def _price_frame(n: int = 120) -> pd.DataFrame:
    dates = pd.bdate_range("2026-03-16", periods=n)
    close = [100 + i * 0.2 for i in range(n)]
    return pd.DataFrame({
        "date": dates,
        "open": [v - 0.1 for v in close],
        "high": [v + 0.5 for v in close],
        "low": [v - 0.5 for v in close],
        "close": close,
        "volume": [1000 + i for i in range(n)],
    })


def test_evaluate_stamps_latest_market_data_date(monkeypatch):
    prices = _price_frame()
    monkeypatch.setattr(
        evaluate_module,
        "get_fundamental",
        lambda _sid: {"eps": {2023: 8, 2024: 9}, "roe": {2023: 18, 2024: 19}},
    )
    monkeypatch.setattr(evaluate_module, "get_price_history", lambda *_args: prices.copy())

    result = evaluate_module.evaluate("2330", "台積電")

    assert result is not None
    assert result["date"] == prices.iloc[-1]["date"].strftime("%Y-%m-%d")


def test_report_data_date_uses_latest_verified_signal_date():
    signals = [{"date": "2026-08-26"}, {"date": "2026-08-27"}, {"date": ""}]

    assert notify._report_data_date(signals) == "2026-08-27"


def test_send_telegram_failure_is_not_silent(monkeypatch):
    response = SimpleNamespace(ok=False, text="bad request", status_code=400)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")
    monkeypatch.setattr(notify.requests, "post", lambda *_args, **_kwargs: response)

    with pytest.raises(RuntimeError, match="HTTP 400"):
        notify.send_telegram("test")
