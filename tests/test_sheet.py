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


def test_load_credentials_accepts_identical_duplicate_with_missing_opening_brace():
    credentials = {"type": "service_account", "project_id": "example"}
    pretty = json.dumps(credentials, indent=2)
    value = pretty[1:] + "\n" + pretty

    assert _load_credentials(value) == credentials


def test_load_credentials_accepts_duplicate_after_literal_newline_separator():
    credentials = {"type": "service_account", "project_id": "example"}
    compact = json.dumps(credentials)
    value = compact[1:] + "\n\\n" + compact[1:]

    assert _load_credentials(value) == credentials


def test_load_credentials_rejects_conflicting_duplicate_objects():
    first = {"type": "service_account", "project_id": "one"}
    second = {"type": "service_account", "project_id": "two"}
    value = json.dumps(first)[1:] + "\n" + json.dumps(second)

    with pytest.raises(ValueError, match="must be valid JSON"):
        _load_credentials(value)


def test_load_credentials_rejects_non_object_json():
    with pytest.raises(ValueError, match="must contain a JSON object"):
        _load_credentials("[]")


def test_load_credentials_rejects_invalid_json():
    with pytest.raises(ValueError, match="must be valid JSON"):
        _load_credentials("not json")
