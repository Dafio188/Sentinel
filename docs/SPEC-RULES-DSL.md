# AIGate — Rule DSL Specification (SPEC-RULES-DSL.md)

## Semantica a Tre Valori (Three-Valued Logic)

Il Rule Engine di AIGate valuta espressioni JsonLogic-like con una logica a tre valori:
- `TRUE` (Vero)
- `FALSE` (Falso)
- `UNKNOWN` (Sconosciuto / Mancante)

Ogni variabile non valorizzata o mancante nel modello di progetto propaga `UNKNOWN` (non `FALSE`).

---

## Tabella di Verità degli Operatori

### 1. AND (`and`)
| A | B | `and(A, B)` |
|---|---|---|
| TRUE | TRUE | TRUE |
| TRUE | FALSE | FALSE |
| FALSE | TRUE | FALSE |
| FALSE | FALSE | FALSE |
| TRUE | UNKNOWN | UNKNOWN |
| FALSE | UNKNOWN | FALSE |
| UNKNOWN | TRUE | UNKNOWN |
| UNKNOWN | FALSE | FALSE |
| UNKNOWN | UNKNOWN | UNKNOWN |

### 2. OR (`or`)
| A | B | `or(A, B)` |
|---|---|---|
| TRUE | TRUE | TRUE |
| TRUE | FALSE | TRUE |
| FALSE | TRUE | TRUE |
| FALSE | FALSE | FALSE |
| TRUE | UNKNOWN | TRUE |
| FALSE | UNKNOWN | UNKNOWN |
| UNKNOWN | TRUE | TRUE |
| UNKNOWN | FALSE | UNKNOWN |
| UNKNOWN | UNKNOWN | UNKNOWN |

### 3. NOT (`!`)
| A | `!(A)` |
|---|---|
| TRUE | FALSE |
| FALSE | TRUE |
| UNKNOWN | UNKNOWN |

### 4. Confronti (`==`, `!=`, `>`, `>=`, `<`, `<=`, `in`)
Se uno qualsiasi degli operandi è `UNKNOWN`, l'esito del confronto è `UNKNOWN`.

### 5. Somma / Aritmetica (`+`)
Se uno qualsiasi dei termini da sommare è `UNKNOWN`, l'esito è `UNKNOWN`.

---

## Operatore Condizionale (`if`)
Sintassi: `{"if": [condizione, ramo_true, ramo_false]}`
- Se `condizione` è `TRUE`, valuta `ramo_true`.
- Se `condizione` è `FALSE`, valuta `ramo_false` (default `FALSE` se assente).
- Se `condizione` è `UNKNOWN`, l'esito di `if` è `UNKNOWN`.

---

## Struttura delle Regole JSON
```json
{
  "rule_id": "GDPR.ART35.DPIA",
  "framework": "GDPR",
  "category": "CLASSIFICATION",
  "severity": "HIGH",
  "source_refs": [{"source_id": "EU_2016_679", "article": "35"}],
  "condition": {
    ">=": [
      {"+": [
        {"if": [{"var": "profiling"}, 1, 0]},
        {"if": [{"in": ["SPECIAL", {"var": "data_types"}]}, 1, 0]}
      ]},
      2
    ]
  },
  "on_true": {"finding": "DPIA_REQUIRED", "action": "REVIEW"},
  "on_false": {"finding": "DPIA_NOT_INDICATED", "action": "INFO"},
  "on_unknown": {"finding": "UNKNOWN", "ask": ["Q_SCALE", "Q_DATA_TYPES"]},
  "kb_version": "KB-2026.07-B"
}
```
