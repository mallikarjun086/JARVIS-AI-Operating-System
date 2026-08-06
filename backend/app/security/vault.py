"""
Secrets Vault Manager Engine.
Encrypts secrets at rest and manages secure retrieval.
"""

from typing import Dict, List, Optional
from app.security.crypto import crypto_engine
from app.security.schemas import SecretVaultEntry


class SecretsVaultManager:
    """Vault manager storing encrypted secret entries at rest."""

    def __init__(self) -> None:
        self._vault: Dict[str, SecretVaultEntry] = {}

    def set_secret(self, key_name: str, raw_value: str) -> SecretVaultEntry:
        """Encrypts raw secret value and stores entry in vault."""
        encrypted_val = crypto_engine.encrypt_string(raw_value)
        entry = SecretVaultEntry(key_name=key_name, encrypted_value=encrypted_val)
        self._vault[key_name] = entry
        return entry

    def get_secret(self, key_name: str) -> Optional[str]:
        """Decrypts and returns raw secret value by key name."""
        entry = self._vault.get(key_name)
        if not entry:
            return None
        return crypto_engine.decrypt_string(entry.encrypted_value)

    def list_secret_entries(self) -> List[SecretVaultEntry]:
        """Returns list of secret metadata entries (values remain encrypted)."""
        return list(self._vault.values())


secrets_vault = SecretsVaultManager()

# Seed default mock encrypted credentials for system testing
secrets_vault.set_secret("OPENAI_API_KEY", "sk-proj-jarvis-secret-key-12345")
secrets_vault.set_secret("POSTGRES_DB_PASSWORD", "SuperSecurePassword987!")
