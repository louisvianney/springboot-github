"""
Atelier 1 – Chiffrement Fernet avec clé stockée dans un Secret GitHub.

Dans GitHub Codespaces / Actions, le secret est injecté via la variable
d'environnement FERNET_KEY (Settings → Secrets → Codespaces).
En local, exportez-la avant d'exécuter le script :
    export FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
"""

import os
import sys
from cryptography.fernet import Fernet, InvalidToken


def load_key_from_secret() -> Fernet:
    key = os.environ.get("FERNET_KEY")
    if not key:
        print(
            "[ERREUR] La variable d'environnement FERNET_KEY est absente.\n"
            "Dans GitHub Codespaces, ajoutez-la dans :\n"
            "  Settings → Secrets and variables → Codespaces → New secret\n\n"
            "En local, générez et exportez une clé :\n"
            "  export FERNET_KEY=$(python -c \""
            "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\")"
        )
        sys.exit(1)
    return Fernet(key.encode())


def chiffrer(f: Fernet, message: str) -> bytes:
    return f.encrypt(message.encode())


def dechiffrer(f: Fernet, token: bytes) -> str:
    try:
        return f.decrypt(token).decode()
    except InvalidToken:
        print("[ERREUR] Impossible de déchiffrer : clé incorrecte ou token altéré.")
        sys.exit(1)


def main():
    print("=== Atelier 1 : Fernet avec clé depuis GitHub Secrets ===\n")

    f = load_key_from_secret()
    print("[OK] Clé Fernet chargée depuis la variable d'environnement FERNET_KEY.\n")

    messages = [
        "Message confidentiel n°1",
        "Données sensibles : mot de passe admin = S3cr3t!",
        "Coordonnées GPS : 48.8566° N, 2.3522° E",
    ]

    tokens = []
    print("--- Chiffrement ---")
    for msg in messages:
        token = chiffrer(f, msg)
        tokens.append(token)
        print(f"  Original  : {msg}")
        print(f"  Chiffré   : {token.decode()}\n")

    print("--- Déchiffrement ---")
    for token in tokens:
        clair = dechiffrer(f, token)
        print(f"  Token     : {token.decode()[:40]}...")
        print(f"  Déchiffré : {clair}\n")


if __name__ == "__main__":
    main()
