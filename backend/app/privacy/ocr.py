import re
from typing import Any, Dict, List, Tuple
from backend.app.privacy.recognizers import verify_cf_checksum

class HybridOcrEngine:
    def cross_check_tokens(
        self, tesseract_token: str, gemma_token: str, confidence: float
    ) -> Tuple[str, str, float]:
        """
        Cross-check Tesseract vs Gemma vision transcription.
        Returns (chosen_token, flag_status, final_confidence)
        """
        if confidence >= 80.0 or tesseract_token == gemma_token:
            return tesseract_token, "OK", confidence

        # Divergence on low confidence token matching PII pattern (e.g. Fiscal Code format)
        cf_pattern = re.compile(r'^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$', re.IGNORECASE)
        
        is_tess_cf = bool(cf_pattern.match(tesseract_token.replace(" ", "")))
        is_gemma_cf = bool(cf_pattern.match(gemma_token.replace(" ", "")))

        if is_gemma_cf:
            # Gemma proposed a PII token: verify checksum
            if verify_cf_checksum(gemma_token):
                return gemma_token, "UNCERTAIN_PII", 0.65
            else:
                # Gemma hallucinated invalid checksum CF: discard Gemma, keep Tesseract + flag
                return tesseract_token, "UNCERTAIN_PII", 0.50

        if is_tess_cf or is_gemma_cf or (tesseract_token != gemma_token):
            return tesseract_token, "UNCERTAIN_PII", 0.55

        return tesseract_token, "OK", confidence
