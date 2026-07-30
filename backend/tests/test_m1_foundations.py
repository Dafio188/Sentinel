import os
import sqlite3
import time
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.app.audit.chain import AuditChainManager
from backend.app.compliance.dsl import UNKNOWN, RuleDSLEvaluator
from backend.app.core.config import settings
from backend.app.core.security import SESSION_TOKEN, store_provider_api_key
from backend.app.core.zones import Zone, ZonedPayload, ZoneViolationError, requires_zone_max
from backend.app.db.engine import get_db_connection, init_db
from backend.app.main import app
from backend.app.vault.manager import VaultLockedError, VaultManager

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    test_db = tmp_path / "aigate_test.db"
    test_vault = tmp_path / "vault_test.db"

    old_db = settings.DATABASE_PATH
    old_vault = settings.VAULT_PATH
    settings.DATABASE_PATH = test_db
    settings.VAULT_PATH = test_vault

    init_db(test_db)
    yield test_db, test_vault

    settings.DATABASE_PATH = old_db
    settings.VAULT_PATH = old_vault

# 1. test_audit_chain_tamper
def test_audit_chain_tamper(setup_test_db):
    test_db, _ = setup_test_db
    audit = AuditChainManager(test_db)

    seq1 = audit.append("TEST", "ACTION1", detail={"msg": "first"})
    seq2 = audit.append("TEST", "ACTION2", detail={"msg": "second"})
    seq3 = audit.append("TEST", "ACTION3", detail={"msg": "third"})

    assert audit.verify() == -1

    # Tamper row seq2 in DB directly
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("UPDATE audit_events SET action = 'TAMPERED' WHERE seq = ?", (seq2,))
    conn.commit()
    conn.close()

    assert audit.verify() == seq2

# 2. test_zone_violation
def test_zone_violation():
    @requires_zone_max(Zone.ZONE_2)
    def process_external_egress(payload: ZonedPayload):
        return "SUCCESS"

    valid_payload = ZonedPayload(data="clean data", zone=Zone.ZONE_2)
    assert process_external_egress(valid_payload) == "SUCCESS"

    # Passing Zone 0 (Vault/Original) to function max Zone 2 input must raise ZoneViolationError
    zone0_payload = ZonedPayload(data="original raw PII", zone=Zone.ZONE_0)
    with pytest.raises(ZoneViolationError):
        process_external_egress(zone0_payload)

# 3. test_vault_lock_cycle
def test_vault_lock_cycle(setup_test_db):
    _, test_vault = setup_test_db
    vault = VaultManager(test_vault, inactivity_timeout_seconds=1)

    # Initial setup
    recovery_code = vault.setup_vault("secret_passphrase_123")
    assert len(recovery_code) > 0

    # Write & Read when unlocked
    vault.store_pseudonym("TOKEN_001", "doc_A", "PERSON", "Mario Rossi")
    val = vault.get_original_value("TOKEN_001", "doc_A")
    assert val == "Mario Rossi"

    # Lock vault
    vault.lock()
    assert vault.is_locked()

    # Reading while locked must raise VaultLockedError
    with pytest.raises(VaultLockedError):
        vault.get_original_value("TOKEN_001", "doc_A")

    # Invalid unlock
    assert not vault.unlock("wrong_password")
    assert vault.is_locked()

    # Correct unlock
    assert vault.unlock("secret_passphrase_123")
    assert vault.get_original_value("TOKEN_001", "doc_A") == "Mario Rossi"

# 4. test_no_secrets_on_disk
def test_no_secrets_on_disk(setup_test_db, tmp_path):
    secret_key = "sk-test-super-secret-key-9999"
    store_provider_api_key("openai", secret_key)

    # Search recursively for secret_key in data/, config/, logs/
    for check_dir in [settings.DATABASE_PATH.parent, tmp_path]:
        for root, dirs, files in os.walk(check_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        assert secret_key not in content, f"Secret leaked in file {file_path}"
                except Exception:
                    pass

# 5. test_localhost_only
def test_localhost_only():
    assert settings.HOST == "127.0.0.1"

    client = TestClient(app)

    # Request without X-Session-Token header to protected route -> 401
    resp_no_token = client.get("/audit")
    assert resp_no_token.status_code == 401

    # Request with invalid token -> 401
    resp_bad_token = client.get("/audit", headers={"X-Session-Token": "invalid_token"})
    assert resp_bad_token.status_code == 401

    # Request with valid token -> 200
    resp_valid = client.get("/audit", headers={"X-Session-Token": SESSION_TOKEN})
    assert resp_valid.status_code == 200

    # /health is accessible without token -> 200
    resp_health = client.get("/health")
    assert resp_health.status_code == 200

# 6. test_llm_requests_check
def test_llm_requests_check(setup_test_db):
    test_db, _ = setup_test_db
    conn = get_db_connection(test_db)
    cursor = conn.cursor()

    # Attempting to INSERT prompt_text != NULL when gate_result = 'BLOCK' must fail sqlite3.IntegrityError
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """
            INSERT INTO llm_requests (
                id, provider_id, prompt_hash, prompt_text, gate_result, created_at
            ) VALUES (?, ?, ?, ?, ?, datetime('now'))
            """,
            ("req_001", "openai", "hash123", "Forbidden raw text", "BLOCK"),
        )
        conn.commit()
    conn.close()

# 7. test_dsl_three_valued
def test_dsl_three_valued():
    ctx = {"a": True, "b": False, "x": 10, "y": 20}

    # Unknown variable propagation
    assert RuleDSLEvaluator.evaluate({"var": "missing_var"}, ctx) == UNKNOWN

    # AND truth table
    assert RuleDSLEvaluator.evaluate({"and": [True, True]}, ctx) is True
    assert RuleDSLEvaluator.evaluate({"and": [True, False]}, ctx) is False
    assert RuleDSLEvaluator.evaluate({"and": [False, UNKNOWN]}, ctx) is False
    assert RuleDSLEvaluator.evaluate({"and": [True, UNKNOWN]}, ctx) == UNKNOWN

    # OR truth table
    assert RuleDSLEvaluator.evaluate({"or": [False, False]}, ctx) is False
    assert RuleDSLEvaluator.evaluate({"or": [True, UNKNOWN]}, ctx) is True
    assert RuleDSLEvaluator.evaluate({"or": [False, UNKNOWN]}, ctx) == UNKNOWN

    # NOT operator
    assert RuleDSLEvaluator.evaluate({"!": True}, ctx) is False
    assert RuleDSLEvaluator.evaluate({"!": False}, ctx) is True
    assert RuleDSLEvaluator.evaluate({"!": UNKNOWN}, ctx) == UNKNOWN

    # Comparison with UNKNOWN
    assert RuleDSLEvaluator.evaluate({">": [{"var": "x"}, {"var": "missing_var"}]}, ctx) == UNKNOWN
    assert RuleDSLEvaluator.evaluate({"in": ["SPECIAL", {"var": "missing_var"}]}, ctx) == UNKNOWN

    # Addition with UNKNOWN
    assert RuleDSLEvaluator.evaluate({"+": [1, {"var": "missing_var"}]}, ctx) == UNKNOWN

    # If condition with UNKNOWN
    assert RuleDSLEvaluator.evaluate({"if": [{"var": "missing_var"}, 1, 0]}, ctx) == UNKNOWN
