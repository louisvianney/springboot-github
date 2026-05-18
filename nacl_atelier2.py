"""
Atelier 2 – Chiffrement symétrique avec PyNaCl SecretBox.

PyNaCl utilise XSalsa20-Poly1305 :
  - XSalsa20 : chiffrement par flux (stream cipher)
  - Poly1305  : authentification (MAC) — garantit l'intégrité du message
  - Clé       : 32 octets (256 bits)
  - Nonce     : 24 octets aléatoires, inclus dans le message chiffré

Différences avec Fernet :
  | Critère         | Fernet (AES-128-CBC + HMAC) | NaCl SecretBox (XSalsa20-Poly1305) |
  |-----------------|----------------------------|------------------------------------|
  | Algo chiffrement| AES-128 en mode CBC        | XSalsa20 (flux)                    |
  | Authentification| HMAC-SHA256                | Poly1305                           |
  | Taille clé      | 256 bits (128 chiffrement) | 256 bits                           |
  | Nonce           | IV 16 octets dans token    | 24 octets, inclus automatiquement  |
  | Timestamp       | Oui (dans le token)        | Non                                |
"""

import os
import nacl.secret
import nacl.utils
import nacl.encoding


def generate_key() -> bytes:
    return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)  # 32 octets


def load_or_generate_key() -> bytes:
    hex_key = os.environ.get("NACL_KEY")
    if hex_key:
        key = bytes.fromhex(hex_key)
        print("[OK] Clé NaCl chargée depuis la variable d'environnement NACL_KEY.\n")
    else:
        key = generate_key()
        print("[INFO] Aucune variable NACL_KEY trouvée. Nouvelle clé générée.")
        print(f"  Clé (hex) : {key.hex()}")
        print(f"  Pour la réutiliser : export NACL_KEY={key.hex()}\n")
    return key


def chiffrer(box: nacl.secret.SecretBox, message: str) -> bytes:
    """Chiffre un message. Le nonce (24 octets) est inclus dans le résultat."""
    return box.encrypt(message.encode())


def dechiffrer(box: nacl.secret.SecretBox, ciphertext: bytes) -> str:
    """Déchiffre et vérifie l'authenticité du message."""
    return box.decrypt(ciphertext).decode()


def demo_texte(box: nacl.secret.SecretBox) -> None:
    print("=== Chiffrement de texte ===\n")
    messages = [
        "Bonjour depuis PyNaCl !",
        "Données ultra-secrètes : 42",
        "XSalsa20 + Poly1305 = chiffrement authentifié",
    ]

    for msg in messages:
        encrypted = chiffrer(box, msg)
        decrypted = dechiffrer(box, encrypted)
        print(f"  Original  : {msg}")
        print(f"  Chiffré   : {encrypted.hex()[:60]}...")
        print(f"  Déchiffré : {decrypted}\n")


def demo_fichier(box: nacl.secret.SecretBox) -> None:
    print("=== Chiffrement de fichier (en mémoire) ===\n")
    contenu = b"Contenu du fichier secret\nLigne 2\nFin du fichier."

    encrypted = box.encrypt(contenu)
    print(f"  Taille originale  : {len(contenu)} octets")
    print(f"  Taille chiffrée   : {len(encrypted)} octets (+ {len(encrypted)-len(contenu)} pour nonce+MAC)")

    decrypted = box.decrypt(encrypted)
    assert decrypted == contenu
    print("  [OK] Déchiffrement et vérification d'intégrité réussis.\n")


def demo_alteration(box: nacl.secret.SecretBox) -> None:
    print("=== Test d'intégrité (altération du message) ===\n")
    msg = "Message authentique"
    encrypted = bytearray(chiffrer(box, msg))

    # Modification d'un octet dans la partie chiffrée (après le nonce de 24 octets)
    encrypted[30] ^= 0xFF

    try:
        box.decrypt(bytes(encrypted))
        print("  [ECHEC] L'altération n'a pas été détectée !")
    except nacl.exceptions.CryptoError:
        print("  [OK] Altération détectée par Poly1305 — déchiffrement refusé.")
    print()


def main():
    print("=== Atelier 2 : Chiffrement avec PyNaCl SecretBox ===\n")

    key = load_or_generate_key()
    box = nacl.secret.SecretBox(key)

    demo_texte(box)
    demo_fichier(box)
    demo_alteration(box)

    print("=== Comparaison Fernet vs NaCl SecretBox ===")
    print("  Fernet      : AES-128-CBC + HMAC-SHA256, avec timestamp, clé en Base64")
    print("  NaCl        : XSalsa20-Poly1305, sans timestamp, clé en bytes (32 oct.)")
    print("  Les deux    : chiffrement authentifié, protection contre l'altération")
    print("  Avantage NaCl : algorithme plus moderne, nonce 24 octets (risque collision << AES-CBC IV)")


if __name__ == "__main__":
    main()
