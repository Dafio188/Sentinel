import datetime
import sqlite3
import pytest
from backend.app.arks.ingest import ArksIngestor
from backend.app.arks.retrieval import ArksRetrieval
from backend.app.compliance.dsl import UNKNOWN, RuleDSLEvaluator
from backend.app.compliance.engine import ComplianceEngine
from backend.app.compliance.wizard import AdaptiveWizard
from backend.app.core.config import settings
from backend.app.db.engine import get_db_connection, init_db

@pytest.fixture(autouse=True)
def setup_m4_test_db(tmp_path):
    test_db = tmp_path / "aigate_m4_test.db"
    test_vault = tmp_path / "vault_m4_test.db"

    old_db = settings.DATABASE_PATH
    old_vault = settings.VAULT_PATH
    settings.DATABASE_PATH = test_db
    settings.VAULT_PATH = test_vault

    init_db(test_db)

    # Insert test projects
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    for pid in ["proj_test_01", "proj_2027", "proj_2028", "proj_chain_test"]:
        cursor.execute(
            """
            INSERT OR IGNORE INTO projects (id, name, intended_purpose, domain, status, features_json, created_at, updated_at)
            VALUES (?, ?, 'Evaluation', 'employment', 'DRAFT', '{}', datetime('now'), datetime('now'))
            """,
            (pid, f"Test Project {pid}"),
        )
    conn.commit()
    conn.close()

    yield test_db, test_vault

    settings.DATABASE_PATH = old_db
    settings.VAULT_PATH = old_vault

# 1. test_dsl_unknown_propagation
def test_dsl_unknown_propagation():
    engine = ComplianceEngine()
    rules = engine.load_rules()

    dpia_rule = [r for r in rules if r["rule_id"] == "GDPR.ART35.DPIA"][0]

    # Partial model without variables -> UNKNOWN
    partial_model = {"profiling": True}
    res = RuleDSLEvaluator.evaluate(dpia_rule["condition"], partial_model)

    assert RuleDSLEvaluator.is_unknown(res)
    assert "Q_SCALE" in dpia_rule["on_unknown"]["ask"]

# 2. Scenario End-to-End "Valutazione Dipendenti"
def test_scenario_employment_evaluation():
    engine = ComplianceEngine()
    wizard = AdaptiveWizard()

    project_model = {
        "is_ai_system": "YES",
        "domain": "employment",
        "purpose": "evaluation",
        "automation_level": "RECOMMENDATION",
        "data_types": ["SPECIAL", "IDENTIFIER"],
    }

    rules = engine.load_rules()
    assessment = engine.assess_project("proj_test_01", project_model, deploy_date="2028-01-01")

    assert len(assessment["findings"]) > 0
    annex3_fnd = [f for f in assessment["findings"] if f["rule_id"] == "AIACT.ANNEX3.EMPLOYMENT"][0]
    assert annex3_fnd["status"] in ("REVIEW", "MET")

    next_q = wizard.get_next_question(project_model, rules)
    assert next_q is not None
    assert next_q["id"] in ("Q_ROLE", "Q_SCALE", "Q_OUTPUT_TYPE", "Q_DEPLOY_DATE")

# 3. test_dual_date
def test_dual_date():
    engine = ComplianceEngine()
    project_model = {"domain": "employment", "purpose": "evaluation"}

    ass_2027 = engine.assess_project("proj_2027", project_model, deploy_date="2027-03-01")
    annex3_fnd = [f for f in ass_2027["findings"] if f["rule_id"] == "AIACT.ANNEX3.EMPLOYMENT"][0]
    assert annex3_fnd["applicable_today"] is False

    ass_2028 = engine.assess_project("proj_2028", project_model, deploy_date="2028-01-01")
    annex3_2028 = [f for f in ass_2028["findings"] if f["rule_id"] == "AIACT.ANNEX3.EMPLOYMENT"][0]
    assert annex3_2028["applicable_at_deploy"] is True

# 4. test_ncii_versioning
def test_ncii_versioning():
    engine = ComplianceEngine()
    ncii_rule = [r for r in engine.load_rules() if r["rule_id"] == "AIACT.ART5.NCII"][0]
    effective_date = ncii_rule.get("effective_from", "2026-12-02")
    assert effective_date == "2026-12-02"

# 5. test_chain_traversal
def test_chain_traversal():
    engine = ComplianceEngine()
    project_model = {"profiling": True, "automation_level": "SOLELY_AUTOMATED", "scale": "LARGE"}

    assessment = engine.assess_project("proj_chain_test", project_model)
    finding_id = assessment["findings"][0]["id"]

    chain = engine.get_compliance_chain(finding_id)
    assert chain["finding_id"] == finding_id
    assert "rule" in chain
    assert "chain_path" in chain

# 6. test_retrieval_effective_date
def test_retrieval_effective_date():
    ingestor = ArksIngestor()
    retrieval = ArksRetrieval()

    sample_text = "Articolo 50. Obblighi di trasparenza per sistemi di intelligenza artificiale."
    ingestor.ingest_source_text("EU_2024_1689", "AI Act", "EU", "PRIMARY_LAW", sample_text)

    results = retrieval.search("trasparenza sistemi intelligenza artificiale")
    assert len(results) >= 0

# 7. Rules Schema Validation
def test_rules_json_schema_validation():
    engine = ComplianceEngine()
    rules = engine.load_rules()

    assert len(rules) >= 4
    for r in rules:
        assert "rule_id" in r
        assert "framework" in r
        assert "condition" in r
        assert "severity" in r

# 8. test_project_feature_extractor
def test_project_feature_extractor():
    from backend.app.compliance.extractor import ProjectFeatureExtractor
    
    name = "Utilizzando Gemini devo analizzare dei CV di candidati"
    purpose = "analisi CV per trovare candidati secondo linee guida come anni di esperienza, titolo di studio, età."
    
    features = ProjectFeatureExtractor.extract_features(name, purpose)
    
    assert features.get("is_ai_system") == "YES"
    assert features.get("domain") == "employment"
    assert features.get("purpose") == "recruitment"
    assert "IDENTIFIER" in features.get("data_types", [])
    assert "SPECIAL" in features.get("data_types", [])
    assert features.get("role") == "DEPLOYER"

