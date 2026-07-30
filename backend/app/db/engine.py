import os
from pathlib import Path
import sqlite3
from backend.app.core.config import settings, BASE_DIR

def get_db_connection(db_path: Path = settings.DATABASE_PATH) -> sqlite3.Connection:
    os.makedirs(db_path.parent, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Path = settings.DATABASE_PATH) -> None:
    ddl_path = BASE_DIR / "docs" / "SPEC-DDL.sql"
    if not ddl_path.exists():
        raise FileNotFoundError(f"SPEC-DDL.sql non trovato in {ddl_path}")
    
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl_sql = f.read()

    conn = get_db_connection(db_path)
    try:
        conn.executescript(ddl_sql)
        _seed_providers(conn)
        conn.commit()
    finally:
        conn.close()

def _seed_providers(conn: sqlite3.Connection) -> None:
    providers = [
        ("ollama-local", "Ollama Local", "http://127.0.0.1:11434", "gemma4", "LOCAL", 0, 1, None, None, None, "LOW", None),
        ("anthropic", "Anthropic Claude", "https://api.anthropic.com", "claude-3-5-sonnet", "EXTERNAL", 0, 0, "US", "DPF", "PAID", "MEDIUM", None),
        ("openai", "OpenAI GPT", "https://api.openai.com", "gpt-4o", "EXTERNAL", 0, 0, "US", "DPF", "PAID", "MEDIUM", None),
        ("gemini", "Google Gemini", "https://generativelanguage.googleapis.com", "gemini-1.5-pro", "EXTERNAL", 0, 0, "US", "DPF", "FREE", "MEDIUM", None),
        ("deepseek", "DeepSeek", "https://api.deepseek.com", "deepseek-r1", "UNKNOWN", 1, 0, "CN", "NONE", None, "LOW", None),
    ]
    cursor = conn.cursor()
    for p in providers:
        cursor.execute(
            """
            INSERT OR IGNORE INTO llm_providers (
                id, name, endpoint, model, privacy_class, privacy_class_locked,
                endpoint_verified_local, country, transfer_mechanism, training_policy_tier,
                max_risk_allowed, params_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            p,
        )
