import base64

from cryptography.fernet import Fernet

from app.config import settings


def _get_fernet() -> Fernet:
    # Ensure key is 32 bytes, base64-encoded for Fernet
    key = settings.encryption_key.encode()
    key_b64 = base64.urlsafe_b64encode(key[:32].ljust(32, b"\0"))
    return Fernet(key_b64)


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for storage."""
    f = _get_fernet()
    return f.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt a stored API key."""
    f = _get_fernet()
    return f.decrypt(encrypted_key.encode()).decode()
