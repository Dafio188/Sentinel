import re
from typing import Any, Dict, List, Tuple
from backend.app.privacy.recognizers import DeterministicDetector

class ZeroResidueValidator:
    def __init__(self):
        self.detector = DeterministicDetector()

    def validate(self, protected_text: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Re-scans protected text from scratch.
        Returns (validator_pass, residual_findings)
        """
        findings = self.detector.scan(protected_text)
        high_conf_findings = []

        for f in findings:
            val = f.get("value", "").strip()
            # Ignore valid placeholder tokens such as [PERSON], PERSONA_001, [IT_FISCAL_CODE], [SPECIAL_HEALTH]
            if (val.startswith("[") and val.endswith("]")) or re.match(r'^[A-Z_]+_\d{3}$', val):
                continue

            start = f.get("span_start")
            end = f.get("span_end")
            if start is not None and start > 0 and end is not None and end < len(protected_text):
                if protected_text[start-1] == "[" and protected_text[end] == "]":
                    continue

            if f.get("confidence", 0.0) >= 0.70:
                high_conf_findings.append(f)

        validator_pass = len(high_conf_findings) == 0
        return validator_pass, high_conf_findings
