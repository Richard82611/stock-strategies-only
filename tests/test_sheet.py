import json

import pytest

from stock_strategies.sheet import _load_credentials


def test_load_credentials_accepts_service_account_json():
    credentials = {"type": "service_account", "project_id": "example"}

    assert _load_credentials(json.dumps(credentials)) == credentials


def test_load_credentials_accepts_json_without_outer_braces():
    credentials = {"type": "service_account", "project_id": "example"}

    assert _load_credentials('"type":"service_account","project_id":"example"') == credentials


def test_load_credentials_rejects_non_object_json():
    with pytest.raises(ValueError, match="must contain a JSON object"):
        _load_credentials("[]")
