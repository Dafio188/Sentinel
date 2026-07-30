import os
import zipfile
import xml.etree.ElementTree as ET
import pytest
from backend.app.privacy.analyzer import AnalyzerEngine
from backend.app.privacy.anonymizer import AnonymizerEngine
from backend.app.privacy.llm_detector import LLMDetector
from backend.app.privacy.ocr import HybridOcrEngine
from backend.app.privacy.parsers.docx_parser import DocxParser
from backend.app.privacy.parsers.image_parser import ImageParser
from backend.app.privacy.parsers.pdf_parser import PdfParser
from backend.app.privacy.parsers.txt_parser import TextParser
from backend.app.privacy.recognizers import DeterministicDetector, verify_cf_checksum
from backend.app.privacy.validator import ZeroResidueValidator
from backend.app.vault.manager import VaultLockedError, VaultManager

# 1. Recognizers Checksum Tests
def test_cf_checksum_valid_and_invalid():
    # Valid Codice Fiscale: RSSMRA78T13A662B
    valid_cf = "RSSMRA78T13A662B"
    assert verify_cf_checksum(valid_cf) is True

    # Invalid checksum (last char changed from B to Z)
    invalid_cf = "RSSMRA78T13A662Z"
    assert verify_cf_checksum(invalid_cf) is False

    detector = DeterministicDetector()

    # Valid CF in text -> high confidence 0.998
    res_valid = detector.scan(f"Il codice di Mario Rossi è {valid_cf}.")
    assert len(res_valid) > 0
    cf_ent = [e for e in res_valid if e["entity_type"] == "IT_FISCAL_CODE"][0]
    assert cf_ent["confidence"] == 0.998

    # Invalid CF in text -> low confidence 0.6, action REVIEW
    res_invalid = detector.scan(f"Il codice di Rossi è {invalid_cf}.")
    assert len(res_invalid) > 0
    inv_ent = [e for e in res_invalid if e["entity_type"] == "IT_FISCAL_CODE"][0]
    assert inv_ent["confidence"] <= 0.6
    assert inv_ent["action"] == "REVIEW"

# 2. test_validator_zero_residue
def test_validator_zero_residue():
    validator = ZeroResidueValidator()

    # Clean protected text -> Pass True
    clean_text = "Il signor [PERSONA] residente a Milano ha inviato una PEC."
    val_pass, findings = validator.validate(clean_text)
    assert val_pass is True
    assert len(findings) == 0

    # Text containing unmasked valid CF -> Pass False
    dirty_text = "Il signor [PERSONA] con codice RSSMRA78T13A662B ha confermato la richiesta."
    val_pass_dirty, findings_dirty = validator.validate(dirty_text)
    assert val_pass_dirty is False
    assert len(findings_dirty) > 0

# 3. test_metadata_stripped
def test_metadata_stripped(tmp_path):
    # Create fake docx with author metadata
    docx_path = tmp_path / "test_doc.docx"
    with zipfile.ZipFile(docx_path, "w") as z:
        core_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                           xmlns:dc="http://purl.org/dc/elements/1.1/">
            <dc:creator>Giuseppe Verdi</dc:creator>
        </cp:coreProperties>
        """
        doc_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:body><w:p><w:r><w:t>Testo semplice senza PII.</w:t></w:r></w:p></w:body>
        </w:document>
        """
        z.writestr("docProps/core.xml", core_xml)
        z.writestr("word/document.xml", doc_xml)

    parser = DocxParser()
    parsed = parser.parse(str(docx_path))
    assert len(parsed.metadata) > 0
    meta_author = [m for m in parsed.metadata if m["entity_type"] == "METADATA_AUTHOR"][0]
    assert meta_author["value"] == "Giuseppe Verdi"

    analyzer = AnalyzerEngine()
    entities = analyzer.analyze(parsed)
    meta_ents = [e for e in entities if e["detector"] == "METADATA"]
    assert len(meta_ents) > 0

    anonymizer = AnonymizerEngine()
    protected_text, kind, diff_list = anonymizer.anonymize(parsed.text, entities, "MASK", "doc_101", vault_unlocked=True)
    # Metadata is marked REMOVE/stripped and not present in protected text
    assert "Giuseppe Verdi" not in protected_text

# 4. test_replace_requires_vault
def test_replace_requires_vault(tmp_path):
    vault_path = tmp_path / "vault.db"
    vault = VaultManager(vault_path)
    vault.setup_vault("passphrase_123")
    vault.lock()  # Lock vault

    anonymizer = AnonymizerEngine(vault)
    entities = [{"entity_type": "PERSON", "value": "Mario Rossi", "span_start": 0, "span_end": 11}]

    # REPLACE with locked vault must raise VaultLockedError
    with pytest.raises(VaultLockedError):
        anonymizer.anonymize("Mario Rossi", entities, "REPLACE", "doc_001", vault_unlocked=False)

# 5. test_llm_quote_realignment
def test_llm_quote_realignment():
    detector = LLMDetector()
    text = "Il dirigente dell'ufficio tecnico è stato assunto nel 1997."

    # Mock response with 1 real quote and 1 hallucinated quote
    mock_llm_output = [
        {"text_quote": "dirigente dell'ufficio tecnico", "entity_type": "ROLE", "confidence": 0.85},
        {"text_quote": "frase mai esistita nel documento", "entity_type": "FAKE", "confidence": 0.99},
    ]

    results = detector.process_pass(text, [], mock_response=mock_llm_output)
    # The hallucinated quote must be discarded
    assert len(results) == 1
    assert results[0]["value"] == "dirigente dell'ufficio tecnico"

# 6. test_ocr_pii_crosscheck
def test_ocr_pii_crosscheck():
    ocr_engine = HybridOcrEngine()

    # Divergence on low confidence Fiscal Code token
    tess_token = "RSSMRA78T13A662B"
    gemma_hallucinated = "RSSMRA78T13A662Z"  # Invalid checksum

    chosen, flag, conf = ocr_engine.cross_check_tokens(tess_token, gemma_hallucinated, confidence=45.0)

    assert chosen == tess_token
    assert flag == "UNCERTAIN_PII"

# 7. Fixture End-to-End Privacy Pipeline Test
def test_privacy_pipeline_end_to_end(tmp_path):
    iban_val = "IT60X0542811101000000123456"
    text = f"Mario Rossi (email: mario.rossi@test.it, pec: mario@pec.it, IBAN: {iban_val}) affetto da diabete con CF RSSMRA78T13A662B."
    
    parsed = TextParser().parse("", content_bytes=text.encode("utf-8"))
    analyzer = AnalyzerEngine()
    raw_entities = analyzer.analyze(parsed)

    from backend.app.privacy.merge import MergeEngine
    entities = MergeEngine().merge(raw_entities)

    assert len(entities) >= 5

    vault_path = tmp_path / "vault_e2e.db"
    vault = VaultManager(vault_path)
    vault.setup_vault("e2e_passphrase")

    anonymizer = AnonymizerEngine(vault)
    protected_text, kind, diff_list = anonymizer.anonymize(text, entities, "MASK", "doc_e2e", vault_unlocked=True)

    validator = ZeroResidueValidator()
    val_pass, residual = validator.validate(protected_text)

    assert val_pass is True, f"Residual findings in protected text: {residual}"
    assert "RSSMRA78T13A662B" not in protected_text
    assert "mario.rossi@test.it" not in protected_text
    assert iban_val not in protected_text
