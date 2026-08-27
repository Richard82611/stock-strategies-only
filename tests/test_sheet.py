import json

import pytest

from stock_strategies.sheet import _load_credentials


def test_load_credentials_accepts_service_account_json():
    credentials = {"type": "service_account", "project_id": "example"}

    assert _load_credentials(json.dumps(credentials)) == credentials


def test_load_credentials_accepts_json_without_outer_braces():
    credentials = {"type": "service_account", "project_id": "example"}
    value = json.dumps(credentials)[1:-1]

    assert _load_credentials(value) == credentials


def test_load_credentials_accepts_json_without_opening_brace():
    credentials = {"type": "service_account", "project_id": "example"}
    value = json.dumps(credentials)[1:]

    assert _load_credentials(value) == credentials


def test_load_credentials_accepts_json_without_closing_brace():
    credentials = {"type": "service_account", "project_id": "example"}
    value = json.dumps(credentials)[:-1]

    assert _load_credentials(value) == credentials


def test_load_credentials_accepts_identical_assignment_duplicate():
    credentials = {"type": "service_account", "project_id": "example"}
    compact = json.dumps(credentials)
    value = compact[1:] + "\nGOOGLE_CREDS_JSON=" + compact

    assert _load_credentials(value) == credentials


def test_load_credentials_rejects_conflicting_assignment_duplicate():
    first = json.dumps({"type": "service_account", "project_id": "one"})
    second = json.dumps({"type": "service_account", "project_id": "two"})
    value = first[1:] + "\nGOOGLE_CREDS_JSON=" + second

    with pytest.raises(ValueError, match="conflicting credential objects"):
        _load_credentials(value)


def test_load_credentials_rejects_non_object_json():
    with pytest.raises(ValueError, match="must contain a JSON object"):
        _load_credentials("[]")


def test_load_credentials_rejects_invalid_json():
    with pytest.raises(ValueError, match="must be valid JSON"):
        _load_credentials("not json")
