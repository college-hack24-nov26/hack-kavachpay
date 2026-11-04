"""
AES-256-GCM Secure Encryption & Backup Recovery Engine
KavachSetu – The Ghost Protocol

Provides authenticated encryption at rest for documents and password-derived
encrypted backup export & restore workflows.
"""

import os
import json
import base64
import hashlib
from typing import Dict, Any, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from backend.app.core.config import settings

# Master storage key derived from SECRET_KEY
STORAGE_SALT = b"KAVACHSETU_VAULT_ENCRYPTION_SALT_2026"

def _get_master_aes_key() -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=STORAGE_SALT,
        iterations=100_000
    )
    return kdf.derive(settings.SECRET_KEY.encode())


class VaultEncryption:
    @staticmethod
    def encrypt_document(data: bytes) -> bytes:
        """
        Encrypts raw document file bytes using AES-256-GCM.
        Prepend 12-byte random IV.
        """
        key = _get_master_aes_key()
        aesgcm = AESGCM(key)
        iv = os.urandom(12)
        ciphertext = aesgcm.encrypt(iv, data, None)
        return iv + ciphertext

    @staticmethod
    def decrypt_document(encrypted_data: bytes) -> bytes:
        """
        Decrypts AES-256-GCM document bytes.
        """
        key = _get_master_aes_key()
        aesgcm = AESGCM(key)
        iv = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        return aesgcm.decrypt(iv, ciphertext, None)

    @staticmethod
    def create_encrypted_backup(backup_payload: Dict[str, Any], passphrase: str) -> Dict[str, Any]:
        """
        Derives an AES-256 key from user passphrase and creates an authenticated encrypted backup archive.
        """
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=150_000
        )
        key = kdf.derive(passphrase.encode())
        aesgcm = AESGCM(key)
        iv = os.urandom(12)

        plaintext = json.dumps(backup_payload, separators=(',', ':')).encode('utf-8')
        ciphertext = aesgcm.encrypt(iv, plaintext, None)

        checksum = hashlib.sha256(plaintext).hexdigest()

        return {
            "format": "KAVACHSETU_ENCRYPTED_VAULT_BACKUP",
            "version": "2.0",
            "kdf": "PBKDF2-HMAC-SHA256",
            "iterations": 150_000,
            "cipher": "AES-256-GCM",
            "salt_b64": base64.b64encode(salt).decode('utf-8'),
            "iv_b64": base64.b64encode(iv).decode('utf-8'),
            "ciphertext_b64": base64.b64encode(ciphertext).decode('utf-8'),
            "plaintext_sha256": checksum,
            "created_at": backup_payload.get("exported_at")
        }

    @staticmethod
    def restore_encrypted_backup(encrypted_backup: Dict[str, Any], passphrase: str) -> Tuple[bool, Any]:
        """
        Decrypts and validates an encrypted backup archive using user passphrase.
        """
        try:
            salt = base64.b64decode(encrypted_backup["salt_b64"])
            iv = base64.b64decode(encrypted_backup["iv_b64"])
            ciphertext = base64.b64decode(encrypted_backup["ciphertext_b64"])
            expected_checksum = encrypted_backup.get("plaintext_sha256")
            iterations = encrypted_backup.get("iterations", 150_000)

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=iterations
            )
            key = kdf.derive(passphrase.encode())
            aesgcm = AESGCM(key)

            plaintext_bytes = aesgcm.decrypt(iv, ciphertext, None)
            actual_checksum = hashlib.sha256(plaintext_bytes).hexdigest()

            if expected_checksum and actual_checksum != expected_checksum:
                return False, "Integrity check failed: Plaintext checksum mismatch."

            restored_data = json.loads(plaintext_bytes.decode('utf-8'))
            return True, restored_data

        except Exception as ex:
            return False, f"Decryption failed: Incorrect passphrase or corrupted backup file ({str(ex)})."
