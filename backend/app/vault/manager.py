import base64
import hashlib
import os
from pathlib import Path
import secrets
import sqlite3
import time
from typing import Optional, Tuple

try:
    from argon2 import PasswordHasher
    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives import hashes
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

class VaultLockedError(Exception):
    """Raised when an operation requiring vault access is attempted while locked."""
    pass

class VaultManager:
    def __init__(
        self,
        vault_path: Path,
        inactivity_timeout_seconds: int = 600,
        audit_callback: Optional[callable] = None,
    ):
        self.vault_path = vault_path
        self.inactivity_timeout_seconds = inactivity_timeout_seconds
        self.audit_callback = audit_callback
        self._master_key: Optional[bytes] = None
        self._aes_key: Optional[bytes] = None
        self._last_activity_time: float = 0.0
        self.salt_path = vault_path.parent / "vault_salt.bin"

    def _get_or_create_salt(self) -> bytes:
        os.makedirs(self.salt_path.parent, exist_ok=True)
        if self.salt_path.exists():
            return self.salt_path.read_bytes()
        salt = os.urandom(16)
        self.salt_path.write_bytes(salt)
        return salt

    def _derive_keys(self, passphrase: str) -> Tuple[bytes, bytes]:
        salt = self._get_or_create_salt()
        if ARGON2_AVAILABLE:
            ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4, hash_len=32)
            raw_key = ph.hash(passphrase + salt.hex()).encode("utf-8")
        else:
            raw_key = hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, 100000, 32)

        if CRYPTOGRAPHY_AVAILABLE:
            hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                info=b"aigate-vault-aes-gcm",
            )
            aes_key = hkdf.derive(raw_key)
        else:
            aes_key = hashlib.sha256(raw_key + salt + b"aigate-vault-aes-gcm").digest()

        return raw_key, aes_key

    def setup_vault(self, passphrase: str) -> str:
        raw_key, aes_key = self._derive_keys(passphrase)
        verify_check = hashlib.sha256(raw_key + b"aigate_vault_check").hexdigest()

        os.makedirs(self.vault_path.parent, exist_ok=True)
        conn = sqlite3.connect(self.vault_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pseudonym_map (
                    token TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    original_value_enc BLOB NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vault_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            cursor.execute(
                "INSERT OR REPLACE INTO vault_metadata (key, value) VALUES ('verification_hash', ?)",
                (verify_check,),
            )
            conn.commit()
        finally:
            conn.close()

        self._master_key = raw_key
        self._aes_key = aes_key
        self._last_activity_time = time.time()

        recovery_code = secrets.token_urlsafe(16)
        return recovery_code

    def unlock(self, passphrase: str) -> bool:
        if not self.vault_path.exists():
            return False
        try:
            raw_key, aes_key = self._derive_keys(passphrase)
            expected_check = hashlib.sha256(raw_key + b"aigate_vault_check").hexdigest()

            conn = sqlite3.connect(self.vault_path)
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM vault_metadata WHERE key = 'verification_hash'")
                row = cursor.fetchone()
                if not row or row[0] != expected_check:
                    return False
            finally:
                conn.close()

            self._master_key = raw_key
            self._aes_key = aes_key
            self._last_activity_time = time.time()
            return True
        except Exception:
            return False

    def is_locked(self) -> bool:
        if self._master_key is None or self._aes_key is None:
            return True
        if (time.time() - self._last_activity_time) > self.inactivity_timeout_seconds:
            self.lock()
            return True
        return False

    def lock(self) -> None:
        self._master_key = None
        self._aes_key = None
        self._last_activity_time = 0.0

    def _check_unlocked(self) -> None:
        if self.is_locked():
            raise VaultLockedError("Vault is locked. Provide master passphrase to unlock.")
        self._last_activity_time = time.time()

    def store_pseudonym(self, token: str, document_id: str, entity_type: str, original_value: str) -> None:
        self._check_unlocked()
        data_bytes = original_value.encode("utf-8")
        if CRYPTOGRAPHY_AVAILABLE:
            aesgcm = AESGCM(self._aes_key)
            nonce = os.urandom(12)
            ciphertext = aesgcm.encrypt(nonce, data_bytes, None)
            blob = nonce + ciphertext
        else:
            keystream = hashlib.sha256(self._aes_key + token.encode("utf-8")).digest()
            encrypted = bytes([b ^ keystream[i % len(keystream)] for i, b in enumerate(data_bytes)])
            blob = encrypted

        conn = sqlite3.connect(self.vault_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO pseudonym_map (token, document_id, entity_type, original_value_enc, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
                """,
                (token, document_id, entity_type, blob),
            )
            conn.commit()
        finally:
            conn.close()

    def get_original_value(self, token: str, document_id: str) -> Optional[str]:
        self._check_unlocked()
        conn = sqlite3.connect(self.vault_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT original_value_enc, entity_type FROM pseudonym_map WHERE token = ? AND document_id = ?",
                (token, document_id),
            )
            row = cursor.fetchone()
            if not row:
                return None
            blob, entity_type = row
            if CRYPTOGRAPHY_AVAILABLE:
                nonce = blob[:12]
                ciphertext = blob[12:]
                aesgcm = AESGCM(self._aes_key)
                decrypted = aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
            else:
                keystream = hashlib.sha256(self._aes_key + token.encode("utf-8")).digest()
                decrypted = bytes([b ^ keystream[i % len(keystream)] for i, b in enumerate(blob)]).decode("utf-8")

            if self.audit_callback:
                self.audit_callback(
                    component="VAULT",
                    action="DE_PSEUDONYMIZE",
                    object_type="TOKEN",
                    object_id=token,
                    detail={"document_id": document_id, "entity_type": entity_type},
                )
            return decrypted
        finally:
            conn.close()
