# utilise cryptography.Fernet pour chiffrer la clé privée avant stockage
from cryptography.fernet import Fernet
import os

# GENERE UNE FOIS et stocker en .env (FERNET_KEY)
# Fernet.generate_key().decode()

FERNET_KEY = os.environ.get("FERNET_KEY")  # ex: base64 key
fernet = Fernet(FERNET_KEY.encode())

def encrypt_privkey(priv_hex: str) -> str:
    return fernet.encrypt(priv_hex.encode()).decode()

def decrypt_privkey(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()