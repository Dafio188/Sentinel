from fastapi import APIRouter
from backend.app.audit.chain import AuditChainManager

router = APIRouter()

@router.get("/health")
def health_check():
    audit_manager = AuditChainManager()
    return {
        "status": "ok",
        "service": "AIGate",
        "binding": "127.0.0.1",
        "audit_chain_valid": audit_manager.verify() == -1,
    }

@router.get("/audit")
def get_audit_verify():
    audit_manager = AuditChainManager()
    tampered_seq = audit_manager.verify()
    return {
        "chain_valid": tampered_seq == -1,
        "first_tampered_seq": tampered_seq if tampered_seq != -1 else None,
        "latest_hash": audit_manager.get_latest_hash(),
    }
