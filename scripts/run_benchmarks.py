import json
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.arks.retrieval import ArksRetrieval
from backend.app.compliance.engine import ComplianceEngine
from backend.app.core.config import settings
from backend.app.db.engine import get_db_connection, init_db
from backend.app.gate.preflight import PreflightGate
from backend.app.privacy.anonymizer import AnonymizerEngine

def run_benchmarks():
    print("=== AIGate Performance & Compliance Benchmarks ===")
    init_db(settings.DATABASE_PATH)
    results = {}

    # 1. Privacy Gate Pre-flight Overhead (< 20ms)
    gate = PreflightGate()
    t0 = time.perf_counter()
    for _ in range(50):
        gate.evaluate("ollama-local", "Prompt di test per la valutazione del gateway con Mario Rossi")
    t1 = time.perf_counter()
    preflight_avg_ms = ((t1 - t0) / 50) * 1000
    results["preflight_gate_avg_ms"] = round(preflight_avg_ms, 2)
    print(f"[BENCHMARK] Pre-flight Privacy Gate: {preflight_avg_ms:.2f} ms (Target < 20 ms)")

    # 2. Rule Engine Benchmark 64 Rules (< 30ms)
    engine = ComplianceEngine()
    project_model = {
        "is_ai_system": "YES",
        "domain": "employment",
        "purpose": "evaluation",
        "automation_level": "RECOMMENDATION",
        "data_types": ["SPECIAL", "IDENTIFIER"],
    }

    # Ensure bench project exists
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO projects (id, name, intended_purpose, domain, status, features_json, created_at, updated_at)
            VALUES ('proj_bench_01', 'Bench Project', 'Evaluation', 'employment', 'DRAFT', '{}', datetime('now'), datetime('now'))
            """,
        )
        conn.commit()
    finally:
        conn.close()

    t0 = time.perf_counter()
    for _ in range(20):
        engine.assess_project("proj_bench_01", project_model)
    t1 = time.perf_counter()
    rule_engine_avg_ms = ((t1 - t0) / 20) * 1000
    results["rule_engine_avg_ms"] = round(rule_engine_avg_ms, 2)
    print(f"[BENCHMARK] Rule Engine Execution: {rule_engine_avg_ms:.2f} ms (Target < 30 ms)")

    # 3. Hybrid Retrieval ARKS RRF (< 50ms)
    retrieval = ArksRetrieval()
    t0 = time.perf_counter()
    for _ in range(30):
        retrieval.search("obblighi trasparenza intelligenza artificiale high risk")
    t1 = time.perf_counter()
    retrieval_avg_ms = ((t1 - t0) / 30) * 1000
    results["retrieval_rrf_avg_ms"] = round(retrieval_avg_ms, 2)
    print(f"[BENCHMARK] ARKS Hybrid Retrieval RRF: {retrieval_avg_ms:.2f} ms (Target < 50 ms)")

    # 4. Anonymizer Engine Benchmark (< 150ms)
    anonymizer = AnonymizerEngine()
    sample_text = "Mario Rossi ha Codice Fiscale RSSMRA78T13A662B e lavora presso la sede centrale. " * 50
    t0 = time.perf_counter()
    anonymizer.anonymize(sample_text, [], "BALANCED", "doc_bench_01")
    t1 = time.perf_counter()
    anonymizer_ms = (t1 - t0) * 1000
    results["anonymizer_engine_ms"] = round(anonymizer_ms, 2)
    print(f"[BENCHMARK] Anonymizer Engine: {anonymizer_ms:.2f} ms (Target < 150 ms)")

    # Save benchmark results JSON
    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    docs_dir.mkdir(exist_ok=True)
    benchmark_file = docs_dir / "BENCHMARK_RESULTS.json"
    benchmark_file.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"\n[SUCCESS] Report dei benchmark salvato in {benchmark_file}")

if __name__ == "__main__":
    run_benchmarks()
