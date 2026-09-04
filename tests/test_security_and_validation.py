"""
Security & Input Validation Tests for Fusion Transcript Oncology Agent.
"""
import os
import sys
from pathlib import Path

# Set secure test key before any imports that initialize GLOBAL_AUDIT
os.environ.setdefault("AUDIT_SECRET_KEY", "test-suite-key-security-validation-2026-secure")

sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import pytest
from pydantic import ValidationError
from agents.models import SystemTaskPayload
from cli import _validate_safe_path


class TestInputValidation:
    """Test that SystemTaskPayload enforces field constraints."""

    def test_task_id_max_length_rejected(self):
        with pytest.raises(ValidationError):
            SystemTaskPayload(task_id="X" * 200, target_identifier="T1", primary_metric=10.0)

    def test_target_identifier_max_length_rejected(self):
        with pytest.raises(ValidationError):
            SystemTaskPayload(task_id="T1", target_identifier="X" * 200, primary_metric=10.0)

    def test_status_descriptor_max_length_rejected(self):
        with pytest.raises(ValidationError):
            SystemTaskPayload(task_id="T1", target_identifier="T1", primary_metric=10.0, status_descriptor="X" * 100)

    def test_empty_task_id_rejected(self):
        with pytest.raises(ValidationError):
            SystemTaskPayload(task_id="", target_identifier="T1", primary_metric=10.0)

    def test_valid_payload_accepted(self):
        payload = SystemTaskPayload(task_id="TASK-001", target_identifier="SPEC-01", primary_metric=15.0)
        assert payload.task_id == "TASK-001"
        assert payload.primary_metric == 15.0

    def test_phi_placeholder_rejected_in_task_id(self):
        with pytest.raises(ValidationError, match="disallowed placeholder"):
            SystemTaskPayload(task_id="<patient>-001", target_identifier="T1", primary_metric=10.0)

    def test_phi_placeholder_rejected_in_target(self):
        with pytest.raises(ValidationError, match="disallowed placeholder"):
            SystemTaskPayload(task_id="T1", target_identifier="[name]-target", primary_metric=10.0)


class TestPathTraversalProtection:
    """Test that batch file operations reject path traversal attempts."""

    def test_traversal_input_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError):
            _validate_safe_path("../../../etc/passwd", must_exist=False)

    def test_traversal_output_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError):
            _validate_safe_path("../../sensitive_file.csv", must_exist=False)

    def test_absolute_outside_cwd_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError):
            _validate_safe_path("C:/Windows/System32/config/SAM", must_exist=False)

    def test_valid_relative_path_accepted(self):
        result = _validate_safe_path("sample.csv", must_exist=False)
        assert result is not None

    def test_nonexistent_input_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError):
            _validate_safe_path("nonexistent_file_12345.csv", must_exist=True)


class TestAuditKeySecurity:
    """Test that audit key requirements are enforced."""

    def test_short_key_rejected(self):
        from agents.base import AuditTrail
        with pytest.raises(RuntimeError, match="at least 16 characters"):
            AuditTrail(secret_key="short")

    def test_missing_key_rejected(self):
        from agents.base import AuditTrail
        original = os.environ.pop("AUDIT_SECRET_KEY", None)
        try:
            with pytest.raises(RuntimeError, match="AUDIT_SECRET_KEY"):
                AuditTrail()
        finally:
            if original:
                os.environ["AUDIT_SECRET_KEY"] = original

    def test_valid_key_accepted(self):
        from agents.base import AuditTrail
        trail = AuditTrail(secret_key="this-is-a-valid-key-32-chars-long!!")
        assert len(trail.logs) == 0
