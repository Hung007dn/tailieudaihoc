#!/usr/bin/env python3
"""
ECIES Lab: Elliptic Curve Integrated Encryption Scheme
======================================================

Version: v2-menu-and-cli

This file revises the older TinyEC ECIES-like demo into a classroom-friendly
lab script with a numbered menu similar to the ECDSA/ECDHE lab style, plus
optional argparse subcommands for repeatable command-line testing.

Scheme implemented for teaching
-------------------------------
Receiver has a long-term EC/XDH key pair:

    Receiver private key: d_B
    Receiver public key : Q_B = d_B * G

Encryption uses a fresh ephemeral key pair each time:

    1. Sender generates ephemeral scalar r and ephemeral public key R = r * G.
    2. Sender computes ECDH/XDH shared secret Z = r * Q_B.
    3. Sender derives AEAD key K = HKDF-SHA256(Z, salt, info).
    4. Sender encrypts plaintext with AES-GCM using K.
    5. Ciphertext package = version || group || ephemeral public key || nonce || ciphertext+tag.

Decryption:

    1. Receiver parses the ephemeral public key R.
    2. Receiver computes the same shared secret Z = d_B * R.
    3. Receiver derives the same K with HKDF-SHA256.
    4. Receiver verifies and decrypts AES-GCM ciphertext.

Security note
-------------
This script is for teaching. It uses a vetted crypto backend for primitive
operations, but prints secrets when requested and stores lab keys on disk.
Do not use it as a production message format or key-management design.
"""

from __future__ import annotations

import argparse
import base64
import json
import secrets
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

try:
    from cryptography import __version__ as CRYPTOGRAPHY_VERSION
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.backends.openssl.backend import backend as openssl_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec, x25519, x448
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "This lab requires pyca/cryptography. Install it with:\n"
        "  python -m pip install cryptography\n"
        f"Import error: {exc}"
    )


# ============================================================
# GROUP DEFINITIONS
# ============================================================

FAMILY_EC = "short-weierstrass-ecdh"
FAMILY_XDH = "montgomery-xdh"


@dataclass(frozen=True)
class ECIESGroup:
    name: str
    aliases: Tuple[str, ...]
    family: str
    security_bits: int
    description: str

    def all_names(self) -> Tuple[str, ...]:
        return (self.name, *self.aliases)


GROUPS: Tuple[ECIESGroup, ...] = (
    ECIESGroup(
        name="secp256r1",
        aliases=("p-256", "p256", "prime256v1", "nistp256"),
        family=FAMILY_EC,
        security_bits=128,
        description="NIST P-256 / prime256v1 ECDH group",
    ),
    ECIESGroup(
        name="secp384r1",
        aliases=("p-384", "p384", "nistp384"),
        family=FAMILY_EC,
        security_bits=192,
        description="NIST P-384 ECDH group",
    ),
    ECIESGroup(
        name="secp521r1",
        aliases=("p-521", "p521", "nistp521"),
        family=FAMILY_EC,
        security_bits=256,
        description="NIST P-521 ECDH group",
    ),
    ECIESGroup(
        name="secp256k1",
        aliases=("k-256", "k256", "bitcoin"),
        family=FAMILY_EC,
        security_bits=128,
        description="SECG secp256k1 ECDH group",
    ),
    ECIESGroup(
        name="x25519",
        aliases=("curve25519", "x-25519"),
        family=FAMILY_XDH,
        security_bits=128,
        description="Montgomery X25519 key-agreement group",
    ),
    ECIESGroup(
        name="x448",
        aliases=("curve448", "x-448"),
        family=FAMILY_XDH,
        security_bits=224,
        description="Montgomery X448 key-agreement group",
    ),
)


def _key(name: str) -> str:
    return name.strip().lower().replace("_", "-")


GROUP_LOOKUP: Dict[str, ECIESGroup] = {}
for group in GROUPS:
    for alias in group.all_names():
        GROUP_LOOKUP[_key(alias)] = group


def parse_group(name: str) -> ECIESGroup:
    try:
        return GROUP_LOOKUP[_key(name)]
    except KeyError as exc:
        known = ", ".join(g.name for g in GROUPS)
        raise argparse.ArgumentTypeError(f"unknown group {name!r}; supported groups: {known}") from exc


def ec_curve_object(group: ECIESGroup):
    mapping = {
        "secp256r1": ec.SECP256R1,
        "secp384r1": ec.SECP384R1,
        "secp521r1": ec.SECP521R1,
        "secp256k1": ec.SECP256K1,
    }
    if group.name not in mapping:
        raise ValueError(f"{group.name} is not a short-Weierstrass EC group")
    return mapping[group.name]()


def generate_private_key(group: ECIESGroup):
    if group.family == FAMILY_EC:
        return ec.generate_private_key(ec_curve_object(group))
    if group.name == "x25519":
        return x25519.X25519PrivateKey.generate()
    if group.name == "x448":
        return x448.X448PrivateKey.generate()
    raise ValueError(f"unsupported group {group.name}")


# ============================================================
# SERIALIZATION HELPERS
# ============================================================


def private_key_to_pem(private_key, password: Optional[str] = None) -> bytes:
    if password:
        enc = serialization.BestAvailableEncryption(password.encode("utf-8"))
    else:
        enc = serialization.NoEncryption()
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc,
    )


def public_key_to_pem(public_key) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def public_key_to_exchange_bytes(public_key, group: ECIESGroup) -> bytes:
    """Bytes placed into the ECIES package as the ephemeral public key."""
    if group.family == FAMILY_EC:
        return public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint,
        )
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def private_key_raw_or_scalar_hex(private_key, group: ECIESGroup) -> str:
    """Return a teaching-oriented private-key display string."""
    if group.family == FAMILY_EC:
        return hex(private_key.private_numbers().private_value)
    raw = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return raw.hex()


def load_private_key(path: str, password: Optional[str] = None):
    data = Path(path).read_bytes()
    return serialization.load_pem_private_key(
        data,
        password=password.encode("utf-8") if password else None,
    )


def load_public_key(path: str):
    return serialization.load_pem_public_key(Path(path).read_bytes())


def load_public_exchange_bytes(path: str, group: ECIESGroup):
    """Load peer/recipient public key from PEM or raw exchange bytes."""
    data = Path(path).read_bytes()
    stripped = data.strip()

    if stripped.startswith(b"-----BEGIN"):
        return serialization.load_pem_public_key(data)

    # Allow raw bytes stored directly or hex text stored in a text file.
    try:
        raw = bytes.fromhex(stripped.decode("ascii"))
    except Exception:
        raw = data

    return public_key_from_exchange_bytes(raw, group)


def public_key_from_exchange_bytes(data: bytes, group: ECIESGroup):
    if group.family == FAMILY_EC:
        return ec.EllipticCurvePublicKey.from_encoded_point(ec_curve_object(group), data)
    if group.name == "x25519":
        return x25519.X25519PublicKey.from_public_bytes(data)
    if group.name == "x448":
        return x448.X448PublicKey.from_public_bytes(data)
    raise ValueError(f"unsupported group {group.name}")


def public_key_summary(public_key, group: ECIESGroup) -> str:
    exchange = public_key_to_exchange_bytes(public_key, group)
    lines = [f"public exchange bytes ({len(exchange)} byte): {exchange.hex()}"]
    if group.family == FAMILY_EC:
        nums = public_key.public_numbers()
        lines.append(f"Q.x = {hex(nums.x)}")
        lines.append(f"Q.y = {hex(nums.y)}")
    return "\n".join(lines)


# ============================================================
# ECIES CORE
# ============================================================


def choose_hkdf_hash(group: ECIESGroup):
    if group.security_bits >= 224:
        return hashes.SHA512()
    if group.security_bits >= 192:
        return hashes.SHA384()
    return hashes.SHA256()


def exchange_shared_secret(private_key, peer_public_key, group: ECIESGroup) -> bytes:
    if group.family == FAMILY_EC:
        return private_key.exchange(ec.ECDH(), peer_public_key)
    return private_key.exchange(peer_public_key)


def hkdf_derive(shared_secret: bytes, group: ECIESGroup, key_len: int, salt: bytes, info: bytes) -> bytes:
    return HKDF(
        algorithm=choose_hkdf_hash(group),
        length=key_len,
        salt=salt if salt else None,
        info=info,
    ).derive(shared_secret)


def b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def b64d(text: str) -> bytes:
    pad = "=" * ((4 - len(text) % 4) % 4)
    return base64.urlsafe_b64decode((text + pad).encode("ascii"))


def encode_package(package: dict, output_format: str) -> str:
    json_bytes = json.dumps(package, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if output_format == "json":
        return json.dumps(package, indent=2)
    if output_format == "hex":
        return json_bytes.hex()
    if output_format == "base64":
        return base64.b64encode(json_bytes).decode("ascii")
    raise ValueError("output format must be json, base64, or hex")


def decode_package(encoded: str, input_format: str) -> dict:
    text = encoded.strip()
    if input_format == "json":
        return json.loads(text)
    if input_format == "hex":
        return json.loads(bytes.fromhex(text).decode("utf-8"))
    if input_format == "base64":
        return json.loads(base64.b64decode(text).decode("utf-8"))
    raise ValueError("input format must be json, base64, or hex")


def ecies_encrypt(
    plaintext: bytes,
    recipient_public_key,
    group: ECIESGroup,
    *,
    aad: bytes = b"",
    salt: bytes = b"",
    info: bytes = b"ECIES lab v2",
    key_len: int = 32,
    show_steps: bool = False,
) -> Tuple[dict, dict]:
    ephemeral_private = generate_private_key(group)
    ephemeral_public = ephemeral_private.public_key()
    ephemeral_public_bytes = public_key_to_exchange_bytes(ephemeral_public, group)

    shared_secret = exchange_shared_secret(ephemeral_private, recipient_public_key, group)
    aead_key = hkdf_derive(shared_secret, group, key_len, salt, info)
    nonce = secrets.token_bytes(12)

    aesgcm = AESGCM(aead_key)
    ciphertext_and_tag = aesgcm.encrypt(nonce, plaintext, aad)

    package = {
        "version": "ECIES-LAB-v2",
        "group": group.name,
        "kdf": f"HKDF-{choose_hkdf_hash(group).name.upper()}",
        "aead": "AES-GCM",
        "key_len": key_len,
        "ephemeral_public": b64e(ephemeral_public_bytes),
        "nonce": b64e(nonce),
        "salt": b64e(salt),
        "info": b64e(info),
        "aad": b64e(aad),
        "ciphertext_tag": b64e(ciphertext_and_tag),
    }

    trace = {
        "ephemeral_private": private_key_raw_or_scalar_hex(ephemeral_private, group),
        "ephemeral_public_hex": ephemeral_public_bytes.hex(),
        "shared_secret_hex": shared_secret.hex(),
        "derived_aead_key_hex": aead_key.hex(),
        "nonce_hex": nonce.hex(),
        "aad_hex": aad.hex(),
        "plaintext_hex": plaintext.hex(),
        "ciphertext_tag_hex": ciphertext_and_tag.hex(),
    }

    if show_steps:
        print_encryption_steps(group, trace, package)

    return package, trace


def ecies_decrypt(
    package: dict,
    recipient_private_key,
    *,
    show_steps: bool = False,
) -> Tuple[bytes, dict]:
    package_group = parse_group(package["group"])
    ephemeral_public_bytes = b64d(package["ephemeral_public"])
    ephemeral_public = public_key_from_exchange_bytes(ephemeral_public_bytes, package_group)
    nonce = b64d(package["nonce"])
    salt = b64d(package.get("salt", ""))
    info = b64d(package.get("info", ""))
    aad = b64d(package.get("aad", ""))
    ciphertext_and_tag = b64d(package["ciphertext_tag"])
    key_len = int(package.get("key_len", 32))

    shared_secret = exchange_shared_secret(recipient_private_key, ephemeral_public, package_group)
    aead_key = hkdf_derive(shared_secret, package_group, key_len, salt, info)
    plaintext = AESGCM(aead_key).decrypt(nonce, ciphertext_and_tag, aad)

    trace = {
        "ephemeral_public_hex": ephemeral_public_bytes.hex(),
        "shared_secret_hex": shared_secret.hex(),
        "derived_aead_key_hex": aead_key.hex(),
        "nonce_hex": nonce.hex(),
        "aad_hex": aad.hex(),
        "ciphertext_tag_hex": ciphertext_and_tag.hex(),
        "plaintext_hex": plaintext.hex(),
    }

    if show_steps:
        print_decryption_steps(package_group, trace)

    return plaintext, trace


# ============================================================
# PRINTING / TEACHING
# ============================================================


def print_line(title: str = "") -> None:
    if title:
        print("\n" + title)
    print("-" * 72)


def print_groups() -> None:
    print("\nSupported ECIES ECDH/XDH groups")
    print("-" * 72)
    for i, group in enumerate(GROUPS, 1):
        aliases = ", ".join(group.aliases)
        print(
            f"{i:2d}. {group.name:10s} family={group.family:24s} "
            f"security≈{group.security_bits:<3d} aliases={aliases}"
        )


def print_group_info(group: ECIESGroup) -> None:
    print("\nECIES Group Parameters")
    print("-" * 72)
    print(f"Group       : {group.name}")
    print(f"Aliases     : {', '.join(group.aliases)}")
    print(f"Family      : {group.family}")
    print(f"Security    : approximately {group.security_bits} bits")
    print(f"Description : {group.description}")
    print(f"Backend     : cryptography {CRYPTOGRAPHY_VERSION} / {openssl_backend.openssl_version_text()}")
    if group.family == FAMILY_EC:
        c = ec_curve_object(group)
        print(f"Curve object : {c.name}, key_size={c.key_size}")
        print("Shared secret: ECDH(d, Q) using short-Weierstrass EC public keys")
    else:
        print("Shared secret: XDH(private, peer_public) using Montgomery u-coordinate keys")
    print(f"KDF         : HKDF-{choose_hkdf_hash(group).name.upper()}")
    print("AEAD        : AES-GCM with 96-bit nonce")


def print_workflow(group: ECIESGroup) -> None:
    print("\nHow ECIES works in this lab")
    print("=" * 72)
    print(f"Selected group: {group.name} ({group.family})")
    print("\nReceiver long-term key pair")
    print("  d_B  = receiver private key")
    print("  Q_B  = d_B * G")
    print("\nEncryption by sender")
    print("  1. Pick fresh ephemeral private key r for this message only.")
    print("  2. Compute ephemeral public key R = r * G.")
    print("  3. Compute shared secret Z = ECDH(r, Q_B).")
    print("  4. Derive AEAD key K = HKDF(Z, salt, info).")
    print("  5. Encrypt plaintext with AES-GCM(K, nonce, AAD).")
    print("  6. Send package: group, R, nonce, salt, info, AAD, ciphertext||tag.")
    print("\nDecryption by receiver")
    print("  1. Parse R from the package.")
    print("  2. Compute Z = ECDH(d_B, R), which matches sender's Z.")
    print("  3. Derive the same K = HKDF(Z, salt, info).")
    print("  4. AES-GCM verifies the tag and decrypts the plaintext.")
    print("\nImportant teaching point")
    print("  The receiver's public key is used for encryption, but only the receiver's")
    print("  private key can recompute the same shared secret and decrypt the package.")


def print_key_pair(private_key, group: ECIESGroup) -> None:
    public_key = private_key.public_key()
    print("\nCurrent receiver key pair")
    print("-" * 72)
    print(f"Group: {group.name}")
    print(f"Private key display ({'scalar' if group.family == FAMILY_EC else 'raw private bytes'}):")
    print(f"  {private_key_raw_or_scalar_hex(private_key, group)}")
    print("Public key:")
    for line in public_key_summary(public_key, group).splitlines():
        print(f"  {line}")


def print_package(package: dict, output_format: str = "json") -> None:
    print("\nECIES ciphertext package")
    print("-" * 72)
    print(encode_package(package, output_format))


def print_encryption_steps(group: ECIESGroup, trace: dict, package: dict) -> None:
    print("\nECIES ENCRYPTION TRACE")
    print("=" * 72)
    print(f"Group: {group.name} ({group.family})")
    print("1. Fresh ephemeral private key r")
    print(f"   r = {trace['ephemeral_private']}")
    print("2. Ephemeral public key R = r*G")
    print(f"   R encoded = {trace['ephemeral_public_hex']}")
    print("3. ECDH/XDH shared secret Z = r*Q_B")
    print(f"   Z = {trace['shared_secret_hex']}")
    print("4. HKDF derives AES-GCM key K")
    print(f"   K = {trace['derived_aead_key_hex']}")
    print("5. AES-GCM encryption")
    print(f"   nonce = {trace['nonce_hex']}")
    print(f"   AAD   = {trace['aad_hex'] or '(empty)'}")
    print(f"   C||T  = {trace['ciphertext_tag_hex']}")
    print("6. Package includes R, nonce, salt, info, AAD, and ciphertext||tag")
    print(f"   package.group = {package['group']}")


def print_decryption_steps(group: ECIESGroup, trace: dict) -> None:
    print("\nECIES DECRYPTION TRACE")
    print("=" * 72)
    print(f"Group: {group.name} ({group.family})")
    print("1. Parse ephemeral public key R from package")
    print(f"   R encoded = {trace['ephemeral_public_hex']}")
    print("2. Receiver recomputes shared secret Z = d_B*R")
    print(f"   Z = {trace['shared_secret_hex']}")
    print("3. HKDF derives the same AES-GCM key K")
    print(f"   K = {trace['derived_aead_key_hex']}")
    print("4. AES-GCM verifies tag and decrypts")
    print(f"   nonce = {trace['nonce_hex']}")
    print(f"   C||T  = {trace['ciphertext_tag_hex']}")
    print(f"   P     = {trace['plaintext_hex']}")


# ============================================================
# INTERACTIVE MENU
# ============================================================


@dataclass
class LabState:
    group: ECIESGroup = GROUPS[0]
    receiver_private_key: object = None
    peer_public_key: object = None
    last_package: Optional[dict] = None
    last_package_format: str = "json"

    @property
    def receiver_public_key(self):
        return None if self.receiver_private_key is None else self.receiver_private_key.public_key()


def input_default(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value if value else default


def select_group_interactive(state: LabState) -> None:
    print_groups()
    choice = input_default("Select group by number or name", state.group.name)
    try:
        if choice.isdigit():
            idx = int(choice) - 1
            if idx < 0 or idx >= len(GROUPS):
                raise ValueError("group number out of range")
            state.group = GROUPS[idx]
        else:
            state.group = parse_group(choice)
        # Public keys and ciphertext packages are group-specific.
        state.receiver_private_key = None
        state.peer_public_key = None
        state.last_package = None
        print(f"Loaded group: {state.group.name}")
    except Exception as exc:
        print(f"error: {exc}")


def generate_key_pair_interactive(state: LabState) -> None:
    state.receiver_private_key = generate_private_key(state.group)
    state.peer_public_key = state.receiver_public_key
    print_key_pair(state.receiver_private_key, state.group)
    save = input_default("Save receiver key pair to files? (y/n)", "n").lower()
    if save == "y":
        priv_path = input_default("Private key output", f"ecies_{state.group.name}_receiver_private.pem")
        pub_path = input_default("Public key output", f"ecies_{state.group.name}_receiver_public.pem")
        raw_path = input_default("Raw exchange public key output", f"ecies_{state.group.name}_receiver_public.raw")
        password = input_default("Private key password, empty for none", "")
        Path(priv_path).write_bytes(private_key_to_pem(state.receiver_private_key, password or None))
        Path(pub_path).write_bytes(public_key_to_pem(state.receiver_public_key))
        Path(raw_path).write_bytes(public_key_to_exchange_bytes(state.receiver_public_key, state.group))
        print(f"Saved private key: {priv_path}")
        print(f"Saved public key : {pub_path}")
        print(f"Saved raw public : {raw_path}")


def enter_public_key_interactive(state: LabState) -> None:
    print("\nEnter recipient public key")
    print("1. Use current receiver public key")
    print("2. Load PEM/raw public key from file")
    print("3. Paste raw exchange public key as hex")
    choice = input_default("Select", "1")
    try:
        if choice == "1":
            if state.receiver_public_key is None:
                print("No current receiver key pair. Generate key pair first.")
                return
            state.peer_public_key = state.receiver_public_key
        elif choice == "2":
            path = input_default("Public key file")
            state.peer_public_key = load_public_exchange_bytes(path, state.group)
        elif choice == "3":
            raw_hex = input_default("Raw public key hex")
            state.peer_public_key = public_key_from_exchange_bytes(bytes.fromhex(raw_hex), state.group)
        else:
            print("Invalid selection")
            return
        print("Loaded recipient public key:")
        print(public_key_summary(state.peer_public_key, state.group))
    except Exception as exc:
        print(f"error: {exc}")


def encrypt_interactive(state: LabState) -> None:
    if state.peer_public_key is None:
        if state.receiver_public_key is not None:
            state.peer_public_key = state.receiver_public_key
        else:
            print("No recipient public key. Generate or enter a public key first.")
            return
    msg = input("Plaintext message: ").encode("utf-8")
    aad = input_default("AAD text, empty for none", "").encode("utf-8")
    info = input_default("HKDF info", "ECIES lab v2").encode("utf-8")
    salt_text = input_default("HKDF salt text, empty for none", "")
    salt = salt_text.encode("utf-8") if salt_text else b""
    key_len = int(input_default("AES-GCM key length in bytes", "32"))
    output_format = input_default("Package format: json/base64/hex", "json").lower()
    show_steps = input_default("Show internal ECIES steps? (y/n)", "y").lower() == "y"
    try:
        state.last_package, _ = ecies_encrypt(
            msg,
            state.peer_public_key,
            state.group,
            aad=aad,
            salt=salt,
            info=info,
            key_len=key_len,
            show_steps=show_steps,
        )
        state.last_package_format = output_format
        print_package(state.last_package, output_format)
        save = input_default("Save package to file? (y/n)", "n").lower()
        if save == "y":
            path = input_default("Package output", "ecies_cipher_package.txt")
            Path(path).write_text(encode_package(state.last_package, output_format), encoding="utf-8")
            print(f"Saved package: {path}")
    except Exception as exc:
        print(f"error: {exc}")


def decrypt_interactive(state: LabState) -> None:
    if state.receiver_private_key is None:
        print("No receiver private key. Generate one or load one first.")
        load = input_default("Load private key from PEM? (y/n)", "n").lower()
        if load != "y":
            return
        try:
            path = input_default("Private key PEM file")
            password = input_default("Password, empty for none", "")
            state.receiver_private_key = load_private_key(path, password or None)
        except Exception as exc:
            print(f"error: {exc}")
            return

    print("\nCiphertext package source")
    print("1. Use last ciphertext package")
    print("2. Load from file")
    print("3. Paste package text")
    choice = input_default("Select", "1")
    try:
        if choice == "1":
            if not state.last_package:
                print("No last package available.")
                return
            package = state.last_package
        elif choice == "2":
            path = input_default("Package file")
            package_format = input_default("Package format: json/base64/hex", state.last_package_format).lower()
            package = decode_package(Path(path).read_text(encoding="utf-8"), package_format)
        elif choice == "3":
            package_format = input_default("Package format: json/base64/hex", state.last_package_format).lower()
            encoded = input("Paste package: ").strip()
            package = decode_package(encoded, package_format)
        else:
            print("Invalid selection")
            return

        show_steps = input_default("Show internal ECIES steps? (y/n)", "y").lower() == "y"
        plaintext, _ = ecies_decrypt(package, state.receiver_private_key, show_steps=show_steps)
        print(f"\nDecrypted plaintext: {plaintext.decode('utf-8', errors='replace')}")
    except InvalidTag:
        print("error: AES-GCM authentication failed. Wrong key, tampered package, wrong AAD/info/salt, or wrong group.")
    except Exception as exc:
        print(f"error: {exc}")


def show_package_interactive(state: LabState) -> None:
    if not state.last_package:
        print("No ciphertext package yet.")
        return
    output_format = input_default("Package format: json/base64/hex", state.last_package_format).lower()
    print_package(state.last_package, output_format)


def client_server_demo(group: ECIESGroup, show_steps: bool = True) -> None:
    print("\nECIES Client/Server Demo")
    print("=" * 72)
    print("Server/receiver generates long-term key pair.")
    server_private = generate_private_key(group)
    server_public = server_private.public_key()
    print("Server public key distributed to client:")
    print(public_key_summary(server_public, group))

    message = b"Hello from client using ECIES."
    aad = b"course=cryptography;lab=ECIES"
    info = b"ECIES client/server demo"
    salt = b"demo-salt"

    print("\nClient encrypts with server public key...")
    package, enc_trace = ecies_encrypt(
        message,
        server_public,
        group,
        aad=aad,
        salt=salt,
        info=info,
        show_steps=show_steps,
    )
    print_package(package, "json")

    print("\nServer decrypts with server private key...")
    plaintext, dec_trace = ecies_decrypt(package, server_private, show_steps=show_steps)
    print(f"\nShared secret matches: {enc_trace['shared_secret_hex'] == dec_trace['shared_secret_hex']}")
    print(f"Derived key matches : {enc_trace['derived_aead_key_hex'] == dec_trace['derived_aead_key_hex']}")
    print(f"Plaintext recovered : {plaintext.decode('utf-8')}")


def menu_loop() -> None:
    state = LabState()
    while True:
        print("\n=== ECIES LAB ===")
        print(f"Current group: {state.group.name} ({state.group.family})")
        print("1. Load ECIES ECDH/XDH Group")
        print("2. Show How ECIES Works")
        print("3. Generate Receiver Key Pair")
        print("4. Show Parameters")
        print("5. Show Receiver Key Pair")
        print("6. Enter / Load Recipient Public Key")
        print("7. Encrypt Message")
        print("8. Show Ciphertext Package")
        print("9. Decrypt Ciphertext")
        print("10. Client/Server Demo")
        print("11. List ECIES Groups")
        print("0. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            select_group_interactive(state)
        elif choice == "2":
            print_workflow(state.group)
        elif choice == "3":
            generate_key_pair_interactive(state)
        elif choice == "4":
            print_group_info(state.group)
        elif choice == "5":
            if state.receiver_private_key is None:
                print("No receiver key pair. Generate key pair first.")
            else:
                print_key_pair(state.receiver_private_key, state.group)
        elif choice == "6":
            enter_public_key_interactive(state)
        elif choice == "7":
            encrypt_interactive(state)
        elif choice == "8":
            show_package_interactive(state)
        elif choice == "9":
            decrypt_interactive(state)
        elif choice == "10":
            client_server_demo(state.group, show_steps=True)
        elif choice == "11":
            print_groups()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")


# ============================================================
# ARGPARSE SUBCOMMANDS
# ============================================================


def read_bytes_from_args(args: argparse.Namespace) -> bytes:
    if getattr(args, "message_file", None):
        return Path(args.message_file).read_bytes()
    if getattr(args, "message_hex", None):
        return bytes.fromhex(args.message_hex)
    return (getattr(args, "message", None) or "").encode("utf-8")


def add_message_options(parser: argparse.ArgumentParser) -> None:
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--message", help="UTF-8 plaintext message")
    g.add_argument("--message-file", help="plaintext file")
    g.add_argument("--message-hex", help="hex-encoded plaintext bytes")


def cmd_list_groups(_: argparse.Namespace) -> int:
    print_groups()
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    print_group_info(args.group)
    return 0


def cmd_workflow(args: argparse.Namespace) -> int:
    print_workflow(args.group)
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    private_key = generate_private_key(args.group)
    public_key = private_key.public_key()
    Path(args.private_out).write_bytes(private_key_to_pem(private_key, args.password))
    Path(args.public_out).write_bytes(public_key_to_pem(public_key))
    if args.public_raw_out:
        Path(args.public_raw_out).write_bytes(public_key_to_exchange_bytes(public_key, args.group))
    print(f"Private key written: {args.private_out}")
    print(f"Public key written : {args.public_out}")
    if args.public_raw_out:
        print(f"Raw public written : {args.public_raw_out}")
    if args.print_key:
        print_key_pair(private_key, args.group)
    return 0


def cmd_encrypt(args: argparse.Namespace) -> int:
    public_key = load_public_exchange_bytes(args.public_key, args.group)
    package, _ = ecies_encrypt(
        read_bytes_from_args(args),
        public_key,
        args.group,
        aad=args.aad.encode("utf-8") if args.aad else b"",
        salt=args.salt.encode("utf-8") if args.salt else b"",
        info=args.info.encode("utf-8"),
        key_len=args.key_len,
        show_steps=args.show_steps,
    )
    encoded = encode_package(package, args.format)
    if args.out:
        Path(args.out).write_text(encoded, encoding="utf-8")
        print(f"Ciphertext package written: {args.out}")
    else:
        print(encoded)
    return 0


def cmd_decrypt(args: argparse.Namespace) -> int:
    private_key = load_private_key(args.private_key, args.password)
    encoded = Path(args.package).read_text(encoding="utf-8") if args.package else args.package_text
    if not encoded:
        raise ValueError("provide --package or --package-text")
    package = decode_package(encoded, args.format)
    plaintext, _ = ecies_decrypt(package, private_key, show_steps=args.show_steps)
    if args.out:
        Path(args.out).write_bytes(plaintext)
        print(f"Plaintext written: {args.out}")
    else:
        print(plaintext.decode("utf-8", errors="replace"))
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    client_server_demo(args.group, show_steps=args.show_steps)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ECIES lab with numbered menu and CLI subcommands.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--group", type=parse_group, default=GROUPS[0], help="ECIES ECDH/XDH group")
    sub = parser.add_subparsers(dest="task")

    p = sub.add_parser("list-groups", help="list supported ECIES groups")
    p.set_defaults(func=cmd_list_groups)

    p = sub.add_parser("info", help="show selected group parameters")
    p.set_defaults(func=cmd_info)

    p = sub.add_parser("workflow", help="show ECIES step-by-step workflow")
    p.set_defaults(func=cmd_workflow)

    p = sub.add_parser("generate", help="generate receiver key pair")
    p.add_argument("--private-out", default="ecies_receiver_private.pem")
    p.add_argument("--public-out", default="ecies_receiver_public.pem")
    p.add_argument("--public-raw-out", default="ecies_receiver_public.raw")
    p.add_argument("--password", help="optional password for private key PEM")
    p.add_argument("--print-key", action="store_true", help="print private/public values for teaching")
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("encrypt", help="encrypt with recipient public key")
    p.add_argument("--public-key", required=True, help="recipient public key PEM/raw/hex file")
    add_message_options(p)
    p.add_argument("--aad", default="", help="AES-GCM associated data text")
    p.add_argument("--salt", default="", help="HKDF salt text")
    p.add_argument("--info", default="ECIES lab v2", help="HKDF info/context text")
    p.add_argument("--key-len", type=int, default=32, help="AEAD key length in bytes")
    p.add_argument("--format", choices=("json", "base64", "hex"), default="json")
    p.add_argument("--out", help="ciphertext package output file")
    p.add_argument("--show-steps", action="store_true", help="print ECIES internal values")
    p.set_defaults(func=cmd_encrypt)

    p = sub.add_parser("decrypt", help="decrypt with receiver private key")
    p.add_argument("--private-key", required=True, help="receiver private key PEM")
    p.add_argument("--password", help="private key password if encrypted")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--package", help="ciphertext package file")
    src.add_argument("--package-text", help="ciphertext package text")
    p.add_argument("--format", choices=("json", "base64", "hex"), default="json")
    p.add_argument("--out", help="plaintext output file")
    p.add_argument("--show-steps", action="store_true", help="print ECIES internal values")
    p.set_defaults(func=cmd_decrypt)

    p = sub.add_parser("demo", help="run full client/server demo")
    p.add_argument("--show-steps", action="store_true", help="print internal ECIES values")
    p.set_defaults(func=cmd_demo)

    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    argv_list = list(sys.argv[1:] if argv is None else argv)
    if not argv_list:
        menu_loop()
        return 0

    parser = build_parser()
    args = parser.parse_args(argv_list)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    try:
        return int(args.func(args) or 0)
    except InvalidTag:
        print("error: AES-GCM authentication failed", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
