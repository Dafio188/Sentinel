import re
from typing import Any, Dict, List, Tuple

# Helper checksum for Codice Fiscale Italiano
ODD_MAP = {
    '0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17, '8': 19, '9': 21,
    'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13, 'G': 15, 'H': 17, 'I': 19, 'J': 21,
    'K': 2, 'L': 4, 'M': 18, 'N': 20, 'O': 11, 'P': 3, 'Q': 6, 'R': 8, 'S': 12, 'T': 14,
    'U': 16, 'V': 10, 'W': 22, 'X': 25, 'Y': 24, 'Z': 23
}

EVEN_MAP = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9,
    'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19,
    'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25
}

def verify_cf_checksum(cf: str) -> bool:
    cf = cf.upper().replace(" ", "")
    if len(cf) != 16:
        return False
    
    total = 0
    for i in range(15):
        char = cf[i]
        if (i + 1) % 2 != 0:  # Odd position (1-indexed)
            total += ODD_MAP.get(char, 0)
        else:
            total += EVEN_MAP.get(char, 0)
            
    expected_char = chr(65 + (total % 26))
    return cf[15] == expected_char

def verify_luhn_vat(vat: str) -> bool:
    vat = vat.strip()
    if not vat.isdigit() or len(vat) != 11:
        return False
    s_even = sum(int(vat[i]) for i in range(0, 9, 2))
    s_odd = sum(2 * int(vat[i]) - (9 if 2 * int(vat[i]) > 9 else 0) for i in range(1, 10, 2))
    check = (10 - ((s_even + s_odd) % 10)) % 10
    return int(vat[10]) == check

def verify_iban(iban: str) -> bool:
    iban = iban.replace(" ", "").upper()
    if not iban.startswith("IT") or len(iban) != 27:
        return False
    rearranged = iban[4:] + iban[:4]
    digits = ""
    for char in rearranged:
        if char.isdigit():
            digits += char
        else:
            digits += str(ord(char) - 55)
    return int(digits) % 97 == 1

# Italian Dictionaries
FIRST_NAMES = {"mario", "giuseppe", "giovanni", "luigi", "francesco", "angelo", "antonio", "rosa", "maria", "anna", "franca"}
LAST_NAMES = {"rossi", "russo", "ferrari", "esposito", "bianchi", "romano", "colombo", "ricci", "marino", "greco"}
TITLE_WORDS = {"dott.", "dottor", "ing.", "ingegnere", "avv.", "avvocato", "prof.", "professore", "sig.", "signore", "sig.ra"}

SPECIAL_KEYWORDS = {
    "HEALTH": ["patologia", "diagnosi", "cartella clinica", "terapia", "tumore", "hiv", "diabete", "ricovero", "malattia"],
    "RELIGIOUS": ["cattolico", "musulmano", "ebreo", "battesimo", "parrocchia", "fede religiosa"],
    "POLITICAL": ["partito", "sindacato", "elettore", "tessera politica", "votazione"],
    "TRADE_UNION": ["sciopero", "iscrizione CGIL", "iscrizione CISL", "iscrizione UIL"],
    "SEX_LIFE": ["orientamento sessuale", "vita sessuale"],
}

class DeterministicDetector:
    def scan(self, text: str) -> List[Dict[str, Any]]:
        entities: List[Dict[str, Any]] = []

        # 1. Codice Fiscale (handling spaces e.g. "RSS MRA 78T13 A662K")
        cf_pattern = re.compile(r'\b[A-Z]{3}\s?[A-Z]{3}\s?\d{2}[A-Z]\d{2}\s?[A-Z]\d{3}\s?[A-Z]\b', re.IGNORECASE)
        for match in cf_pattern.finditer(text):
            val = match.group(0)
            norm_val = val.replace(" ", "").upper()
            is_valid = verify_cf_checksum(norm_val)
            conf = 0.998 if is_valid else 0.6
            entities.append({
                "entity_type": "IT_FISCAL_CODE",
                "category": "IDENTIFIER",
                "detector": "REGEX",
                "confidence": conf,
                "span_start": match.start(),
                "span_end": match.end(),
                "value": val,
                "action": "MASK" if conf >= 0.7 else "REVIEW",
                "action_reason": "Codice Fiscale italiano validato con checksum" if is_valid else "Formato Codice Fiscale con checksum invalido",
            })

        # 2. Partita IVA
        vat_pattern = re.compile(r'\bIT\d{11}\b|\b\d{11}\b', re.IGNORECASE)
        for match in vat_pattern.finditer(text):
            val = match.group(0).upper().replace("IT", "")
            if verify_luhn_vat(val):
                entities.append({
                    "entity_type": "IT_VAT",
                    "category": "IDENTIFIER",
                    "detector": "REGEX",
                    "confidence": 0.99,
                    "span_start": match.start(),
                    "span_end": match.end(),
                    "value": match.group(0),
                    "action": "MASK",
                    "action_reason": "Partita IVA italiana valida",
                })

        # 3. IBAN
        iban_pattern = re.compile(r'\bIT\d{2}[A-Z]\d{10}[0-9A-Z]{12}\b', re.IGNORECASE)
        for match in iban_pattern.finditer(text):
            val = match.group(0)
            is_valid = verify_iban(val)
            if is_valid:
                entities.append({
                    "entity_type": "IT_IBAN",
                    "category": "IDENTIFIER",
                    "detector": "REGEX",
                    "confidence": 0.995,
                    "span_start": match.start(),
                    "span_end": match.end(),
                    "value": val,
                    "action": "MASK",
                    "action_reason": "IBAN italiano valido",
                })

        # 4. PEC / Email
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
        pec_domains = ["pec.it", "legalmail.it", "arubapec.it", "postecert.it"]
        for match in email_pattern.finditer(text):
            val = match.group(0)
            is_pec = any(val.lower().endswith(d) or "pec" in val.lower() for d in pec_domains)
            entities.append({
                "entity_type": "IT_PEC" if is_pec else "EMAIL",
                "category": "IDENTIFIER",
                "detector": "REGEX",
                "confidence": 0.99 if is_pec else 0.95,
                "span_start": match.start(),
                "span_end": match.end(),
                "value": val,
                "action": "MASK",
                "action_reason": "Email/PEC rilevata",
            })

        # 5. Telefonici Italiani
        phone_pattern = re.compile(r'(\+39\s?)?\(?3\d{2}\)?[\s.-]?\d{6,7}\b|\b0\d{1,4}[\s.-]?\d{5,8}\b')
        for match in phone_pattern.finditer(text):
            val = match.group(0)
            entities.append({
                "entity_type": "IT_PHONE",
                "category": "IDENTIFIER",
                "detector": "REGEX",
                "confidence": 0.95,
                "span_start": match.start(),
                "span_end": match.end(),
                "value": val,
                "action": "MASK",
                "action_reason": "Numero di telefono italiano",
            })

        # 6. Targhe Italiane
        plate_pattern = re.compile(r'\b[A-HK-PR-YZ]{2}\d{3}[A-HK-PR-YZ]{2}\b', re.IGNORECASE)
        for match in plate_pattern.finditer(text):
            val = match.group(0)
            entities.append({
                "entity_type": "IT_PLATE",
                "category": "IDENTIFIER",
                "detector": "REGEX",
                "confidence": 0.97,
                "span_start": match.start(),
                "span_end": match.end(),
                "value": val,
                "action": "MASK",
                "action_reason": "Targa automobilistica italiana",
            })

        # 7. Nomi / Cognomi (Dictionary + Title boost)
        words = list(re.finditer(r"\b[A-Za-zÀ-ÖØ-öø-ÿ']+\b", text))
        for i, match in enumerate(words):
            word_str = match.group(0).lower()
            if word_str in FIRST_NAMES or word_str in LAST_NAMES:
                has_title = False
                if i > 0:
                    prev_word = words[i-1].group(0).lower()
                    if prev_word in TITLE_WORDS:
                        has_title = True
                conf = 0.93 if has_title else 0.85
                entities.append({
                    "entity_type": "PERSON",
                    "category": "IDENTIFIER",
                    "detector": "DICT",
                    "confidence": conf,
                    "span_start": match.start(),
                    "span_end": match.end(),
                    "value": match.group(0),
                    "action": "MASK",
                    "action_reason": "Nome/Cognome da dizionario italiano",
                })

        # 8. Dati Particolari (SPECIAL)
        for category_name, keywords in SPECIAL_KEYWORDS.items():
            for kw in keywords:
                kw_pattern = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
                for match in kw_pattern.finditer(text):
                    entities.append({
                        "entity_type": f"SPECIAL_{category_name}",
                        "category": "SPECIAL",
                        "detector": "DICT",
                        "confidence": 0.90,
                        "span_start": match.start(),
                        "span_end": match.end(),
                        "value": match.group(0),
                        "action": "BLOCK",
                        "action_reason": f"Dato particolare afferente a {category_name}",
                    })

        return entities
