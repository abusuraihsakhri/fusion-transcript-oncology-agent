"""
Pytest configuration: sets secure test environment variables before imports.
"""
import os
import secrets

# Set a secure test key for HMAC-SHA256 audit trail before any module imports
os.environ.setdefault("AUDIT_SECRET_KEY", f"test-key-{secrets.token_hex(16)}-secure-audit-trail-2026")
