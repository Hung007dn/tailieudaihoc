#!/usr/bin/env python3
"""
ECDHE_lab_menu_v2.py

ECDHE lab CLI using OpenSSL-backed pyca/cryptography.

Version: v2-ffdhe-style-menu-cli

Goal
----
This file supports both an FFDHE-style interactive numbered lab menu
and a scriptable CLI workflow:

    list-groups -> info -> generate -> public -> validate-peer -> derive -> demo

The CLI deliberately calls elliptic-curve choices "groups", because that is how
TLS 1.3 and FFDHE labs normally discuss key-exchange parameter negotiation.

Supported ECDHE/XDH groups
--------------------------
Short-Weierstrass ECDHE groups:
    secp256r1 / p-256 / prime256v1
    secp384r1 / p-384
    secp521r1 / p-521
    secp256k1

Montgomery XDH groups:
    x25519 / curve25519
    x448 / curve448

Important security notes
------------------------
1. This is a teaching/lab script. It uses cryptography/OpenSSL primitives, but
   the file prints intermediate values for learning.
2. ECDHE means ephemeral ECDH. In real protocols, generate a fresh private key
   for every handshake/session.
3. Do not use Ed25519/Ed448 signing keys for ECDH. For Curve25519/Curve448
   key agreement, use X25519/X448.
4. The raw ECDH shared secret is not a symmetric key. Derive a session key with
   a KDF such as HKDF.

Example commands
----------------
    python ECDHE_lab_menu_v2.py list-groups
    python ECDHE_lab_menu_v2.py --group secp256r1 info
    python ECDHE_lab_menu_v2.py --group x25519 info

    python ECDHE_lab_menu_v2.py --group secp256r1 generate \
        --private-out alice_priv.pem --public-out alice_pub.pem
    python ECDHE_lab_menu_v2.py --group secp256r1 generate \
        --private-out bob_priv.pem --public-out bob_pub.pem

    python ECDHE_lab_menu_v2.py --group secp256r1 validate-peer \
        --public bob_pub.pem
    python ECDHE_lab_menu_v2.py --group secp256r1 derive \
        --private alice_priv.pem --peer-public bob_pub.pem \
        --key-len 32 --info "NT219 ECDHE lab"

    python ECDHE_lab_menu_v2.py --group x25519 demo
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple


# ============================================================
# CRYPTOGRAPHY / OPENSSL LOADING
# ============================================================


def require_cryptography():
    """Import pyca/cryptography lazily and give a clear error if missing."""
    try:
        import cryptography
        from cryptography.hazmat.bindings.openssl.binding import Binding
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec, x25519, x448
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    except Exception as exc:  # pragma: no cover - environment diagnostic path.
        raise RuntimeError(
            "This ECDHE CLI requires pyca/cryptography. Install it with:\n"
            "  python -m pip install cryptography"
        ) from exc

    return {
        "cryptography": cryptography,
        "Binding": Binding,
        "hashes": hashes,
        "serialization": serialization,
        "ec": ec,
        "x25519": x25519,
        "x448": x448,
        "HKDF": HKDF,
    }


# ============================================================
# GROUP DEFINITIONS
# ============================================================


FAMILY_EC = "short-weierstrass-ecdh"
FAMILY_X25519 = "x25519"
FAMILY_X448 = "x448"


@dataclass(frozen=True)
class ECDHEGroup:
    name: str
    aliases: Tuple[str, ...]
    family: str
    bits: int
    security_bits: int
    openssl_name: str
    equation: str
    generator_note: str
    kdf_hash: str
    description: str


GROUPS: Tuple[ECDHEGroup, ...] = (
    ECDHEGroup(
        name="secp256r1",
        aliases=("p-256", "p256", "prime256v1", "nistp256", "nist-p256"),
        family=FAMILY_EC,
        bits=256,
        security_bits=128,
        openssl_name="secp256r1",
        equation="y^2 = x^3 - 3*x + b over F_p",
        generator_note="Generator G is the standard NIST P-256 base point.",
        kdf_hash="sha256",
        description="NIST P-256 / prime256v1 short-Weierstrass ECDHE group.",
    ),
    ECDHEGroup(
        name="secp384r1",
        aliases=("p-384", "p384", "nistp384", "nist-p384"),
        family=FAMILY_EC,
        bits=384,
        security_bits=192,
        openssl_name="secp384r1",
        equation="y^2 = x^3 - 3*x + b over F_p",
        generator_note="Generator G is the standard NIST P-384 base point.",
        kdf_hash="sha384",
        description="NIST P-384 short-Weierstrass ECDHE group.",
    ),
    ECDHEGroup(
        name="secp521r1",
        aliases=("p-521", "p521", "nistp521", "nist-p521"),
        family=FAMILY_EC,
        bits=521,
        security_bits=256,
        openssl_name="secp521r1",
        equation="y^2 = x^3 - 3*x + b over F_p",
        generator_note="Generator G is the standard NIST P-521 base point.",
        kdf_hash="sha512",
        description="NIST P-521 short-Weierstrass ECDHE group.",
    ),
    ECDHEGroup(
        name="secp256k1",
        aliases=("k-256", "k256", "bitcoin"),
        family=FAMILY_EC,
        bits=256,
        security_bits=128,
        openssl_name="secp256k1",
        equation="y^2 = x^3 + 7 over F_p",
        generator_note="Generator G is the SEC2 secp256k1 base point.",
        kdf_hash="sha256",
        description="Koblitz-style short-Weierstrass curve used by Bitcoin; not a common TLS ECDHE default.",
    ),
    ECDHEGroup(
        name="x25519",
        aliases=("curve25519", "curve-25519", "montgomery25519"),
        family=FAMILY_X25519,
        bits=255,
        security_bits=128,
        openssl_name="X25519",
        equation="v^2 = u^3 + 486662*u^2 + u over F_p, p = 2^255 - 19",
        generator_note="X25519 uses the Montgomery u-coordinate base point u = 9.",
        kdf_hash="sha256",
        description="Montgomery XDH group. Public keys are 32-byte u-coordinates.",
    ),
    ECDHEGroup(
        name="x448",
        aliases=("curve448", "curve-448", "montgomery448"),
        family=FAMILY_X448,
        bits=448,
        security_bits=224,
        openssl_name="X448",
        equation="v^2 = u^3 + 156326*u^2 + u over F_p, p = 2^448 - 2^224 - 1",
        generator_note="X448 uses the Montgomery u-coordinate base point u = 5.",
        kdf_hash="sha512",
        description="Montgomery XDH group. Public keys are 56-byte u-coordinates.",
    ),
)


def _key(text: str) -> str:
    return text.strip().lower().replace("_", "-")


GROUP_LOOKUP: Dict[str, ECDHEGroup] = {}
for _group in GROUPS:
    GROUP_LOOKUP[_key(_group.name)] = _group
    for _alias in _group.aliases:
        GROUP_LOOKUP[_key(_alias)] = _group


# ============================================================
# GENERIC UTILITIES
# ============================================================


def parse_group(text: str) -> ECDHEGroup:
    try:
        return GROUP_LOOKUP[_key(text)]
    except KeyError as exc:
        known = ", ".join(g.name for g in GROUPS)
        raise argparse.ArgumentTypeError(
            f"unknown ECDHE group {text!r}; supported groups: {known}"
        ) from exc


def bytes_to_hex(data: bytes) -> str:
    return data.hex()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_or_print(data: bytes, output: Optional[str], label: str, *, as_hex: bool = True) -> None:
    if output:
        Path(output).write_bytes(data)
        print(f"{label} written to: {output}")
    else:
        if as_hex:
            print(f"{label}.hex = {data.hex()}")
        else:
            print(data.decode("utf-8", errors="replace"))


def read_bytes(path: str) -> bytes:
    return Path(path).read_bytes()


def parse_hex_or_text(hex_value: Optional[str], text_value: Optional[str], label: str) -> Optional[bytes]:
    if hex_value is not None and text_value is not None:
        raise ValueError(f"use either --{label}-hex or --{label}, not both")
    if hex_value is not None:
        try:
            return bytes.fromhex(hex_value)
        except ValueError as exc:
            raise ValueError(f"invalid {label} hex") from exc
    if text_value is not None:
        return text_value.encode("utf-8")
    return None


# ============================================================
# GROUP-TO-OPENSSL OBJECT MAPPING
# ============================================================


def ec_curve_object(group: ECDHEGroup):
    d = require_cryptography()
    ec = d["ec"]
    mapping = {
        "secp256r1": ec.SECP256R1,
        "secp384r1": ec.SECP384R1,
        "secp521r1": ec.SECP521R1,
        "secp256k1": ec.SECP256K1,
    }
    if group.family != FAMILY_EC:
        raise RuntimeError(f"group {group.name} is {group.family}, not short-Weierstrass EC")
    try:
        return mapping[group.openssl_name]()
    except KeyError as exc:
        raise RuntimeError(f"no EC curve mapping for {group.name}") from exc


def generate_private_key(group: ECDHEGroup):
    d = require_cryptography()
    if group.family == FAMILY_EC:
        return d["ec"].generate_private_key(ec_curve_object(group))
    if group.family == FAMILY_X25519:
        return d["x25519"].X25519PrivateKey.generate()
    if group.family == FAMILY_X448:
        return d["x448"].X448PrivateKey.generate()
    raise RuntimeError(f"unsupported group family {group.family}")


def is_private_key_for_group(private_key, group: ECDHEGroup) -> bool:
    d = require_cryptography()
    ec = d["ec"]
    x25519 = d["x25519"]
    x448 = d["x448"]

    if group.family == FAMILY_EC:
        return isinstance(private_key, ec.EllipticCurvePrivateKey) and private_key.curve.name == group.openssl_name
    if group.family == FAMILY_X25519:
        return isinstance(private_key, x25519.X25519PrivateKey)
    if group.family == FAMILY_X448:
        return isinstance(private_key, x448.X448PrivateKey)
    return False


def is_public_key_for_group(public_key, group: ECDHEGroup) -> bool:
    d = require_cryptography()
    ec = d["ec"]
    x25519 = d["x25519"]
    x448 = d["x448"]

    if group.family == FAMILY_EC:
        return isinstance(public_key, ec.EllipticCurvePublicKey) and public_key.curve.name == group.openssl_name
    if group.family == FAMILY_X25519:
        return isinstance(public_key, x25519.X25519PublicKey)
    if group.family == FAMILY_X448:
        return isinstance(public_key, x448.X448PublicKey)
    return False


def load_password(password: Optional[str]) -> Optional[bytes]:
    if password is None:
        return None
    return password.encode("utf-8")


def load_private_key(path: str, group: ECDHEGroup, password: Optional[str] = None):
    d = require_cryptography()
    serialization = d["serialization"]
    key = serialization.load_pem_private_key(read_bytes(path), password=load_password(password))
    if not is_private_key_for_group(key, group):
        actual = describe_private_key_type(key)
        raise ValueError(f"private key in {path!r} does not match group {group.name}; actual: {actual}")
    return key


def load_public_key_auto(
    path: str,
    group: ECDHEGroup,
    *,
    public_format: str = "auto",
):
    data = read_bytes(path)
    return load_public_key_bytes_auto(data, group, public_format=public_format, source=path)


def load_public_key_bytes_auto(
    data: bytes,
    group: ECDHEGroup,
    *,
    public_format: str = "auto",
    source: str = "input",
):
    d = require_cryptography()
    serialization = d["serialization"]

    fmt = public_format.lower()
    if fmt not in {"auto", "pem", "raw", "x962"}:
        raise ValueError("public format must be auto, pem, raw, or x962")

    is_pem = data.lstrip().startswith(b"-----BEGIN")
    if fmt == "pem" or (fmt == "auto" and is_pem):
        key = serialization.load_pem_public_key(data)
    else:
        key = load_raw_public_key(data, group)

    if not is_public_key_for_group(key, group):
        actual = describe_public_key_type(key)
        raise ValueError(f"public key from {source!r} does not match group {group.name}; actual: {actual}")
    return key


def load_raw_public_key(data: bytes, group: ECDHEGroup):
    d = require_cryptography()
    ec = d["ec"]
    x25519 = d["x25519"]
    x448 = d["x448"]

    if group.family == FAMILY_EC:
        # SEC1/X9.62 uncompressed point: 0x04 || x || y.
        return ec.EllipticCurvePublicKey.from_encoded_point(ec_curve_object(group), data)
    if group.family == FAMILY_X25519:
        return x25519.X25519PublicKey.from_public_bytes(data)
    if group.family == FAMILY_X448:
        return x448.X448PublicKey.from_public_bytes(data)
    raise RuntimeError(f"unsupported group family {group.family}")




def ecdh_exchange(private_key, peer_public_key, group: ECDHEGroup) -> bytes:
    """Compute ECDH/XDH shared secret with the correct API for the group."""
    if group.family == FAMILY_EC:
        ec = require_cryptography()["ec"]
        return private_key.exchange(ec.ECDH(), peer_public_key)
    if group.family in {FAMILY_X25519, FAMILY_X448}:
        return private_key.exchange(peer_public_key)
    raise RuntimeError(f"unsupported group family {group.family}")

def describe_private_key_type(private_key) -> str:
    d = require_cryptography()
    ec = d["ec"]
    x25519 = d["x25519"]
    x448 = d["x448"]
    if isinstance(private_key, ec.EllipticCurvePrivateKey):
        return f"EC private key on {private_key.curve.name}"
    if isinstance(private_key, x25519.X25519PrivateKey):
        return "X25519 private key"
    if isinstance(private_key, x448.X448PrivateKey):
        return "X448 private key"
    return type(private_key).__name__


def describe_public_key_type(public_key) -> str:
    d = require_cryptography()
    ec = d["ec"]
    x25519 = d["x25519"]
    x448 = d["x448"]
    if isinstance(public_key, ec.EllipticCurvePublicKey):
        return f"EC public key on {public_key.curve.name}"
    if isinstance(public_key, x25519.X25519PublicKey):
        return "X25519 public key"
    if isinstance(public_key, x448.X448PublicKey):
        return "X448 public key"
    return type(public_key).__name__


# ============================================================
# SERIALIZATION HELPERS
# ============================================================


def private_key_to_pem(private_key, password: Optional[str]) -> bytes:
    serialization = require_cryptography()["serialization"]
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
    serialization = require_cryptography()["serialization"]
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def public_key_to_raw(public_key, group: ECDHEGroup) -> bytes:
    d = require_cryptography()
    serialization = d["serialization"]
    ec = d["ec"]

    if group.family == FAMILY_EC:
        if not isinstance(public_key, ec.EllipticCurvePublicKey):
            raise ValueError("expected EC public key")
        return public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint,
        )

    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def private_key_scalar_hex(private_key, group: ECDHEGroup) -> Optional[str]:
    """Return the EC private scalar for short-Weierstrass keys only.

    X25519/X448 private scalars are intentionally not exposed by this helper.
    Their byte encodings include protocol-specific clamping, so printing them as
    a simple scalar would be misleading for students.
    """
    d = require_cryptography()
    ec = d["ec"]
    if group.family == FAMILY_EC and isinstance(private_key, ec.EllipticCurvePrivateKey):
        return hex(private_key.private_numbers().private_value)
    return None


def public_key_coordinates(public_key, group: ECDHEGroup) -> Optional[Tuple[int, int]]:
    d = require_cryptography()
    ec = d["ec"]
    if group.family == FAMILY_EC and isinstance(public_key, ec.EllipticCurvePublicKey):
        nums = public_key.public_numbers()
        return nums.x, nums.y
    return None


# ============================================================
# KDF HELPERS
# ============================================================


def hash_algorithm(name: str, group: ECDHEGroup):
    hashes = require_cryptography()["hashes"]
    normalized = group.kdf_hash if name == "auto" else name.lower().replace("-", "")
    if normalized == "sha256":
        return hashes.SHA256()
    if normalized == "sha384":
        return hashes.SHA384()
    if normalized == "sha512":
        return hashes.SHA512()
    raise ValueError("supported hashes: auto, sha256, sha384, sha512")


def hkdf_derive(
    shared_secret: bytes,
    group: ECDHEGroup,
    *,
    key_len: int,
    hash_name: str,
    salt: Optional[bytes],
    info: bytes,
) -> bytes:
    HKDF = require_cryptography()["HKDF"]
    return HKDF(
        algorithm=hash_algorithm(hash_name, group),
        length=key_len,
        salt=salt,
        info=info,
    ).derive(shared_secret)


# ============================================================
# COMMAND HANDLERS
# ============================================================


def cmd_openssl_info(_: argparse.Namespace) -> int:
    d = require_cryptography()
    binding = d["Binding"]()
    openssl_version = d["Binding"].ffi.string(
        binding.lib.OpenSSL_version(0)
    ).decode("ascii", errors="replace")
    print(f"cryptography version: {d['cryptography'].__version__}")
    print(f"OpenSSL version: {openssl_version}")
    return 0


def cmd_list_groups(_: argparse.Namespace) -> int:
    print("Supported ECDHE/XDH groups")
    print("-" * 96)
    for group in GROUPS:
        aliases = ", ".join(group.aliases)
        print(
            f"{group.name:10s} family={group.family:24s} "
            f"bits={group.bits:<3d} security≈{group.security_bits:<3d} "
            f"openssl={group.openssl_name:10s} aliases={aliases}"
        )
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    group = args.group
    print("Script: ECDHE_lab_menu_v2.py")
    print("Version: v2-ffdhe-style-menu-cli")
    print(f"Group: {group.name}")
    print(f"Family: {group.family}")
    print(f"OpenSSL name: {group.openssl_name}")
    print(f"Aliases: {', '.join(group.aliases)}")
    print(f"Field/key size: {group.bits} bit(s)")
    print(f"Approximate classical security: {group.security_bits} bit(s)")
    print(f"Equation/model: {group.equation}")
    print(f"Generator/base point: {group.generator_note}")
    print(f"Default HKDF hash: {group.kdf_hash}")
    print(f"Description: {group.description}")
    print()
    print("ECDHE relation:")
    print("  Alice: private a, public A = a*G")
    print("  Bob:   private b, public B = b*G")
    print("  Alice computes Z_A = a*B = a*b*G")
    print("  Bob computes   Z_B = b*A = b*a*G")
    print("  Z_A == Z_B, then HKDF(Z, salt, info) derives the session key")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    group = args.group
    private_key = generate_private_key(group)
    public_key = private_key.public_key()

    private_pem = private_key_to_pem(private_key, args.password)
    public_pem = public_key_to_pem(public_key)
    public_raw = public_key_to_raw(public_key, group)

    Path(args.private_out).write_bytes(private_pem)
    Path(args.public_out).write_bytes(public_pem)
    print(f"Group: {group.name}")
    print(f"Private key PEM written to: {args.private_out}")
    print(f"Public key PEM written to: {args.public_out}")

    if args.public_raw_out:
        Path(args.public_raw_out).write_bytes(public_raw)
        print(f"Raw public key written to: {args.public_raw_out}")

    if args.print_public:
        print(f"public.raw.hex = {public_raw.hex()}")
        coords = public_key_coordinates(public_key, group)
        if coords:
            x, y = coords
            print(f"public.x = {hex(x)}")
            print(f"public.y = {hex(y)}")

    if args.print_private_scalar:
        scalar = private_key_scalar_hex(private_key, group)
        if scalar is None:
            print("private scalar: not printed for X25519/X448 because the raw private bytes are clamped protocol input")
        else:
            print(f"private.scalar = {scalar}")

    return 0


def cmd_public(args: argparse.Namespace) -> int:
    group = args.group
    private_key = load_private_key(args.private, group, args.password)
    public_key = private_key.public_key()

    if args.public_out:
        Path(args.public_out).write_bytes(public_key_to_pem(public_key))
        print(f"Public key PEM written to: {args.public_out}")

    raw = public_key_to_raw(public_key, group)
    if args.raw_out:
        Path(args.raw_out).write_bytes(raw)
        print(f"Raw public key written to: {args.raw_out}")
    else:
        print(f"public.raw.hex = {raw.hex()}")

    coords = public_key_coordinates(public_key, group)
    if coords:
        x, y = coords
        print(f"public.x = {hex(x)}")
        print(f"public.y = {hex(y)}")
    return 0


def cmd_validate_peer(args: argparse.Namespace) -> int:
    group = args.group
    public_key = load_public_key_auto(args.public, group, public_format=args.public_format)
    raw = public_key_to_raw(public_key, group)
    print("Peer public key valid: True")
    print(f"Group: {group.name}")
    print(f"Detected type: {describe_public_key_type(public_key)}")
    print(f"Raw public length: {len(raw)} byte(s)")
    print(f"Raw public SHA-256: {sha256_hex(raw)}")
    coords = public_key_coordinates(public_key, group)
    if coords:
        x, y = coords
        print(f"public.x = {hex(x)}")
        print(f"public.y = {hex(y)}")
    return 0


def cmd_derive(args: argparse.Namespace) -> int:
    group = args.group
    private_key = load_private_key(args.private, group, args.password)

    if args.peer_public_hex:
        try:
            peer_bytes = bytes.fromhex(args.peer_public_hex)
        except ValueError as exc:
            raise ValueError("invalid --peer-public-hex") from exc
        peer_public = load_public_key_bytes_auto(
            peer_bytes, group, public_format="raw", source="--peer-public-hex"
        )
    else:
        peer_public = load_public_key_auto(args.peer_public, group, public_format=args.peer_public_format)

    shared = ecdh_exchange(private_key, peer_public, group)
    print(f"Group: {group.name}")
    print(f"Shared secret length: {len(shared)} byte(s)")
    print(f"Shared secret SHA-256: {sha256_hex(shared)}")
    write_or_print(shared, args.shared_out, "shared_secret", as_hex=True)

    if not args.no_kdf:
        salt = parse_hex_or_text(args.salt_hex, args.salt, "salt")
        info = (args.info or "ecdhe-lab").encode("utf-8")
        derived = hkdf_derive(
            shared,
            group,
            key_len=args.key_len,
            hash_name=args.hash,
            salt=salt,
            info=info,
        )
        print(f"HKDF hash: {group.kdf_hash if args.hash == 'auto' else args.hash}")
        print(f"HKDF info: {(args.info or 'ecdhe-lab')!r}")
        if salt is None:
            print("HKDF salt: None")
        else:
            print(f"HKDF salt.hex = {salt.hex()}")
        write_or_print(derived, args.key_out, f"hkdf_key_{args.key_len}_bytes", as_hex=True)

    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    group = args.group
    alice_private = generate_private_key(group)
    bob_private = generate_private_key(group)
    alice_public = alice_private.public_key()
    bob_public = bob_private.public_key()

    alice_shared = ecdh_exchange(alice_private, bob_public, group)
    bob_shared = ecdh_exchange(bob_private, alice_public, group)

    print("=" * 76)
    print(f"ECDHE demo: {group.name} ({group.family})")
    print("=" * 76)
    print("Step 1: negotiate group")
    print(f"  group = {group.name}")
    print(f"  model = {group.equation}")
    print()
    print("Step 2: generate ephemeral keys")
    print(f"  Alice public.raw.hex = {public_key_to_raw(alice_public, group).hex()}")
    print(f"  Bob   public.raw.hex = {public_key_to_raw(bob_public, group).hex()}")

    alice_coords = public_key_coordinates(alice_public, group)
    bob_coords = public_key_coordinates(bob_public, group)
    if alice_coords and bob_coords:
        print(f"  Alice public.x = {hex(alice_coords[0])}")
        print(f"  Alice public.y = {hex(alice_coords[1])}")
        print(f"  Bob   public.x = {hex(bob_coords[0])}")
        print(f"  Bob   public.y = {hex(bob_coords[1])}")

    print()
    print("Step 3: derive raw ECDH shared secret")
    print(f"  Alice shared == Bob shared: {alice_shared == bob_shared}")
    print(f"  shared_secret.hex = {alice_shared.hex()}")
    print(f"  shared_secret.sha256 = {sha256_hex(alice_shared)}")

    print()
    print("Step 4: derive symmetric key with HKDF")
    salt = parse_hex_or_text(args.salt_hex, args.salt, "salt")
    info = (args.info or "ecdhe-lab-demo").encode("utf-8")
    alice_key = hkdf_derive(
        alice_shared,
        group,
        key_len=args.key_len,
        hash_name=args.hash,
        salt=salt,
        info=info,
    )
    bob_key = hkdf_derive(
        bob_shared,
        group,
        key_len=args.key_len,
        hash_name=args.hash,
        salt=salt,
        info=info,
    )
    print(f"  HKDF hash = {group.kdf_hash if args.hash == 'auto' else args.hash}")
    print(f"  HKDF info = {(args.info or 'ecdhe-lab-demo')!r}")
    print(f"  Alice key == Bob key: {alice_key == bob_key}")
    print(f"  session_key.hex = {alice_key.hex()}")
    return 0


def cmd_steps(args: argparse.Namespace) -> int:
    group = args.group
    print(f"ECDHE teaching steps for group {group.name}")
    print("-" * 76)
    print("1. Group negotiation")
    print(f"   Use named group: {group.name}")
    print(f"   Curve equation/model: {group.equation}")
    print("2. Alice ephemeral key pair")
    print("   a <- random scalar/private input")
    print("   A = a*G")
    print("3. Bob ephemeral key pair")
    print("   b <- random scalar/private input")
    print("   B = b*G")
    print("4. Shared secret")
    print("   Alice: Z_A = a*B")
    print("   Bob:   Z_B = b*A")
    print("   Because scalar multiplication is associative: a*(b*G) = b*(a*G)")
    print("5. Session key")
    print("   K = HKDF(Z, salt, info)")
    print("6. Security note")
    print("   Use fresh ephemeral private keys for each session. Authenticate the peer")
    print("   public key or transcript; unauthenticated ECDHE is vulnerable to MITM.")
    return 0



# ============================================================
# INTERACTIVE FFDHE-STYLE MENU
# ============================================================


@dataclass
class InteractiveState:
    """Mutable state for the numbered ECDHE lab menu."""

    group: ECDHEGroup = GROUP_LOOKUP["secp256r1"]
    private_key: object = None
    public_key: object = None
    peer_public_key: object = None
    shared_secret: Optional[bytes] = None
    session_key: Optional[bytes] = None


def _input_default(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or default


def _pause() -> None:
    input("\nPress Enter to continue...")


def _menu_group_choices() -> None:
    print("\nAvailable ECDHE/XDH groups:")
    for idx, group in enumerate(GROUPS, start=1):
        alias = ", ".join(group.aliases[:3])
        print(f"  {idx}. {group.name:<10s}  {group.family:<24s}  security≈{group.security_bits:<3d} aliases: {alias}")


def _select_group_interactive(state: InteractiveState) -> None:
    _menu_group_choices()
    choice = _input_default("Select group by number or name", state.group.name)
    try:
        if choice.isdigit():
            idx = int(choice) - 1
            if idx < 0 or idx >= len(GROUPS):
                raise ValueError("group number out of range")
            state.group = GROUPS[idx]
        else:
            state.group = parse_group(choice)
        # Group change invalidates old keys because they belong to the old group.
        state.private_key = None
        state.public_key = None
        state.peer_public_key = None
        state.shared_secret = None
        state.session_key = None
        print(f"\nLoaded group: {state.group.name}")
    except Exception as exc:
        print(f"\nError loading group: {exc}")


def _show_parameters_interactive(state: InteractiveState) -> None:
    print()
    cmd_info(argparse.Namespace(group=state.group))


def _generate_key_interactive(state: InteractiveState) -> None:
    group = state.group
    state.private_key = generate_private_key(group)
    state.public_key = state.private_key.public_key()
    state.shared_secret = None
    state.session_key = None
    print(f"\nGenerated ephemeral key pair for group: {group.name}")
    _show_key_pair_interactive(state)

    save = _input_default("Save key pair to PEM/raw files? y/N", "N").lower()
    if save == "y":
        prefix = _input_default("File prefix", f"{group.name}_local").replace("/", "_").replace("\\\\", "_")
        priv_path = f"{prefix}_priv.pem"
        pub_path = f"{prefix}_pub.pem"
        raw_path = f"{prefix}_pub.raw"
        Path(priv_path).write_bytes(private_key_to_pem(state.private_key, None))
        Path(pub_path).write_bytes(public_key_to_pem(state.public_key))
        Path(raw_path).write_bytes(public_key_to_raw(state.public_key, group))
        print(f"Private key PEM written to: {priv_path}")
        print(f"Public key PEM written to:  {pub_path}")
        print(f"Raw public key written to:  {raw_path}")


def _show_key_pair_interactive(state: InteractiveState) -> None:
    if state.private_key is None or state.public_key is None:
        print("\nNo local key pair. Use option 2 first.")
        return

    group = state.group
    raw = public_key_to_raw(state.public_key, group)
    print("\nLocal key pair")
    print("-" * 76)
    print(f"Group: {group.name}")
    print(f"Private key type: {describe_private_key_type(state.private_key)}")
    scalar = private_key_scalar_hex(state.private_key, group)
    if scalar is not None:
        print(f"private.scalar = {scalar}")
    else:
        print("private scalar/raw bytes: hidden for X25519/X448 to avoid misleading clamped-scalar display")
    print(f"Public key type: {describe_public_key_type(state.public_key)}")
    print(f"public.raw.hex = {raw.hex()}")
    coords = public_key_coordinates(state.public_key, group)
    if coords:
        x, y = coords
        print(f"public.x = {hex(x)}")
        print(f"public.y = {hex(y)}")


def _enter_peer_public_interactive(state: InteractiveState) -> None:
    group = state.group
    print("\nEnter/load peer public key")
    print("1. Raw public key hex")
    print("2. Public key file: PEM or raw")
    choice = _input_default("Select input method", "1")
    try:
        if choice == "1":
            raw_hex = input("Peer raw public key hex: ").strip().replace(" ", "")
            peer_data = bytes.fromhex(raw_hex)
            state.peer_public_key = load_public_key_bytes_auto(peer_data, group, public_format="raw", source="interactive raw hex")
        elif choice == "2":
            path = input("Peer public key path: ").strip().strip('"')
            fmt = _input_default("Format: auto/pem/raw/x962", "auto")
            state.peer_public_key = load_public_key_auto(path, group, public_format=fmt)
        else:
            print("Invalid input method.")
            return
        state.shared_secret = None
        state.session_key = None
        print("\nPeer public key loaded and validated: True")
        _show_peer_public_interactive(state)
    except Exception as exc:
        print(f"\nInvalid peer public key: {exc}")


def _show_peer_public_interactive(state: InteractiveState) -> None:
    if state.peer_public_key is None:
        print("\nNo peer public key. Use option 3 first.")
        return
    group = state.group
    raw = public_key_to_raw(state.peer_public_key, group)
    print("\nPeer public key")
    print("-" * 76)
    print(f"Group: {group.name}")
    print(f"Detected type: {describe_public_key_type(state.peer_public_key)}")
    print(f"Raw length: {len(raw)} byte(s)")
    print(f"Raw SHA-256: {sha256_hex(raw)}")
    print(f"peer.raw.hex = {raw.hex()}")
    coords = public_key_coordinates(state.peer_public_key, group)
    if coords:
        x, y = coords
        print(f"peer.x = {hex(x)}")
        print(f"peer.y = {hex(y)}")


def _compute_shared_interactive(state: InteractiveState) -> None:
    if state.private_key is None:
        print("\nNo local private key. Use option 2 first.")
        return
    if state.peer_public_key is None:
        print("\nNo peer public key. Use option 3 first, or use option 8 for a full client/server demo.")
        return

    group = state.group
    try:
        shared = ecdh_exchange(state.private_key, state.peer_public_key, group)
        state.shared_secret = shared
        print("\nComputed ECDHE/XDH shared secret")
        print("-" * 76)
        print(f"Group: {group.name}")
        print(f"Shared secret length: {len(shared)} byte(s)")
        print(f"shared_secret.hex = {shared.hex()}")
        print(f"shared_secret.sha256 = {sha256_hex(shared)}")

        use_kdf = _input_default("Derive session key with HKDF? Y/n", "Y").lower()
        if use_kdf != "n":
            key_len = int(_input_default("HKDF key length in bytes", "32"))
            hash_name = _input_default("HKDF hash: auto/sha256/sha384/sha512", "auto")
            info_text = _input_default("HKDF info/context", "ecdhe-lab-menu")
            salt_text = input("HKDF salt text, empty for None: ").strip()
            salt = salt_text.encode("utf-8") if salt_text else None
            key = hkdf_derive(
                shared,
                group,
                key_len=key_len,
                hash_name=hash_name,
                salt=salt,
                info=info_text.encode("utf-8"),
            )
            state.session_key = key
            print(f"HKDF key.hex = {key.hex()}")
    except Exception as exc:
        print(f"\nError computing shared secret: {exc}")


def _client_server_demo_interactive(state: InteractiveState) -> None:
    print()
    key_len = int(_input_default("HKDF key length in bytes", "32"))
    info_text = _input_default("HKDF info/context", "ecdhe-lab-demo")
    args = argparse.Namespace(group=state.group, key_len=key_len, hash="auto", salt=None, salt_hex=None, info=info_text)
    cmd_demo(args)


def _openssl_info_interactive() -> None:
    print()
    cmd_openssl_info(argparse.Namespace())


def print_interactive_menu(state: InteractiveState) -> None:
    print("\n=== ECDHE LAB ===")
    print(f"Current group: {state.group.name} ({state.group.family})")
    print("1. Load ECDHE/XDH Group")
    print("2. Generate Key Pair")
    print("3. Enter Peer Public Key")
    print("4. Show Parameters")
    print("5. Show Key Pair")
    print("6. Show Peer Public Key")
    print("7. Compute Shared Secret")
    print("8. Client/Server Demo")
    print("9. List ECDHE/XDH Groups")
    print("0. Exit")


def interactive_menu() -> int:
    """Run FFDHE-style numbered menu when no CLI task is supplied."""
    state = InteractiveState()
    while True:
        try:
            print_interactive_menu(state)
            choice = input("Select an option: ").strip()
            if choice == "1":
                _select_group_interactive(state)
                _pause()
            elif choice == "2":
                _generate_key_interactive(state)
                _pause()
            elif choice == "3":
                _enter_peer_public_interactive(state)
                _pause()
            elif choice == "4":
                _show_parameters_interactive(state)
                _pause()
            elif choice == "5":
                _show_key_pair_interactive(state)
                _pause()
            elif choice == "6":
                _show_peer_public_interactive(state)
                _pause()
            elif choice == "7":
                _compute_shared_interactive(state)
                _pause()
            elif choice == "8":
                _client_server_demo_interactive(state)
                _pause()
            elif choice == "9":
                print()
                cmd_list_groups(argparse.Namespace())
                _pause()
            elif choice == "0":
                print("Exiting...")
                return 0
            else:
                print("Invalid option. Please try again.")
                _pause()
        except KeyboardInterrupt:
            print("\nExiting...")
            return 130
        except EOFError:
            print("\nExiting...")
            return 0

# ============================================================
# ARGPARSE
# ============================================================


def add_common_kdf_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--key-len", type=int, default=32, help="HKDF output length in bytes")
    parser.add_argument(
        "--hash",
        choices=("auto", "sha256", "sha384", "sha512"),
        default="auto",
        help="HKDF hash; auto follows the selected group",
    )
    salt_group = parser.add_mutually_exclusive_group()
    salt_group.add_argument("--salt", help="HKDF salt as UTF-8 text")
    salt_group.add_argument("--salt-hex", help="HKDF salt as hexadecimal bytes")
    parser.add_argument("--info", help="HKDF info/context string")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ECDHE/XDH lab CLI with FFDHE-style group/task workflow.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--group",
        "--curve",
        dest="group",
        type=parse_group,
        default=GROUP_LOOKUP["secp256r1"],
        help="ECDHE/XDH named group. --curve is accepted as an alias.",
    )

    sub = parser.add_subparsers(dest="task", required=True, title="tasks")

    p = sub.add_parser("openssl-info", help="show cryptography/OpenSSL versions")
    p.set_defaults(func=cmd_openssl_info)

    p = sub.add_parser("list-groups", help="list supported ECDHE/XDH groups")
    p.set_defaults(func=cmd_list_groups)

    p = sub.add_parser("info", help="show selected group parameters and ECDHE equations")
    p.set_defaults(func=cmd_info)

    p = sub.add_parser("steps", help="print ECDHE teaching steps and formulas")
    p.set_defaults(func=cmd_steps)

    p = sub.add_parser("generate", help="generate one ephemeral/private key pair")
    p.add_argument("--private-out", default="ecdh_private.pem", help="output private key PEM")
    p.add_argument("--public-out", default="ecdh_public.pem", help="output public key PEM")
    p.add_argument("--public-raw-out", help="optional raw public key output file")
    p.add_argument("--password", help="optional password for encrypting the private PEM")
    p.add_argument("--print-public", action="store_true", help="print public key raw hex and coordinates")
    p.add_argument(
        "--print-private-scalar",
        action="store_true",
        help="print EC private scalar for short-Weierstrass groups only; teaching/debug only",
    )
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("public", help="recompute/export public key from a private key")
    p.add_argument("--private", required=True, help="input private key PEM")
    p.add_argument("--password", help="private key password if encrypted")
    p.add_argument("--public-out", help="optional output public key PEM")
    p.add_argument("--raw-out", help="optional output raw public key file")
    p.set_defaults(func=cmd_public)

    p = sub.add_parser("validate-peer", help="validate/load a peer public key for the selected group")
    p.add_argument("--public", required=True, help="peer public key file; PEM or raw")
    p.add_argument(
        "--public-format",
        choices=("auto", "pem", "raw", "x962"),
        default="auto",
        help="input public-key encoding",
    )
    p.set_defaults(func=cmd_validate_peer)

    p = sub.add_parser("derive", help="derive raw ECDH secret and optional HKDF session key")
    p.add_argument("--private", required=True, help="our private key PEM")
    p.add_argument("--password", help="private key password if encrypted")
    peer_group = p.add_mutually_exclusive_group(required=True)
    peer_group.add_argument("--peer-public", help="peer public key file; PEM or raw")
    peer_group.add_argument("--peer-public-hex", help="peer raw public key as hex")
    p.add_argument(
        "--peer-public-format",
        choices=("auto", "pem", "raw", "x962"),
        default="auto",
        help="peer public-key encoding when --peer-public is used",
    )
    p.add_argument("--shared-out", help="optional output file for raw shared secret")
    p.add_argument("--key-out", help="optional output file for HKDF-derived key")
    p.add_argument("--no-kdf", action="store_true", help="only compute raw shared secret")
    add_common_kdf_options(p)
    p.set_defaults(func=cmd_derive)

    p = sub.add_parser("demo", help="run Alice/Bob ECDHE + HKDF demonstration")
    add_common_kdf_options(p)
    p.set_defaults(func=cmd_demo)

    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    # FFDHE-style behavior: running the file with no arguments opens the
    # numbered teaching menu. Passing any argument keeps the scriptable CLI.
    if argv is None:
        argv_list = sys.argv[1:]
    else:
        argv_list = list(argv)

    if not argv_list:
        return interactive_menu()

    parser = build_parser()
    args = parser.parse_args(argv_list)
    try:
        return int(args.func(args) or 0)
    except (ValueError, RuntimeError, OSError, binascii.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
