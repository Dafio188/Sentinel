import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Any, Dict, Optional
from backend.app.core.config import settings

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

def _canonical_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

class AuditChainManager:
    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path

    @property
    def db_path(self) -> Path:
        return self._db_path if self._db_path is not None else settings.DATABASE_PATH

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_latest_hash(self) -> str:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT event_hash FROM audit_events ORDER BY seq DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                return row["event_hash"]
            return GENESIS_HASH
        finally:
            conn.close()

    def append(
        self,
        component: str,
        action: str,
        object_type: Optional[str] = None,
        object_id: Optional[str] = None,
        input_hash: Optional[str] = None,
        output_hash: Optional[str] = None,
        rule_id: Optional[str] = None,
        risk: Optional[str] = None,
        detail: Optional[Dict[str, Any]] = None,
    ) -> int:
        prev_hash = self.get_latest_hash()
        ts = datetime.now(timezone.utc).isoformat()
        detail_json = _canonical_json(detail) if detail else None

        record_data = {
            "ts": ts,
            "component": component,
            "action": action,
            "object_type": object_type,
            "object_id": object_id,
            "input_hash": input_hash,
            "output_hash": output_hash,
            "rule_id": rule_id,
            "risk": risk,
            "detail_json": detail_json,
            "prev_hash": prev_hash,
        }

        payload_to_hash = (prev_hash + _canonical_json(record_data)).encode("utf-8")
        event_hash = hashlib.sha256(payload_to_hash).hexdigest()

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO audit_events (
                    ts, component, action, object_type, object_id,
                    input_hash, output_hash, rule_id, risk, detail_json,
                    prev_hash, event_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ts,
                    component,
                    action,
                    object_type,
                    object_id,
                    input_hash,
                    output_hash,
                    rule_id,
                    risk,
                    detail_json,
                    prev_hash,
                    event_hash,
                ),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def verify(self) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_events ORDER BY seq ASC")
            rows = cursor.fetchall()
            expected_prev_hash = GENESIS_HASH

            for row in rows:
                seq = row["seq"]
                if row["prev_hash"] != expected_prev_hash:
                    return seq

                record_data = {
                    "ts": row["ts"],
                    "component": row["component"],
                    "action": row["action"],
                    "object_type": row["object_type"],
                    "object_id": row["object_id"],
                    "input_hash": row["input_hash"],
                    "output_hash": row["output_hash"],
                    "rule_id": row["rule_id"],
                    "risk": row["risk"],
                    "detail_json": row["detail_json"],
                    "prev_hash": row["prev_hash"],
                }
                payload_to_hash = (row["prev_hash"] + _canonical_json(record_data)).encode("utf-8")
                computed_hash = hashlib.sha256(payload_to_hash).hexdigest()

                if computed_hash != row["event_hash"]:
                    return seq

                expected_prev_hash = row["event_hash"]

            return -1
        finally:
            conn.close()
