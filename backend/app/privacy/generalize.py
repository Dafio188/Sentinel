import re

def generalize_value(entity_type: str, val: str) -> str:
    val_str = val.strip()

    # Age generalization
    if "AGE" in entity_type or val_str.isdigit() and len(val_str) <= 2:
        try:
            age = int(val_str)
            decade = (age // 10) * 10
            return f"fascia d'età {decade}-{decade+9} anni"
        except ValueError:
            pass

    # Date generalization -> Year
    date_match = re.search(r'\b(19|20)\d{2}\b', val_str)
    if date_match:
        return f"anno {date_match.group(0)}"

    # Currency amount generalization
    num_match = re.search(r'\b\d+[\d.,]*\b', val_str)
    if num_match:
        try:
            clean_num = float(num_match.group(0).replace(".", "").replace(",", "."))
            if clean_num < 1000:
                return "< 1.000 €"
            elif clean_num < 10000:
                return "1.000 - 10.000 €"
            elif clean_num < 50000:
                return "10.000 - 50.000 €"
            else:
                return "> 50.000 €"
        except ValueError:
            pass

    return f"[{entity_type}_GENERALIZZATO]"
