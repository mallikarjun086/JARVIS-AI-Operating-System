"""
AES-256 Fernet Cryptography Engine for Data Encryption at Rest.
"""

import base64
import os
from typing import Optional
from cryptography.fernet import Fernet


class CryptographyEngine:
    """AES-256 Fernet encryption and decryption engine."""

    def __init__(self, key: Optional[bytes] = None) -> None:
        if not key:
            key = Fernet.generate_key()
        self._cipher = Fernet(key)

    def encrypt_string(self, text: str) -> str:
        """Encrypts plaintext string into Base64 ciphertext."""
        encrypted_bytes = self._cipher.encrypt(text.encode("utf-8"))
        return base64.b64encode(encrypted_bytes).decode("utf-8")

    def decrypt_string(self, ciphertext_b64: str) -> str:
        """Decrypts Base64 ciphertext into plaintext string."""
        raw_bytes = base64.b64decode(ciphertext_b64.encode("utf-8"))
        decrypted_bytes = self._cipher.decrypt(raw_bytes)
        return decrypted_bytes.decode("utf-8")


crypto_engine = CryptographyEngine()
