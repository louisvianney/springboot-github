import os
from cryptography.fernet import Fernet


def load_key() -> Fernet:
    key = os.environ.get("FERNET_KEY")
    if key is None:
        key = Fernet.generate_key().decode()
        print("=== Clé générée (aucune variable FERNET_KEY trouvée) ===")
        print(f"Clé : {key}")
        print(f"Pour la réutiliser : export FERNET_KEY={key}\n")
    return Fernet(key.encode() if isinstance(key, str) else key)


def main():
    f = load_key()

    message = "Bonjour, ceci est un secret à encoder !"

    # Chiffrement
    token = f.encrypt(message.encode())
    print("=== Chiffrement ===")
    print(f"Message original : {message}")
    print(f"Token chiffré    : {token.decode()}\n")

    # Déchiffrement
    decrypted = f.decrypt(token).decode()
    print("=== Déchiffrement ===")
    print(f"Message déchiffré : {decrypted}")


if __name__ == "__main__":
    main()
