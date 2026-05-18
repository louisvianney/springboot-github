import argparse
import os
import sys
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken


def get_fernet() -> Fernet:
    key = os.environ.get("FERNET_KEY")
    if not key:
        print(
            "Erreur : la variable d'environnement FERNET_KEY n'est pas définie.\n"
            "Générez une clé avec :\n"
            "  python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"\n"
            "Puis exportez-la : export FERNET_KEY=<votre_clé>"
        )
        sys.exit(1)
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_file(input_path: Path, output_path: Path) -> None:
    f = get_fernet()
    data = input_path.read_bytes()
    encrypted = f.encrypt(data)
    output_path.write_bytes(encrypted)
    print(f"Fichier chiffré : {output_path}")


def decrypt_file(input_path: Path, output_path: Path) -> None:
    f = get_fernet()
    data = input_path.read_bytes()
    try:
        decrypted = f.decrypt(data)
    except InvalidToken:
        print("Erreur : clé incorrecte ou fichier altéré (InvalidToken).")
        sys.exit(1)
    output_path.write_bytes(decrypted)
    print(f"Fichier déchiffré : {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Chiffrement/déchiffrement de fichiers avec Fernet")
    parser.add_argument("mode", choices=["encrypt", "decrypt"], help="Mode : encrypt ou decrypt")
    parser.add_argument("input", type=Path, help="Fichier d'entrée")
    parser.add_argument("output", type=Path, help="Fichier de sortie")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Erreur : le fichier '{args.input}' n'existe pas.")
        sys.exit(1)

    if args.mode == "encrypt":
        encrypt_file(args.input, args.output)
    else:
        decrypt_file(args.input, args.output)


if __name__ == "__main__":
    main()
