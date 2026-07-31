import re
from typing import Any, Dict, List, Optional

class ProjectFeatureExtractor:
    """
    Estrattore intelligente di parametri di compliance (AI Act & GDPR)
    dalla descrizione testuale (Nome e Finalità Intesa) inserita dall'utente.
    """
    @classmethod
    def extract_features(cls, name: str, intended_purpose: str) -> Dict[str, Any]:
        text = f"{name or ''} {intended_purpose or ''}".lower()
        features: Dict[str, Any] = {}

        # 1. Rilevamento sistema AI
        ai_keywords = [
            "ai", "ia", "gemini", "openai", "gpt", "claude", "llm", "machine learning",
            "algoritmo", "modello", "deep learning", "vision", "chatbot", "prompt"
        ]
        if any(kw in text for kw in ai_keywords):
            features["is_ai_system"] = "YES"

        # 2. Rilevamento Ruolo Operativo
        if any(kw in text for kw in ["utilizzando", "api", "usando", "gemini", "openai", "gpt", "claude"]):
            features["role"] = "DEPLOYER"
        elif any(kw in text for kw in ["sviluppo", "addestramento", "training", "custom model"]):
            features["role"] = "PROVIDER"

        # 3. Rilevamento Dominio Operativo
        if any(kw in text for kw in ["cv", "curriculum", "candidati", "lavoro", "dipendenti", "personale", "assunzione", "hr", "recruitment", "esperienza"]):
            features["domain"] = "employment"
        elif any(kw in text for kw in ["facciale", "voce", "biometrico", "emozioni"]):
            features["domain"] = "biometrics"
        elif any(kw in text for kw in ["studenti", "esami", "scuola", "università", "formazione"]):
            features["domain"] = "education"
        elif any(kw in text for kw in ["energia", "trasporti", "rete elettrica", "acqua"]):
            features["domain"] = "critical_infrastructure"
        elif any(kw in text for kw in ["chatbot", "assistenza clienti", "supporto", "faq"]):
            features["domain"] = "general_public"

        # 4. Rilevamento Finalità Specifica
        if any(kw in text for kw in ["trovare candidati", "assunzione", "filtro cv", "recruiting", "selezione"]):
            features["purpose"] = "recruitment"
        elif any(kw in text for kw in ["valutazione", "punteggio", "merito", "prestazioni", "ranking"]):
            features["purpose"] = "evaluation"
        elif any(kw in text for kw in ["promozione", "carriera", "avanzamento"]):
            features["purpose"] = "promotion"
        elif any(kw in text for kw in ["licenziamento", "cessazione"]):
            features["purpose"] = "termination"
        elif any(kw in text for kw in ["monitoraggio", "controllo"]):
            features["purpose"] = "monitoring"

        # 5. Rilevamento Categorie Dati Elaborati
        data_types: List[str] = []
        if any(kw in text for kw in ["cv", "curriculum", "nome", "email", "telefono", "candidati", "identificativi"]):
            data_types.append("IDENTIFIER")
        if any(kw in text for kw in ["età", "eta", "sesso", "genere", "salute", "disabilità", "opinioni", "sensibili"]):
            data_types.append("SPECIAL")
        if any(kw in text for kw in ["fatturato", "retribuzione", "stipendio", "iban", "bancari", "prezzo"]):
            data_types.append("FINANCIAL")
        if any(kw in text for kw in ["titolo di studio", "esperienza", "ruolo", "competenze"]):
            data_types.append("INDIRECT")

        if data_types:
            features["data_types"] = data_types

        # 6. Rilevamento Output Type
        if any(kw in text for kw in ["testo", "report", "valutazione", "sintesi", "classifica"]):
            features["output_type"] = "TEXT"

        return features
