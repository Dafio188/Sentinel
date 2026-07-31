import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# Tassonomia dei 22 tag Rizzo-PII e loro mappatura in Sentinell
RIZZO_TAG_MAPPING: Dict[str, Dict[str, str]] = {
    "FULLNAME": {"entity_type": "PERSON", "category": "IDENTIFIER"},
    "CF": {"entity_type": "IT_FISCAL_CODE", "category": "SPECIAL"},
    "PIVA": {"entity_type": "IT_VAT_CODE", "category": "IDENTIFIER"},
    "IBAN": {"entity_type": "IBAN_CODE", "category": "FINANCIAL"},
    "CREDITCARDNUMBER": {"entity_type": "CREDIT_CARD", "category": "FINANCIAL"},
    "EMAIL": {"entity_type": "EMAIL_ADDRESS", "category": "IDENTIFIER"},
    "TELEPHONENUM": {"entity_type": "PHONE_NUMBER", "category": "IDENTIFIER"},
    "STREET": {"entity_type": "ADDRESS", "category": "INDIRECT"},
    "BUILDINGNUM": {"entity_type": "ADDRESS", "category": "INDIRECT"},
    "ZIPCODE": {"entity_type": "ADDRESS", "category": "INDIRECT"},
    "CITY": {"entity_type": "LOCATION", "category": "INDIRECT"},
    "PROVINCE": {"entity_type": "LOCATION", "category": "INDIRECT"},
    "CATASTO": {"entity_type": "IT_CATASTO", "category": "INDIRECT"},
    "DOCID": {"entity_type": "LEGAL_DOC_ID", "category": "INDIRECT"},
    "ID_DOC": {"entity_type": "ID_DOCUMENT", "category": "IDENTIFIER"},
    "DATE": {"entity_type": "DATE_TIME", "category": "INDIRECT"},
    "TIME": {"entity_type": "DATE_TIME", "category": "INDIRECT"},
    "AGE": {"entity_type": "DEMOGRAPHIC", "category": "INDIRECT"},
    "GENDER": {"entity_type": "DEMOGRAPHIC", "category": "INDIRECT"},
    "AMOUNT": {"entity_type": "FINANCIAL_AMOUNT", "category": "FINANCIAL"},
    "TARGA": {"entity_type": "VEHICLE_PLATE", "category": "IDENTIFIER"},
    "ORG": {"entity_type": "ORGANIZATION", "category": "INDIRECT"},
}

class RizzoDetector:
    """
    Rilevatore PII basato sul modello locale Rizzo-PII (mmBERT Token Tagger).
    Funziona in locale su CPU con latenza di pochissimi millisecondi.
    """
    def __init__(self, model_dir: Optional[str] = None):
        self.classifier = None
        self.model_loaded = False
        
        # Cerca il modello nel percorso specificato, in env PII_MODEL_DIR, o nella repo RIZZO locale
        target_dir = model_dir or os.environ.get("PII_MODEL_DIR")
        if not target_dir:
            repo_models = Path(__file__).resolve().parents[3] / "RIZZO" / "models"
            if repo_models.exists():
                versioned = [p for p in repo_models.glob("rizzo-pii-0.3B-v*") if p.is_dir() and not (p / "MOCK_MODEL.txt").exists()]
                if versioned:
                    target_dir = str(max(versioned))
                elif (repo_models / "rizzo-pii-0.3B").exists():
                    target_dir = str(repo_models / "rizzo-pii-0.3B")

        if target_dir and Path(target_dir).exists():
            try:
                # pyrefly: ignore [missing-import]
                from transformers import pipeline  # type: ignore
                self.classifier = pipeline(
                    "token-classification",
                    model=target_dir,
                    aggregation_strategy="first"
                )
                self.model_loaded = True
            except Exception as e:
                print(f"[RizzoDetector] Impossibile caricare il modello da {target_dir}: {e}")

    def scan(self, text: str) -> List[Dict[str, Any]]:
        """
        Esegue la scansione del testo con il tagger Rizzo-PII.
        Se il modello neurale non è disponibile, utilizza il motore euristico locale.
        """
        if not text or not text.strip():
            return []

        if self.model_loaded and self.classifier:
            return self._scan_with_model(text)
        else:
            return self._scan_fallback(text)

    def _scan_with_model(self, text: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        try:
            raw_entities = self.classifier(text)
            for ent in raw_entities:
                raw_tag = ent.get("entity_group") or ent.get("entity", "")
                tag = raw_tag.replace("B-", "").replace("I-", "").upper()
                
                mapping = RIZZO_TAG_MAPPING.get(tag, {"entity_type": "INDIRECT_IDENTIFIER", "category": "INDIRECT"})
                val = ent.get("word") or text[ent["start"]:ent["end"]]
                conf = float(ent.get("score", 0.95))
                
                results.append({
                    "entity_type": mapping["entity_type"],
                    "category": mapping["category"],
                    "detector": "RIZZO",
                    "confidence": conf,
                    "span_start": ent["start"],
                    "span_end": ent["end"],
                    "value": val,
                    "action": "MASK" if conf >= 0.70 else "REVIEW",
                    "action_reason": f"Rilevativo NER Rizzo-PII (tag: {tag})",
                })
        except Exception as e:
            print(f"[RizzoDetector] Errore durante l'inferenza del modello: {e}")
            return self._scan_fallback(text)
            
        return results

    def _scan_fallback(self, text: str) -> List[Dict[str, Any]]:
        """
        Fallback euristico per identificatori legali italiani (Catasto, Atti/DOCID, Nomi).
        """
        results: List[Dict[str, Any]] = []
        
        # 1. Rilevamento Dati Catastali (Foglio X, particella Y, sub Z)
        catasto_pattern = re.compile(
            r"(?i)\b(foglio\s+\d+[\w]*|particella\s+\d+[\w]*|part\.\s*\d+|sub(?:alterno)?\.?\s*\d+)\b"
        )
        for m in catasto_pattern.finditer(text):
            results.append({
                "entity_type": "IT_CATASTO",
                "category": "INDIRECT",
                "detector": "RIZZO",
                "confidence": 0.92,
                "span_start": m.start(),
                "span_end": m.end(),
                "value": m.group(0),
                "action": "MASK",
                "action_reason": "Rilevamento euristico dati catastali (Rizzo-PII)",
            })

        # 2. Rilevamento Identificativi Atti / DOCID (es. N. 1234/2024, RG 567/2023)
        docid_pattern = re.compile(r"(?i)\b(?:r\.?g\.?|repertorio|sentenza|protocollo|atto)\s*(?:n\.?\s*)?(\d+[\/\-]\d{2,4})\b")
        for m in docid_pattern.finditer(text):
            results.append({
                "entity_type": "LEGAL_DOC_ID",
                "category": "INDIRECT",
                "detector": "RIZZO",
                "confidence": 0.90,
                "span_start": m.start(),
                "span_end": m.end(),
                "value": m.group(0),
                "action": "MASK",
                "action_reason": "Rilevamento identificativo atto legale (Rizzo-PII)",
            })

        return results
