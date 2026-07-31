import pytest
from backend.app.privacy.analyzer import AnalyzerEngine
from backend.app.privacy.merge import MergeEngine
from backend.app.privacy.parsers.base import ParsedDocument
from backend.app.privacy.rizzo_detector import RizzoDetector


def test_rizzo_detector_catasto_and_docid():
    detector = RizzoDetector()
    text = "Immobile sito in Milano, censito al Foglio 12, particella 345, sub. 6. Riferimento Atto N. 1234/2024."
    
    results = detector.scan(text)
    assert len(results) >= 2
    
    catasto_ents = [e for e in results if e["entity_type"] == "IT_CATASTO"]
    assert len(catasto_ents) > 0
    assert catasto_ents[0]["detector"] == "RIZZO"
    assert catasto_ents[0]["action"] == "MASK"

    docid_ents = [e for e in results if e["entity_type"] == "LEGAL_DOC_ID"]
    assert len(docid_ents) > 0
    assert docid_ents[0]["detector"] == "RIZZO"


def test_analyzer_and_merge_with_rizzo():
    analyzer = AnalyzerEngine()
    merger = MergeEngine()
    
    sample_text = (
        "Il Sig. Mario Rossi, Codice Fiscale RSSMRA78T13A662B, "
        "è proprietario dell'immobile al Foglio 45, part. 120. "
        "Contatto PEC: m.rossi@pec.it - Telefono +39 333 1234567."
    )
    
    parsed_doc = ParsedDocument(
        text=sample_text,
        metadata=[{"field": "author", "value": "Studio Legale Rossi", "category": "IDENTIFIER", "entity_type": "ORGANIZATION"}]
    )
    
    raw_entities = analyzer.analyze(parsed_doc)
    assert len(raw_entities) > 0
    
    # Check that both Deterministic and Rizzo detectors contributed
    detectors = {e["detector"] for e in raw_entities}
    assert "REGEX" in detectors
    assert "RIZZO" in detectors
    assert "METADATA" in detectors
    
    merged = merger.merge(raw_entities)
    assert len(merged) > 0
    
    # Valid Codice Fiscale should win via REGEX (SPECIAL category / high confidence)
    cf_ent = [e for e in merged if e["entity_type"] == "IT_FISCAL_CODE"][0]
    assert cf_ent["value"] == "RSSMRA78T13A662B"
    assert cf_ent["confidence"] >= 0.99
    
    # Catasto entity detected by Rizzo should be present
    catasto_ent = [e for e in merged if e["entity_type"] == "IT_CATASTO"][0]
    assert "Foglio 45" in catasto_ent["value"] or "part. 120" in catasto_ent["value"]
