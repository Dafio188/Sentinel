from dataclasses import dataclass
from typing import Optional

@dataclass
class Project:
    id: str
    name: str
    intended_purpose: Optional[str]
    domain: Optional[str]
    status: str
    features_json: Optional[str]
    created_at: str
    updated_at: str

@dataclass
class LLMProvider:
    id: str
    name: str
    endpoint: str
    model: str
    privacy_class: str
    privacy_class_locked: int
    endpoint_verified_local: Optional[int]
    country: Optional[str]
    transfer_mechanism: Optional[str]
    training_policy_tier: Optional[str]
    max_risk_allowed: str
    params_json: Optional[str]

@dataclass
class AuditEventRecord:
    seq: Optional[int]
    ts: str
    component: str
    action: str
    object_type: Optional[str]
    object_id: Optional[str]
    input_hash: Optional[str]
    output_hash: Optional[str]
    rule_id: Optional[str]
    risk: Optional[str]
    detail_json: Optional[str]
    prev_hash: str
    event_hash: str
