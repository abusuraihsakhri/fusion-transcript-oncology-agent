"""Regression coverage for audit cryptography, batch parsing and API access."""
import csv
import math
import os

import pytest
from pydantic import ValidationError

os.environ.setdefault("AUDIT_SECRET_KEY", "test-only-audit-key-for-regression-tests")

from agents.base import AuditTrail
from agents.models import SystemTaskPayload
from cli import _parse_csv_bool, _validate_safe_path, main


def test_audit_integrity_checks_signatures():
    trail = AuditTrail(secret_key="long-test-secret-key-for-tests")
    trail.log("supervisor", "test", "completed", {"task_id": "SYNTH-1"})
    assert trail.verify_integrity()
    snapshot = trail.get_trail()
    snapshot[0]["event_type"] = "forged"
    assert trail.verify_integrity()
    trail.logs[0]["event_type"] = "forged"
    assert not trail.verify_integrity()


def test_audit_integrity_checks_missing_fields():
    trail = AuditTrail(secret_key="long-test-secret-key-for-tests")
    trail.log("supervisor", "test", "completed", {"task_id": "SYNTH-1"})
    del trail.logs[0]["payload_hash"]
    assert not trail.verify_integrity()


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_nonfinite_metrics_rejected(value):
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T", target_identifier="S", primary_metric=value)
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T", target_identifier="S", primary_metric=0, secondary_metric=value)


@pytest.mark.parametrize("value,expected", [
    ("false", False), ("False", False), ("0", False), ("", False),
    ("true", True), ("TRUE", True), ("1", True), ("yes", True),
])
def test_csv_booleans(value, expected):
    assert _parse_csv_bool(value) is expected


def test_invalid_csv_boolean():
    with pytest.raises(ValueError):
        _parse_csv_bool("maybe")


def test_windows_absolute_path_rejected():
    import argparse
    with pytest.raises(argparse.ArgumentTypeError):
        _validate_safe_path("C:/Windows/System32/config/SAM")


def test_batch_false_flag_not_critical(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with open("cases.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "task_id", "target_identifier", "primary_metric",
            "secondary_metric", "is_critical_flag"
        ])
        writer.writeheader()
        writer.writerow(dict(task_id="CASE-1", target_identifier="SYNTH-1",
                             primary_metric=0, secondary_metric=13,
                             is_critical_flag="False"))
    assert main(["batch", "-i", "cases.csv", "-o", "results.csv"]) == 0
    with open("results.csv", newline="", encoding="utf-8") as handle:
        row = next(csv.DictReader(handle))
    assert row["overall_urgency"] == "ELEVATED_RISK"


def test_batch_missing_metrics_rejected(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "cases.csv").write_text("task_id\\nCASE-1\\n", encoding="utf-8")
    assert main(["batch", "-i", "cases.csv", "-o", "results.csv"]) == 1
    assert not (tmp_path / "results.csv").exists()


def test_api_token_and_phi_validation(monkeypatch):
    from fastapi.testclient import TestClient
    from agents.api import app
    client = TestClient(app)
    payload = {"task_id": "DEMO-1", "target_identifier": "SYNTH-2", "primary_metric": 3.0}
    monkeypatch.delenv("API_ACCESS_TOKEN", raising=False)
    assert client.post("/api/audit", json=payload).status_code == 503
    monkeypatch.setenv("API_ACCESS_TOKEN", "test-only-bearer-secret")
    assert client.post("/api/audit", json=payload).status_code == 401
    headers = {"X-API-Key": "test-only-bearer-secret"}
    assert client.post("/api/audit", json=payload, headers=headers).status_code == 200
    payload["target_identifier"] = "MRN-123456"
    assert client.post("/api/audit", json=payload, headers=headers).status_code == 422
    data = client.get("/api/audit/logs", headers=headers).json()
    assert data["verified"] is True
