import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from backend.app.audit.chain import AuditChainManager
from backend.app.core.config import settings
from backend.app.db.engine import get_db_connection
from backend.app.gate.postflight import PostflightScanner
from backend.app.gate.preflight import PreflightGate
from backend.app.llm.connectors.external import ExternalLLMConnector
from backend.app.llm.connectors.ollama import OllamaConnector
from backend.app.llm.registry import ProviderLockedError, ProviderRegistry
from backend.app.privacy.analyzer import AnalyzerEngine
from backend.app.privacy.anonymizer import AnonymizerEngine
from backend.app.privacy.parsers import ParserRegistry
from backend.app.privacy.parsers.docx_parser import DocxParser
from backend.app.privacy.parsers.txt_parser import TextParser
from backend.app.privacy.scores import calculate_privacy_scores
from backend.app.privacy.validator import ZeroResidueValidator
from backend.app.vault.manager import VaultManager

router = APIRouter()
audit_manager = AuditChainManager()
analyzer = AnalyzerEngine()
validator = ZeroResidueValidator()
registry = ProviderRegistry()
preflight_gate = PreflightGate()
postflight_scanner = PostflightScanner()

class ProtectRequest(BaseModel):
    strategy: str = "BALANCED"
    policy_id: Optional[str] = None
    overrides: Optional[List[Dict[str, Any]]] = None
    vault_passphrase: Optional[str] = None

class PreflightRequestModel(BaseModel):
    provider_id: str
    prompt_text: str
    document_version_id: Optional[str] = None
    policy_name: str = "BALANCED"

class ChatRequestModel(BaseModel):
    provider_id: str
    prompt_text: str
    document_version_id: Optional[str] = None
    policy_name: str = "BALANCED"

class UpdateProviderModel(BaseModel):
    privacy_class: str

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "AIGate",
        "binding": "127.0.0.1",
        "audit_chain_valid": audit_manager.verify() == -1,
    }

@router.get("/audit")
def get_audit_verify():
    tampered_seq = audit_manager.verify()
    return {
        "chain_valid": tampered_seq == -1,
        "first_tampered_seq": tampered_seq if tampered_seq != -1 else None,
        "latest_hash": audit_manager.get_latest_hash(),
    }

# --- Provider Registry Endpoints ---
@router.get("/providers")
def list_providers():
    return {"providers": registry.get_providers()}

@router.patch("/providers/{id}")
def update_provider(id: str, body: UpdateProviderModel):
    try:
        updated = registry.update_provider_privacy_class(id, body.privacy_class)
        return updated
    except ProviderLockedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Gate & Chat Endpoints ---
@router.post("/gate/preflight")
def preflight_check(req: PreflightRequestModel):
    try:
        res = preflight_gate.evaluate(req.provider_id, req.prompt_text, req.document_version_id, req.policy_name)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/chat")
async def chat_orchestrate(req: ChatRequestModel):
    # 1. Preflight Evaluation
    pre_res = preflight_gate.evaluate(req.provider_id, req.prompt_text, req.document_version_id, req.policy_name)
    if pre_res["gate_result"] == "BLOCK":
        raise HTTPException(
            status_code=403,
            detail={"message": "Richiesta bloccata dal Privacy Gate", "findings": pre_res["findings"]},
        )

    # 2. Invoke Connector
    provider = registry.get_provider(req.provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    if provider["privacy_class"] == "LOCAL":
        connector = OllamaConnector(endpoint=provider["endpoint"], model=provider["model"])
    else:
        connector = ExternalLLMConnector(provider_id=req.provider_id, endpoint=provider["endpoint"], model=provider["model"])

    raw_response = await connector.generate_chat(req.prompt_text)
    resp_text = raw_response.get("text", "")

    # 3. Post-flight Response Scanning
    post_res = postflight_scanner.scan_response(pre_res["request_id"], resp_text)

    return {
        "request_id": pre_res["request_id"],
        "gate_result": pre_res["gate_result"],
        "postflight_result": post_res["postflight_result"],
        "reid_warning": post_res["reid_warning"],
        "response_text": post_res["response_text"],
    }

@router.get("/requests/{id}")
def get_request_info(id: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM llm_requests WHERE id = ?", (id,))
        req = cursor.fetchone()
        if not req:
            raise HTTPException(status_code=404, detail="LLM request not found")
        
        cursor.execute("SELECT * FROM llm_responses WHERE request_id = ?", (id,))
        resp = cursor.fetchone()
        return {
            "request": dict(req),
            "response": dict(resp) if resp else None,
        }
    finally:
        conn.close()

# --- Privacy Engine Endpoints ---
@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    language: Optional[str] = Form("ita"),
):
    content = await file.read()
    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
    sha256 = hashlib.sha256(content).hexdigest()

    orig_dir = settings.DATABASE_PATH.parent.parent / "documents" / "original"
    os.makedirs(orig_dir, exist_ok=True)
    file_path = orig_dir / f"{doc_id}_{file.filename}"
    file_path.write_bytes(content)

    parser = ParserRegistry.get_parser(file.content_type or "") or TextParser()
    if file.filename.endswith(".docx"):
        parser = DocxParser()

    parsed = parser.parse(str(file_path), content_bytes=content)

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO documents (id, project_id, filename, mime_type, original_path, original_sha256, language, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc_id,
                project_id,
                file.filename,
                file.content_type,
                str(file_path),
                sha256,
                language,
                "PARSED",
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        version_id = f"ver_{uuid.uuid4().hex[:12]}"
        cursor.execute(
            """
            INSERT INTO document_versions (id, document_id, kind, zone, path, sha256, created_at)
            VALUES (?, ?, 'EXTRACTED', 0, ?, ?, ?)
            """,
            (version_id, doc_id, str(file_path), sha256, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()

    audit_manager.append("PRIVACY_ENGINE", "INGEST_DOCUMENT", "DOCUMENT", doc_id, input_hash=sha256)

    return {
        "document_id": doc_id,
        "filename": file.filename,
        "extracted_text_length": len(parsed.text),
        "metadata_count": len(parsed.metadata),
    }

@router.post("/documents/{id}/scan")
def scan_document(id: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (id,))
        doc = cursor.fetchone()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        cursor.execute("SELECT id FROM document_versions WHERE document_id = ? AND kind = 'EXTRACTED'", (id,))
        v_row = cursor.fetchone()
        if not v_row:
            raise HTTPException(status_code=400, detail="Document extracted version missing")

        version_id = v_row["id"]
        file_path = doc["original_path"]

        parser = DocxParser() if doc["filename"].endswith(".docx") else TextParser()
        parsed = parser.parse(file_path)

        detected = analyzer.analyze(parsed)

        for ent in detected:
            ent_id = f"ent_{uuid.uuid4().hex[:12]}"
            cursor.execute(
                """
                INSERT INTO detected_entities (
                    id, document_version_id, entity_type, category, detector, confidence,
                    span_start, span_end, value_hash, action, action_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ent_id,
                    version_id,
                    ent["entity_type"],
                    ent["category"],
                    ent["detector"],
                    ent["confidence"],
                    ent.get("span_start"),
                    ent.get("span_end"),
                    ent["value_hash"],
                    ent.get("action"),
                    ent.get("action_reason"),
                ),
            )
        conn.commit()
    finally:
        conn.close()

    audit_manager.append("PRIVACY_ENGINE", "SCAN_DOCUMENT", "DOCUMENT", id, detail={"detected_count": len(detected)})

    return {"document_id": id, "detected_entities_count": len(detected), "entities": detected}

@router.post("/documents/{id}/protect")
def protect_document(id: str, req: ProtectRequest):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (id,))
        doc = cursor.fetchone()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        parser = DocxParser() if doc["filename"].endswith(".docx") else TextParser()
        parsed = parser.parse(doc["original_path"])
        entities = analyzer.analyze(parsed)

        vault_mgr = VaultManager(settings.VAULT_PATH)
        vault_unlocked = False
        if req.vault_passphrase:
            vault_unlocked = vault_mgr.unlock(req.vault_passphrase)

        anonymizer = AnonymizerEngine(vault_mgr)
        protected_text, kind, diff_list = anonymizer.anonymize(
            parsed.text, entities, req.strategy, id, vault_unlocked=vault_unlocked
        )

        val_pass, residual = validator.validate(protected_text)

        prot_dir = settings.DATABASE_PATH.parent.parent / "documents" / "protected"
        os.makedirs(prot_dir, exist_ok=True)
        result_ver_id = f"ver_{uuid.uuid4().hex[:12]}"
        prot_path = prot_dir / f"{result_ver_id}_protected.txt"
        prot_path.write_text(protected_text, encoding="utf-8")
        prot_sha256 = hashlib.sha256(protected_text.encode("utf-8")).hexdigest()

        priv_score, util_score, reid_risk, snapshot_json = calculate_privacy_scores(entities, diff_list, req.strategy)

        cursor.execute(
            """
            INSERT INTO document_versions (
                id, document_id, kind, zone, path, sha256, policy_id,
                privacy_snapshot_json, utility_score, privacy_score, reid_risk, created_at
            ) VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result_ver_id,
                id,
                kind,
                str(prot_path),
                prot_sha256,
                req.policy_id,
                snapshot_json,
                util_score,
                priv_score,
                reid_risk,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        event_id = f"anon_{uuid.uuid4().hex[:12]}"
        cursor.execute(
            """
            INSERT INTO anonymization_events (
                id, source_version_id, result_version_id, strategy,
                entities_processed, entities_blocked, diff_json, validator_pass, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                id,
                result_ver_id,
                req.strategy,
                len(entities),
                0,
                json.dumps(diff_list),
                1 if val_pass else 0,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
    finally:
        conn.close()

    audit_manager.append(
        "PRIVACY_ENGINE", "PROTECT_DOCUMENT", "DOCUMENT_VERSION", result_ver_id, output_hash=prot_sha256
    )

    return {
        "result_version_id": result_ver_id,
        "kind": kind,
        "validator_pass": val_pass,
        "privacy_score": priv_score,
        "utility_score": util_score,
        "reid_risk": reid_risk,
        "diff_count": len(diff_list),
    }

@router.get("/documents/{id}/versions")
def get_document_versions(id: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM document_versions WHERE document_id = ?", (id,))
        rows = [dict(r) for r in cursor.fetchall()]
        return {"document_id": id, "versions": rows}
    finally:
        conn.close()

@router.get("/versions/{id}/diff")
def get_version_diff(id: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM anonymization_events WHERE result_version_id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Anonymization event not found for this version")
        diff_list = json.loads(row["diff_json"]) if row["diff_json"] else []
        return {"version_id": id, "diff": diff_list, "validator_pass": row["validator_pass"]}
    finally:
        conn.close()
