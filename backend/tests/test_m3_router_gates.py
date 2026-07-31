import datetime
import sqlite3
import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.core.http_client import EgressBlockedError, GuardedHttpClient
from backend.app.core.security import SESSION_TOKEN
from backend.app.db.engine import get_db_connection, init_db
from backend.app.gate.postflight import PostflightScanner
from backend.app.gate.preflight import PreflightGate
from backend.app.llm.registry import ProviderLockedError, ProviderRegistry
from backend.app.main import app

@pytest.fixture(autouse=True)
def setup_m3_test_db(tmp_path):
    test_db = tmp_path / "aigate_m3_test.db"
    test_vault = tmp_path / "vault_m3_test.db"

    old_db = settings.DATABASE_PATH
    old_vault = settings.VAULT_PATH
    settings.DATABASE_PATH = test_db
    settings.VAULT_PATH = test_vault

    init_db(test_db)

    # Insert test document versions
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO documents (id, filename, original_path, original_sha256, status, created_at)
        VALUES ('doc_test_1', 'test.txt', '/tmp/test.txt', 'sha123', 'PARSED', datetime('now'))
        """
    )
    cursor.execute(
        """
        INSERT INTO document_versions (id, document_id, kind, zone, path, sha256, created_at)
        VALUES ('ver_extracted_1', 'doc_test_1', 'EXTRACTED', 0, '/tmp/test.txt', 'sha123', datetime('now'))
        """
    )
    cursor.execute(
        """
        INSERT INTO document_versions (id, document_id, kind, zone, path, sha256, created_at)
        VALUES ('ver_pseudonymized_1', 'doc_test_1', 'PSEUDONYMIZED', 1, '/tmp/test_pseudonymized.txt', 'sha456', datetime('now'))
        """
    )
    cursor.execute(
        """
        INSERT INTO document_versions (id, document_id, kind, zone, path, sha256, created_at)
        VALUES ('ver_masked_1', 'doc_test_1', 'MASKED', 1, '/tmp/test_masked.txt', 'sha789', datetime('now'))
        """
    )
    conn.commit()
    conn.close()

    yield test_db, test_vault

    settings.DATABASE_PATH = old_db
    settings.VAULT_PATH = old_vault

# 1. test_provider_matrix
def test_provider_matrix():
    gate = PreflightGate()
    prompt = "Riassumi il documento."

    # ollama-local: PASS
    res_ollama = gate.evaluate("ollama-local", prompt, "ver_pseudonymized_1")
    assert res_ollama["gate_result"] == "PASS"

    # openai (EXTERNAL): REVIEW/PASS depending on policy
    res_openai = gate.evaluate("openai", prompt, "ver_pseudonymized_1")
    assert res_openai["gate_result"] in ("PASS", "REVIEW")

    # gemini FREE: BLOCK (UNKNOWN)
    res_gemini = gate.evaluate("gemini", prompt, "ver_pseudonymized_1")
    assert res_gemini["gate_result"] == "BLOCK"

    # deepseek (CN / NONE): BLOCK (CH5)
    res_deepseek = gate.evaluate("deepseek", prompt, "ver_pseudonymized_1")
    assert res_deepseek["gate_result"] == "BLOCK"

# 2. test_deepseek_never_replace
def test_deepseek_never_replace():
    gate = PreflightGate()
    prompt = "Elabora questo testo"
    # PSEUDONYMIZED (REPLACE) to deepseek must always return BLOCK
    res = gate.evaluate("deepseek", prompt, "ver_pseudonymized_1")
    assert res["gate_result"] == "BLOCK"
    assert any("DEEPSEEK_NEVER_REPLACE" in f.get("rule", "") or "GDPR_CH5" in f.get("rule", "") for f in res["findings"])

# 3. test_original_never_external
def test_original_never_external():
    gate = PreflightGate()
    prompt = "Invia versione originale"

    # EXTRACTED / original version to non-LOCAL provider must BLOCK
    res_ext = gate.evaluate("openai", prompt, "ver_extracted_1")
    assert res_ext["gate_result"] == "BLOCK"
    assert any("INVARIANT_I2" in f.get("rule", "") for f in res_ext["findings"])

# 4. test_provider_lock
def test_provider_lock():
    client = TestClient(app)
    headers = {"X-Session-Token": SESSION_TOKEN}

    # Attempting to PATCH deepseek privacy class must yield HTTP 403
    resp = client.patch("/api/providers/deepseek", json={"privacy_class": "LOCAL"}, headers=headers)
    assert resp.status_code == 403

# 5. test_ollama_loopback
def test_ollama_loopback():
    reg = ProviderRegistry()

    # Loopback endpoint -> verified = 1
    assert reg.verify_loopback("ollama-local", "http://127.0.0.1:11434", "LOCAL") == 1

    # Remote non-loopback endpoint -> verified = 0
    assert reg.verify_loopback("ollama-local", "http://192.168.1.100:11434", "LOCAL") == 0

# 6. test_egress_allowlist
def test_egress_allowlist():
    http_client = GuardedHttpClient(allowed_hosts={"api.openai.com"})

    # Host in allowlist -> OK
    assert http_client.check_url("https://api.openai.com/v1/chat") == "api.openai.com"

    # Host not in allowlist -> EgressBlockedError
    with pytest.raises(EgressBlockedError):
        http_client.check_url("https://unauthorized-external-api.com/v1")

# 7. test_postflight_leak
def test_postflight_leak():
    gate = PreflightGate()
    pre_res = gate.evaluate("ollama-local", "Test prompt per leak scan")
    request_id = pre_res["request_id"]

    scanner = PostflightScanner()
    leak_response = "Il risultato per Mario Rossi con CF RSSMRA78T13A662B è approvato."

    res = scanner.scan_response(request_id, leak_response)
    assert res["postflight_result"] == "LEAK_SUSPECT"

# 8. test_prompt_gate_mario_rossi
def test_prompt_gate_mario_rossi():
    gate = PreflightGate()
    prompt = "Analizza il rendimento di Mario Rossi e dimmi se promuoverlo"

    res = gate.evaluate("openai", prompt)
    assert any("PROMPT_GATE_HR_EVALUATION" in f.get("rule", "") for f in res["findings"])
    assert res["gate_result"] in ("REVIEW", "BLOCK")

# 9. test_download_version_auth
def test_download_version_auth(tmp_path):
    client = TestClient(app)
    
    # 1. Unauthenticated download (no token) -> 401
    res_unauth = client.get("/api/versions/ver_extracted_1/download")
    assert res_unauth.status_code == 401
    
    # 2. Query parameter token download -> 200 (or file path handling)
    res_query = client.get(f"/api/versions/ver_extracted_1/download?token={SESSION_TOKEN}")
    assert res_query.status_code in (200, 404)  # 404 if physical temp file absent, but auth 401 passed!
    
    # 3. Header token download -> 200 (or 404 for missing dummy file)
    res_header = client.get(
        "/api/versions/ver_extracted_1/download",
        headers={"X-Session-Token": SESSION_TOKEN}
    )
    assert res_header.status_code in (200, 404)

