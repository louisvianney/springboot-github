# Atelier Chiffrement Python

Atelier pratique sur le chiffrement symétrique en Python avec les bibliothèques `cryptography` (Fernet) et `PyNaCl` (SecretBox).

---

## Prérequis

- Python 3.10+
- pip

## Installation

```bash
pip install -r requirements.txt
```

---

## Structure du projet

```
ATELIER_CHIFFREMENT/
├── requirements.txt
└── app/
    ├── fernet_demo.py       # Partie A — démo Fernet
    ├── file_crypto.py       # Partie B — chiffrement de fichiers
    ├── fernet_atelier1.py   # Atelier 1 — clé depuis GitHub Secrets
    └── nacl_atelier2.py     # Atelier 2 — PyNaCl SecretBox
```

---

## Partie A — Démo Fernet

`fernet_demo.py` illustre le cycle complet chiffrement / déchiffrement avec une clé Fernet.

Si la variable d'environnement `FERNET_KEY` est absente, le script en génère une nouvelle et indique comment l'exporter.

```bash
python app/fernet_demo.py
```

Sortie attendue :

```
=== Clé générée (aucune variable FERNET_KEY trouvée) ===
Clé : <clé_base64>
Pour la réutiliser : export FERNET_KEY=<clé_base64>

=== Chiffrement ===
Message original : Bonjour, ceci est un secret à encoder !
Token chiffré    : gAAAAAB...

=== Déchiffrement ===
Message déchiffré : Bonjour, ceci est un secret à encoder !
```

### Anatomie d'une clé Fernet

Une clé Fernet est une clé symétrique **256 bits encodée en Base64**. Elle contient deux sous-clés :
- 128 bits pour le chiffrement AES-128-CBC
- 128 bits pour l'authentification HMAC-SHA256

### Anatomie d'un token Fernet

Un token Fernet est composé de 5 champs :

| Champ      | Taille       | Rôle                              |
|------------|--------------|-----------------------------------|
| Version    | 1 octet      | Toujours `0x80`                   |
| Timestamp  | 8 octets     | Date de création (Unix)           |
| IV         | 16 octets    | Vecteur d'initialisation aléatoire|
| Ciphertext | variable     | Données chiffrées (AES-128-CBC)   |
| HMAC       | 32 octets    | Signature d'intégrité (SHA256)    |

---

## Partie B — Chiffrement de fichiers

`file_crypto.py` chiffre et déchiffre n'importe quel fichier depuis la ligne de commande.

**La variable `FERNET_KEY` doit être définie avant de l'utiliser.**

```bash
# Générer et exporter une clé
export FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Créer un fichier test
echo "Message Top secret !" > secret.txt

# Chiffrer
python app/file_crypto.py encrypt secret.txt secret.enc

# Déchiffrer
python app/file_crypto.py decrypt secret.enc secret.dec.txt
```

> **Que se passe-t-il si on modifie `secret.enc` avant de déchiffrer ?**
> Le HMAC détecte l'altération et lève une erreur `InvalidToken` — le fichier ne peut pas être déchiffré.

> **Risque lié au versioning :**
> Ne jamais commiter un fichier `.enc` et la clé dans le même dépôt. Si la clé fuite, tous les fichiers chiffrés sont compromis.

---

## Atelier 1 — Clé Fernet depuis GitHub Secrets

`fernet_atelier1.py` simule le fonctionnement d'un script déployé dans GitHub Codespaces ou Actions : la clé est injectée via une variable d'environnement, jamais écrite dans le code.

### Configuration dans GitHub Codespaces

1. Aller dans **Settings → Secrets and variables → Codespaces**
2. Créer un secret nommé `FERNET_KEY` avec la valeur de votre clé
3. Relancer le Codespace — la variable est automatiquement disponible

### En local

```bash
export FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
python app/fernet_atelier1.py
```

Le script chiffre plusieurs messages et vérifie leur déchiffrement. Si `FERNET_KEY` est absente, il affiche un message d'erreur explicite avec les instructions.

---

## Atelier 2 — PyNaCl SecretBox

`nacl_atelier2.py` implémente le même principe de chiffrement symétrique authentifié avec **PyNaCl**, une liaison Python vers la bibliothèque NaCl.

```bash
python app/nacl_atelier2.py
```

L'atelier couvre :
- Chiffrement et déchiffrement de texte
- Chiffrement de données binaires (fichier en mémoire)
- Détection d'altération (test d'intégrité)

### Algorithme : XSalsa20-Poly1305

| Composant   | Rôle                                    |
|-------------|-----------------------------------------|
| XSalsa20    | Chiffrement par flux (stream cipher)    |
| Poly1305    | Authentification (MAC)                  |
| Clé         | 32 octets (256 bits)                    |
| Nonce       | 24 octets aléatoires, inclus dans le message chiffré |

### Fernet vs NaCl SecretBox

| Critère          | Fernet                    | NaCl SecretBox               |
|------------------|---------------------------|------------------------------|
| Chiffrement      | AES-128-CBC               | XSalsa20                     |
| Authentification | HMAC-SHA256               | Poly1305                     |
| Taille de clé    | 256 bits                  | 256 bits                     |
| Nonce            | IV 16 octets (dans token) | 24 octets (inclus automatiquement) |
| Timestamp        | Oui                       | Non                          |
| Format clé       | Base64                    | Bytes / hex                  |
| Maturité         | Bien établi, pythonique   | Standard cryptographique moderne |

Les deux offrent un **chiffrement authentifié** : toute altération du message chiffré est détectée avant déchiffrement.

---

## Bonnes pratiques

- Ne jamais écrire une clé en dur dans le code source
- Stocker les clés dans des secrets (GitHub Secrets, variables d'environnement, coffre-fort de secrets)
- Ne jamais versionner un fichier contenant une clé (ajouter `*.key`, `*.pem` au `.gitignore`)
- Utiliser une clé différente par environnement (dev, staging, prod)
