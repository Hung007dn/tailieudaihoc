#!/usr/bin/env python3
"""
ECC arithmetic and OpenSSL-backed ECC task CLI.

Version: v3-curve-models

This version extends the previous short-Weierstrass-only teaching CLI with
multiple elliptic-curve models:

1. Short Weierstrass curves
   - Equation: y^2 = x^3 + a*x + b mod p
   - Examples: P-256, P-384, P-521, secp256k1

2. Montgomery curves
   - Equation: B*y^2 = x^3 + A*x^2 + x mod p
   - Examples: Curve25519, Curve448
   - Includes both full affine point operations and an x-only Montgomery
     ladder task for teaching X25519/X448-style scalar multiplication.

3. Twisted Edwards curves
   - Equation: a*x^2 + y^2 = 1 + d*x^2*y^2 mod p
   - Examples: Ed25519, Ed448

Important security note
-----------------------
All pure-Python arithmetic in this file is educational only. It is not
constant-time and must not be used with production secrets. For real systems,
use a vetted cryptographic library such as pyca/cryptography/OpenSSL.

Example commands
----------------

    python ECC_arithmetic_cli_v3_models.py list-curves
    python ECC_arithmetic_cli_v3_models.py --curve p-256 info
    python ECC_arithmetic_cli_v3_models.py --curve curve25519 info
    python ECC_arithmetic_cli_v3_models.py --curve ed25519 info

    python ECC_arithmetic_cli_v3_models.py --curve p-256 check-generator
    python ECC_arithmetic_cli_v3_models.py --curve curve25519 check-generator
    python ECC_arithmetic_cli_v3_models.py --curve ed25519 check-generator

    python ECC_arithmetic_cli_v3_models.py --curve ed25519 add --p1 G --p2 2G
    python ECC_arithmetic_cli_v3_models.py --curve curve25519 mul --k 123456789 --point G
    python ECC_arithmetic_cli_v3_models.py --curve curve25519 xmul --k 123456789 --u 9

    python ECC_arithmetic_cli_v3_models.py openssl-info
    python ECC_arithmetic_cli_v3_models.py --curve p-256 openssl-keygen \
        --private-key-out ec_private.pem --public-key-out ec_public.pem
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

Point = Optional[Tuple[int, int]]
INF: Point = None

MODEL_WEIERSTRASS = "short-weierstrass"
MODEL_MONTGOMERY = "montgomery"
MODEL_TWISTED_EDWARDS = "twisted-edwards"


# ============================================================
# FINITE-FIELD HELPERS USED DURING CURVE CONSTRUCTION
# ============================================================


def inv_mod_prime(a: int, p: int) -> int:
    """Return a^{-1} mod p."""
    return pow(a % p, -1, p)


def mod_sqrt(n: int, p: int) -> int:
    """Return one square root of n modulo odd prime p.

    Uses fast special cases for p % 4 == 3 and p % 8 == 5, then falls back
    to Tonelli-Shanks. Raises ValueError if no square root exists.
    """
    n %= p
    if n == 0:
        return 0
    if p == 2:
        return n
    if pow(n, (p - 1) // 2, p) != 1:
        raise ValueError("not a quadratic residue")

    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)

    if p % 8 == 5:
        x = pow(n, (p + 3) // 8, p)
        if (x * x - n) % p != 0:
            x = (x * pow(2, (p - 1) // 4, p)) % p
        if (x * x - n) % p == 0:
            return x
        raise ValueError("square-root failure")

    # Tonelli-Shanks for the general odd-prime case.
    q = p - 1
    s = 0
    while q % 2 == 0:
        s += 1
        q //= 2

    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1

    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q + 1) // 2, p)

    while t != 1:
        i = 1
        t2i = (t * t) % p
        while t2i != 1:
            t2i = (t2i * t2i) % p
            i += 1
            if i == m:
                raise ValueError("Tonelli-Shanks failure")

        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p

    return r


# ============================================================
# CURVE DEFINITIONS
# ============================================================


@dataclass(frozen=True)
class Curve:
    """Prime-field elliptic curve in one of several affine models."""

    name: str
    aliases: Tuple[str, ...]
    model: str
    p: int
    gx: int
    gy: int
    n: int
    h: int

    # Short Weierstrass: y^2 = x^3 + a*x + b.
    a: int = 0
    b: int = 0

    # Montgomery: B*y^2 = x^3 + A*x^2 + x.
    mont_A: int = 0
    mont_B: int = 1

    # Twisted Edwards: a*x^2 + y^2 = 1 + d*x^2*y^2.
    ed_a: int = 0
    ed_d: int = 0

    # Optional OpenSSL/cryptography name for short-Weierstrass ec.ECDSA/ec.ECDH.
    openssl_name: str = ""
    parameter_note: str = ""

    @property
    def G(self) -> Tuple[int, int]:
        return (self.gx, self.gy)

    @property
    def bits(self) -> int:
        return self.p.bit_length()

    @property
    def hex_width(self) -> int:
        return (self.bits + 3) // 4


# NIST / SEC short-Weierstrass curves.
P256 = Curve(
    name="p-256",
    aliases=("p256", "secp256r1", "prime256v1", "nistp256", "nist-p256"),
    model=MODEL_WEIERSTRASS,
    p=0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF,
    a=0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC,
    b=0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B,
    gx=0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
    gy=0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5,
    n=0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551,
    h=1,
    openssl_name="secp256r1",
)

P384 = Curve(
    name="p-384",
    aliases=("p384", "secp384r1", "nistp384", "nist-p384"),
    model=MODEL_WEIERSTRASS,
    p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFF0000000000000000FFFFFFFF,
    a=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFF0000000000000000FFFFFFFC,
    b=0xB3312FA7E23EE7E4988E056BE3F82D19181D9C6EFE8141120314088F5013875AC656398D8A2ED19D2A85C8EDD3EC2AEF,
    gx=0xAA87CA22BE8B05378EB1C71EF320AD746E1D3B628BA79B9859F741E082542A385502F25DBF55296C3A545E3872760AB7,
    gy=0x3617DE4A96262C6F5D9E98BF9292DC29F8F41DBD289A147CE9DA3113B5F0B8C00A60B1CE1D7E819D7A431D7C90EA0E5F,
    n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973,
    h=1,
    openssl_name="secp384r1",
)

P521 = Curve(
    name="p-521",
    aliases=("p521", "secp521r1", "nistp521", "nist-p521"),
    model=MODEL_WEIERSTRASS,
    p=(1 << 521) - 1,
    a=((1 << 521) - 1) - 3,
    b=0x0051953EB9618E1C9A1F929A21A0B68540EEA2DA725B99B315F3B8B489918EF109E156193951EC7E937B1652C0BD3BB1BF073573DF883D2C34F1EF451FD46B503F00,
    gx=0x00C6858E06B70404E9CD9E3ECB662395B4429C648139053FB521F828AF606B4D3DBAA14B5E77EFE75928FE1DC127A2FFA8DE3348B3C1856A429BF97E7E31C2E5BD66,
    gy=0x011839296A789A3BC0045C8A5FB42C7D1BD998F54449579B446817AFBD17273E662C97EE72995EF42640C550B9013FAD0761353C7086A272C24088BE94769FD16650,
    n=0x01FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA51868783BF2F966B7FCC0148F709A5D03BB5C9B8899C47AEBB6FB71E91386409,
    h=1,
    openssl_name="secp521r1",
)

SECP256K1 = Curve(
    name="secp256k1",
    aliases=("k-256", "k256", "bitcoin"),
    model=MODEL_WEIERSTRASS,
    p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
    a=0,
    b=7,
    gx=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    gy=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
    n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
    h=1,
    openssl_name="secp256k1",
)

# Montgomery curves.  The X25519/X448 protocols normally use only the u/x
# coordinate.  For teaching full affine addition, we recover one valid y from
# the standard base u-coordinate using modular square root.
P25519 = (1 << 255) - 19
L25519 = (1 << 252) + 27742317777372353535851937790883648493
CURVE25519_U = 9
CURVE25519_A = 486662
CURVE25519_B = 1
# One valid affine y-coordinate for the standard Montgomery base u=9.
# It satisfies y^2 = u^3 + 486662*u^2 + u mod p.
CURVE25519_V = 14781619447589544791020593568409986887264606134616475288964881837755586237401

CURVE25519 = Curve(
    name="curve25519",
    aliases=("montgomery25519", "x25519", "curve-25519"),
    model=MODEL_MONTGOMERY,
    p=P25519,
    mont_A=CURVE25519_A,
    mont_B=CURVE25519_B,
    gx=CURVE25519_U,
    gy=CURVE25519_V,
    n=L25519,
    h=8,
    openssl_name="x25519",
    parameter_note="Montgomery base u/x = 9; affine y was recovered with modular square root for teaching.",
)

P448 = (1 << 448) - (1 << 224) - 1
L448 = (1 << 446) - 13818066809895115352007386748515426880336692474882178609894547503885
CURVE448_U = 5
CURVE448_A = 156326
CURVE448_B = 1
# One valid affine y-coordinate for the standard Montgomery base u=5.
# It satisfies y^2 = u^3 + 156326*u^2 + u mod p.
CURVE448_V = 371544797510038715285196305824221199544664961299603788449609300745443239379763362683463709932811995019946110314575531522067902727759077

CURVE448 = Curve(
    name="curve448",
    aliases=("montgomery448", "x448", "goldilocks"),
    model=MODEL_MONTGOMERY,
    p=P448,
    mont_A=CURVE448_A,
    mont_B=CURVE448_B,
    gx=CURVE448_U,
    gy=CURVE448_V,
    n=L448,
    h=4,
    openssl_name="x448",
    parameter_note="Montgomery base u/x = 5; affine y was recovered with modular square root for teaching.",
)

# Twisted Edwards curves.
ED25519_D = (-121665 * inv_mod_prime(121666, P25519)) % P25519
ED25519 = Curve(
    name="ed25519",
    aliases=("edwards25519", "ed-25519"),
    model=MODEL_TWISTED_EDWARDS,
    p=P25519,
    ed_a=(-1) % P25519,
    ed_d=ED25519_D,
    gx=15112221349535400772501151409588531511454012693041857206046113283949847762202,
    gy=46316835694926478169428394003475163141307993866256225615783033603165251855960,
    n=L25519,
    h=8,
    openssl_name="ed25519",
    parameter_note="d = -121665/121666 mod p; neutral point is (0, 1), not a point at infinity.",
)

ED448 = Curve(
    name="ed448",
    aliases=("edwards448", "ed-448"),
    model=MODEL_TWISTED_EDWARDS,
    p=P448,
    ed_a=1,
    ed_d=(-39081) % P448,
    gx=224580040295924300187604334099896036246789641632564134246125461686950415467406032909029192869357953282578032075146446173674602635247710,
    gy=298819210078481492676017930443930673437544040154080242095928241372331506189835876003536878655418784733982303233503462500531545062832660,
    n=L448,
    h=4,
    openssl_name="ed448",
    parameter_note="d = -39081 mod p; neutral point is (0, 1), not a point at infinity.",
)

SUPPORTED_CURVES: Tuple[Curve, ...] = (
    P256,
    P384,
    P521,
    SECP256K1,
    CURVE25519,
    CURVE448,
    ED25519,
    ED448,
)


def _curve_key(name: str) -> str:
    return name.strip().lower().replace("_", "-")


CURVE_LOOKUP: Dict[str, Curve] = {}
for _curve in SUPPORTED_CURVES:
    CURVE_LOOKUP[_curve_key(_curve.name)] = _curve
    for _alias in _curve.aliases:
        CURVE_LOOKUP[_curve_key(_alias)] = _curve


# ============================================================
# BASIC PARSING AND FORMATTING
# ============================================================


def parse_int(text: str) -> int:
    """Parse decimal or 0x-prefixed integer text."""
    clean = text.strip().replace("_", "")
    if not clean:
        raise ValueError("empty integer")
    return int(clean, 0)


def fmt_int(value: int, curve: Optional[Curve] = None) -> str:
    """Format an integer as fixed-width hexadecimal if a curve is known."""
    if curve is None:
        return hex(value)
    return "0x" + format(value % curve.p if value >= 0 else value, f"0{curve.hex_width}x")


def signed_small_or_hex(value: int, curve: Curve, small_limit: int = 1_000_000) -> str:
    """Format a field element as small signed decimal when useful, else hex."""
    value %= curve.p
    if value <= small_limit:
        return str(value)
    negative = curve.p - value
    if negative <= small_limit:
        return f"-{negative}"
    return fmt_int(value, curve)


def coefficient_for_equation(value: int, variable: str, curve: Curve) -> str:
    """Return a readable coefficient term for a symbolic curve equation."""
    value %= curve.p

    if value == 0:
        return ""
    if value == 1:
        return f" + {variable}"

    negative_magnitude = curve.p - value
    if negative_magnitude == 1:
        return f" - {variable}"
    if negative_magnitude <= 16:
        return f" - {negative_magnitude}*{variable}"
    if value <= 16:
        return f" + {value}*{variable}"

    return f" + {fmt_int(value, curve)}*{variable}"


def constant_for_equation(value: int, curve: Curve) -> str:
    """Return a readable constant term for a symbolic curve equation."""
    value %= curve.p

    if value == 0:
        return ""
    if value <= 16:
        return f" + {value}"

    negative_magnitude = curve.p - value
    if negative_magnitude <= 16:
        return f" - {negative_magnitude}"

    return f" + {fmt_int(value, curve)}"



def signed_coefficient_term(value: int, variable: str, curve: Curve, *, first: bool = False) -> str:
    """Format a signed coefficient term, e.g., -x^2, + 486662*x^2."""
    value %= curve.p
    if value == 0:
        return "" if not first else "0"

    negative = curve.p - value
    if value == 1:
        term = variable
        sign = "+"
    elif negative == 1:
        term = variable
        sign = "-"
    elif value <= 1_000_000:
        term = f"{value}*{variable}"
        sign = "+"
    elif negative <= 1_000_000:
        term = f"{negative}*{variable}"
        sign = "-"
    else:
        term = f"{fmt_int(value, curve)}*{variable}"
        sign = "+"

    if first:
        return term if sign == "+" else f"-{term}"
    return f" {sign} {term}"

def curve_equation(curve: Curve) -> str:
    """Return the affine equation for the selected curve model."""
    if curve.model == MODEL_WEIERSTRASS:
        rhs = "x^3"
        rhs += coefficient_for_equation(curve.a, "x", curve)
        rhs += constant_for_equation(curve.b, curve)
        return f"y^2 ≡ {rhs} (mod p)"

    if curve.model == MODEL_MONTGOMERY:
        lhs = "y^2" if curve.mont_B % curve.p == 1 else f"{signed_small_or_hex(curve.mont_B, curve)}*y^2"
        rhs = "x^3"
        rhs += signed_coefficient_term(curve.mont_A, "x^2", curve)
        rhs += " + x"
        return f"{lhs} ≡ {rhs} (mod p)"

    if curve.model == MODEL_TWISTED_EDWARDS:
        left = signed_coefficient_term(curve.ed_a, "x^2", curve, first=True) + " + y^2"
        d_term = signed_coefficient_term(curve.ed_d, "x^2*y^2", curve)
        right = f"1{d_term}" if d_term else "1"
        return f"{left} ≡ {right} (mod p)"

    raise ValueError(f"unsupported curve model {curve.model!r}")


def canonical_equation_form(curve: Curve) -> str:
    if curve.model == MODEL_WEIERSTRASS:
        return "short Weierstrass: y^2 ≡ x^3 + a*x + b (mod p)"
    if curve.model == MODEL_MONTGOMERY:
        return "Montgomery: B*y^2 ≡ x^3 + A*x^2 + x (mod p)"
    if curve.model == MODEL_TWISTED_EDWARDS:
        return "twisted Edwards: a*x^2 + y^2 ≡ 1 + d*x^2*y^2 (mod p)"
    raise ValueError(f"unsupported curve model {curve.model!r}")


def print_point(name: str, point: Point, curve: Curve) -> None:
    if point is INF:
        print(f"{name} = INF")
        return
    x, y = point
    print(f"{name}.x = {fmt_int(x, curve)}")
    print(f"{name}.y = {fmt_int(y, curve)}")


def parse_curve(name: str) -> Curve:
    key = _curve_key(name)
    try:
        return CURVE_LOOKUP[key]
    except KeyError as exc:
        known = ", ".join(curve.name for curve in SUPPORTED_CURVES)
        raise argparse.ArgumentTypeError(
            f"unknown curve {name!r}; supported canonical names: {known}"
        ) from exc


# ============================================================
# MODEL-AWARE FIELD AND POINT OPERATIONS
# ============================================================


def mod_inv(a: int, curve: Curve) -> int:
    """Return a^{-1} mod p for the selected curve field."""
    return pow(a % curve.p, -1, curve.p)


def identity_point(curve: Curve) -> Point:
    """Return the neutral element for the selected affine model."""
    if curve.model == MODEL_TWISTED_EDWARDS:
        return (0, 1)
    return INF


def is_identity(point: Point, curve: Curve) -> bool:
    if curve.model == MODEL_TWISTED_EDWARDS:
        return point is INF or point == (0, 1)
    return point is INF


def is_on_curve(point: Point, curve: Curve) -> bool:
    if point is INF:
        return True

    x, y = point
    p = curve.p

    if curve.model == MODEL_WEIERSTRASS:
        lhs = (y * y) % p
        rhs = (pow(x, 3, p) + curve.a * x + curve.b) % p
        return lhs == rhs

    if curve.model == MODEL_MONTGOMERY:
        lhs = (curve.mont_B * y * y) % p
        rhs = (pow(x, 3, p) + curve.mont_A * x * x + x) % p
        return lhs == rhs

    if curve.model == MODEL_TWISTED_EDWARDS:
        lhs = (curve.ed_a * x * x + y * y) % p
        rhs = (1 + curve.ed_d * x * x * y * y) % p
        return lhs == rhs

    raise ValueError(f"unsupported curve model {curve.model!r}")


def point_neg(point: Point, curve: Curve) -> Point:
    if point is INF:
        return identity_point(curve)

    x, y = point
    if curve.model in {MODEL_WEIERSTRASS, MODEL_MONTGOMERY}:
        return (x, (-y) % curve.p)
    if curve.model == MODEL_TWISTED_EDWARDS:
        return ((-x) % curve.p, y)

    raise ValueError(f"unsupported curve model {curve.model!r}")


def point_double(point: Point, curve: Curve) -> Point:
    if is_identity(point, curve):
        return identity_point(curve)

    if curve.model == MODEL_TWISTED_EDWARDS:
        return point_add(point, point, curve)

    assert point is not INF
    x, y = point
    p = curve.p

    if y % p == 0:
        return identity_point(curve)

    if curve.model == MODEL_WEIERSTRASS:
        lam = ((3 * x * x + curve.a) * mod_inv(2 * y, curve)) % p
        x3 = (lam * lam - 2 * x) % p
        y3 = (lam * (x - x3) - y) % p
        return (x3, y3)

    if curve.model == MODEL_MONTGOMERY:
        numerator = (3 * x * x + 2 * curve.mont_A * x + 1) % p
        denominator = (2 * curve.mont_B * y) % p
        lam = (numerator * mod_inv(denominator, curve)) % p
        x3 = (curve.mont_B * lam * lam - curve.mont_A - 2 * x) % p
        y3 = (lam * (x - x3) - y) % p
        return (x3, y3)

    raise ValueError(f"unsupported curve model {curve.model!r}")


def point_add(p1: Point, p2: Point, curve: Curve) -> Point:
    if is_identity(p1, curve):
        return p2 if p2 is not INF else identity_point(curve)
    if is_identity(p2, curve):
        return p1 if p1 is not INF else identity_point(curve)

    assert p1 is not INF and p2 is not INF
    x1, y1 = p1
    x2, y2 = p2
    p = curve.p

    if curve.model in {MODEL_WEIERSTRASS, MODEL_MONTGOMERY}:
        # P + (-P) = O, the point at infinity.
        if x1 == x2 and (y1 + y2) % p == 0:
            return identity_point(curve)
        if p1 == p2:
            return point_double(p1, curve)

        lam = ((y2 - y1) * mod_inv(x2 - x1, curve)) % p

        if curve.model == MODEL_WEIERSTRASS:
            x3 = (lam * lam - x1 - x2) % p
        else:
            x3 = (curve.mont_B * lam * lam - curve.mont_A - x1 - x2) % p

        y3 = (lam * (x1 - x3) - y1) % p
        return (x3, y3)

    if curve.model == MODEL_TWISTED_EDWARDS:
        xx = (x1 * x2) % p
        yy = (y1 * y2) % p
        xyxy = (xx * yy) % p
        denom_x = (1 + curve.ed_d * xyxy) % p
        denom_y = (1 - curve.ed_d * xyxy) % p
        x3 = ((x1 * y2 + y1 * x2) * mod_inv(denom_x, curve)) % p
        y3 = ((yy - curve.ed_a * xx) * mod_inv(denom_y, curve)) % p
        return (x3, y3)

    raise ValueError(f"unsupported curve model {curve.model!r}")


def scalar_mult(k: int, point: Point, curve: Curve) -> Point:
    """Double-and-add scalar multiplication.

    Educational implementation only. It is not constant-time and should not be
    used with production secrets.
    """
    if is_identity(point, curve):
        return identity_point(curve)

    if k < 0:
        return scalar_mult(-k, point_neg(point, curve), curve)

    if k == 0:
        return identity_point(curve)

    result: Point = identity_point(curve)
    addend: Point = point

    while k:
        if k & 1:
            result = point_add(result, addend, curve)
        addend = point_double(addend, curve)
        k >>= 1

    return result


def montgomery_x_ladder(k: int, u: int, curve: Curve) -> int:
    """Return x/u-coordinate of k*(u, v) using a Montgomery x-only ladder.

    This is a teaching implementation of the ladder formulas. It does not
    implement full RFC 7748 clamping or byte encoding/decoding.
    """
    if curve.model != MODEL_MONTGOMERY:
        raise ValueError("x-only Montgomery ladder requires a Montgomery curve")
    if curve.mont_B % curve.p != 1:
        raise ValueError("this simple ladder implementation expects B = 1")
    if k < 0:
        raise ValueError("x-only ladder expects a non-negative scalar")

    p = curve.p
    x1 = u % p
    x2, z2 = 1, 0
    x3, z3 = x1, 1
    swap = 0
    a24 = ((curve.mont_A - 2) * inv_mod_prime(4, p)) % p

    for t in range(max(k.bit_length() - 1, 0), -1, -1):
        kt = (k >> t) & 1
        swap ^= kt
        if swap:
            x2, x3 = x3, x2
            z2, z3 = z3, z2
        swap = kt

        A = (x2 + z2) % p
        AA = (A * A) % p
        B = (x2 - z2) % p
        BB = (B * B) % p
        E = (AA - BB) % p
        C = (x3 + z3) % p
        D = (x3 - z3) % p
        DA = (D * A) % p
        CB = (C * B) % p
        x3 = ((DA + CB) ** 2) % p
        z3 = (x1 * ((DA - CB) ** 2)) % p
        x2 = (AA * BB) % p
        z2 = (E * (AA + a24 * E)) % p

    if swap:
        x2, x3 = x3, x2
        z2, z3 = z3, z2

    if z2 % p == 0:
        raise ZeroDivisionError("ladder result has z = 0; point at infinity in projective x-coordinate")
    return (x2 * inv_mod_prime(z2, p)) % p


def parse_point(text: str, curve: Curve) -> Point:
    """Parse INF, ID, G, kG/k*G, or x,y point coordinates."""
    raw = text.strip()
    compact = raw.replace(" ", "")
    lower = compact.lower()

    if lower in {"inf", "infinity", "none", "o", "id", "identity", "neutral"}:
        return identity_point(curve)

    if lower in {"g", "generator", "base"}:
        return curve.G

    # Accept teaching-friendly notation: 2G, 2*G, 0x10*G, -3G.
    if lower.endswith("g"):
        scalar_part = compact[:-1]
        if scalar_part.endswith("*"):
            scalar_part = scalar_part[:-1]
        if scalar_part in {"", "+"}:
            return curve.G
        if scalar_part == "-":
            return point_neg(curve.G, curve)
        point = scalar_mult(parse_int(scalar_part), curve.G, curve)
        if point is INF or is_on_curve(point, curve):
            return point
        raise ValueError(f"generated point from {text!r} is not on {curve.name}")

    sep = "," if "," in compact else ":" if ":" in compact else None
    if sep is None:
        raise ValueError(
            f"invalid point {text!r}; use G, INF/ID, kG, k*G, or x,y hexadecimal coordinates"
        )

    left, right = compact.split(sep, 1)
    point = (parse_int(left), parse_int(right))
    if not is_on_curve(point, curve):
        raise ValueError(f"point {text!r} is not on curve {curve.name}")
    return point


# ============================================================
# OPENSSL / CRYPTOGRAPHY SUPPORT
# ============================================================


def require_cryptography():
    try:
        from cryptography import __version__ as crypto_version
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.bindings.openssl.binding import Binding
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    except Exception as exc:  # pragma: no cover - used for environment diagnostics.
        raise RuntimeError(
            "OpenSSL-backed tasks require pyca/cryptography. Install it with: "
            "python -m pip install cryptography"
        ) from exc

    return {
        "version": crypto_version,
        "InvalidSignature": InvalidSignature,
        "Binding": Binding,
        "hashes": hashes,
        "serialization": serialization,
        "ec": ec,
        "HKDF": HKDF,
    }


def require_short_weierstrass_openssl_curve(curve: Curve) -> None:
    if curve.model != MODEL_WEIERSTRASS or not curve.openssl_name:
        raise RuntimeError(
            f"OpenSSL ECDSA/ECDH demo tasks in this script currently use "
            f"cryptography.hazmat.primitives.asymmetric.ec and therefore require "
            f"a short-Weierstrass curve. Selected curve {curve.name!r} uses "
            f"model {curve.model!r}. Use pure arithmetic tasks for this curve."
        )


def openssl_curve_object(curve: Curve):
    require_short_weierstrass_openssl_curve(curve)
    c = require_cryptography()["ec"]
    mapping = {
        "secp256r1": c.SECP256R1,
        "secp384r1": c.SECP384R1,
        "secp521r1": c.SECP521R1,
        "secp256k1": c.SECP256K1,
    }
    try:
        return mapping[curve.openssl_name]()
    except KeyError as exc:
        raise RuntimeError(f"curve {curve.name} has no OpenSSL ec mapping") from exc


def default_hash_algorithm(curve: Curve):
    hashes = require_cryptography()["hashes"]
    if curve.bits >= 512:
        return hashes.SHA512()
    if curve.bits >= 384:
        return hashes.SHA384()
    return hashes.SHA256()


def read_message(args: argparse.Namespace) -> bytes:
    if getattr(args, "message_file", None):
        return Path(args.message_file).read_bytes()
    if getattr(args, "message_hex", None):
        return bytes.fromhex(args.message_hex)
    if getattr(args, "message", None) is not None:
        return args.message.encode("utf-8")
    return b""


def load_password(password: Optional[str]) -> Optional[bytes]:
    if password is None:
        return None
    return password.encode("utf-8")


def load_private_key(path: str, password: Optional[str] = None):
    d = require_cryptography()
    serialization = d["serialization"]
    return serialization.load_pem_private_key(
        Path(path).read_bytes(), password=load_password(password)
    )


def load_public_key(path: str):
    d = require_cryptography()
    serialization = d["serialization"]
    return serialization.load_pem_public_key(Path(path).read_bytes())


def write_bytes_or_hex(data: bytes, output_path: Optional[str], label: str) -> None:
    if output_path:
        Path(output_path).write_bytes(data)
        print(f"{label} written to: {output_path}")
    else:
        print(f"{label}.hex = {data.hex()}")


# ============================================================
# CLI TASK HANDLERS: PURE PYTHON
# ============================================================


def cmd_list_curves(_: argparse.Namespace) -> int:
    for curve in SUPPORTED_CURVES:
        alias_text = ", ".join(curve.aliases)
        openssl_text = curve.openssl_name or "-"
        print(
            f"{curve.name:12s} model={curve.model:18s} "
            f"bits={curve.bits:<3d} h={curve.h:<2d} openssl={openssl_text:10s} "
            f"aliases={alias_text}"
        )
    return 0


def print_model_parameters(curve: Curve) -> None:
    if curve.model == MODEL_WEIERSTRASS:
        print(f"a = {fmt_int(curve.a, curve)}")
        print(f"b = {fmt_int(curve.b, curve)}")
    elif curve.model == MODEL_MONTGOMERY:
        print(f"A = {fmt_int(curve.mont_A, curve)}")
        print(f"B = {fmt_int(curve.mont_B, curve)}")
        print(f"a24 = (A - 2)/4 mod p = {fmt_int(((curve.mont_A - 2) * mod_inv(4, curve)) % curve.p, curve)}")
    elif curve.model == MODEL_TWISTED_EDWARDS:
        print(f"a = {fmt_int(curve.ed_a, curve)}")
        print(f"d = {fmt_int(curve.ed_d, curve)}")
        print("identity/neutral point = (0, 1)")
    else:
        raise ValueError(f"unsupported curve model {curve.model!r}")


def cmd_info(args: argparse.Namespace) -> int:
    curve = args.curve
    print("Script: ECC_arithmetic_cli_v3_models.py")
    print("Version: v3-curve-models")
    print(f"Curve: {curve.name}")
    print(f"Model: {curve.model}")
    print(f"Aliases: {', '.join(curve.aliases)}")
    print(f"OpenSSL name: {curve.openssl_name or '(not mapped for ECDSA/ECDH ec API)'}")
    print(f"Bits: {curve.bits}")
    print("Equation over F_p:")
    print(f"  {curve_equation(curve)}")
    print(f"  canonical form: {canonical_equation_form(curve)}")
    if curve.parameter_note:
        print(f"  note: {curve.parameter_note}")
    print(f"p = {fmt_int(curve.p)}")
    print_model_parameters(curve)
    print(f"n = {fmt_int(curve.n)}")
    print(f"h = {curve.h}")
    print_point("G", curve.G, curve)
    return 0


def cmd_check_generator(args: argparse.Namespace) -> int:
    curve = args.curve
    q = scalar_mult(curve.n, curve.G, curve)
    print(f"Curve: {curve.name}")
    print(f"Model: {curve.model}")
    print(f"Generator on curve: {is_on_curve(curve.G, curve)}")
    print(f"n*G is identity: {is_identity(q, curve)}")
    if not is_identity(q, curve):
        print_point("nG", q, curve)
    return 0


def cmd_neg(args: argparse.Namespace) -> int:
    curve = args.curve
    point = parse_point(args.point, curve)
    q = point_neg(point, curve)
    print_point("-P", q, curve)
    print(f"On curve: {is_on_curve(q, curve)}")
    return 0


def cmd_double(args: argparse.Namespace) -> int:
    curve = args.curve
    point = parse_point(args.point, curve)
    q = point_double(point, curve)
    print_point("2P", q, curve)
    print(f"On curve: {is_on_curve(q, curve)}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    curve = args.curve
    p1 = parse_point(args.p1, curve)
    p2 = parse_point(args.p2, curve)
    q = point_add(p1, p2, curve)
    print_point("P1 + P2", q, curve)
    print(f"On curve: {is_on_curve(q, curve)}")
    return 0


def cmd_mul(args: argparse.Namespace) -> int:
    curve = args.curve
    k = parse_int(args.k)
    point = parse_point(args.point, curve)
    q = scalar_mult(k, point, curve)
    print(f"k = {k}")
    print_point("kP", q, curve)
    print(f"On curve: {is_on_curve(q, curve)}")
    print(f"Is identity: {is_identity(q, curve)}")
    return 0


def cmd_xmul(args: argparse.Namespace) -> int:
    curve = args.curve
    k = parse_int(args.k)
    if args.u.lower() in {"g", "base", "generator"}:
        u = curve.gx
    else:
        u = parse_int(args.u)
    x = montgomery_x_ladder(k, u, curve)
    print(f"Curve: {curve.name}")
    print(f"k = {k}")
    print(f"input u/x = {fmt_int(u, curve)}")
    print(f"x(kP) by Montgomery ladder = {fmt_int(x, curve)}")

    if args.compare_affine and u == curve.gx:
        affine = scalar_mult(k, curve.G, curve)
        if affine is INF:
            print("affine kG = INF")
        else:
            print(f"x(kG) by affine double-and-add = {fmt_int(affine[0], curve)}")
            print(f"Ladder matches affine x-coordinate: {x == affine[0]}")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    curve = args.curve
    print("=" * 76)
    print(f"ECC arithmetic demo for {curve.name} ({curve.model})")
    print("=" * 76)
    print(f"Equation: {curve_equation(curve)}")
    print(f"Generator on curve: {is_on_curve(curve.G, curve)}")
    print()

    q2 = point_double(curve.G, curve)
    print_point("2G", q2, curve)
    print()

    q3 = scalar_mult(3, curve.G, curve)
    print_point("3G", q3, curve)
    print()

    d = parse_int(args.scalar)
    q = scalar_mult(d, curve.G, curve)
    print(f"Public key for d = {d}")
    print_point("Q", q, curve)
    print(f"Q on curve: {is_on_curve(q, curve)}")
    print()

    print(f"Verify n*G is identity: {is_identity(scalar_mult(curve.n, curve.G, curve), curve)}")
    if curve.model == MODEL_MONTGOMERY:
        x_ladder = montgomery_x_ladder(d, curve.gx, curve)
        if q is not INF:
            print(f"Montgomery ladder x(dG) matches affine x(dG): {x_ladder == q[0]}")
    return 0


# ============================================================
# CLI TASK HANDLERS: OPENSSL-BACKED
# ============================================================


def cmd_openssl_info(_: argparse.Namespace) -> int:
    d = require_cryptography()
    binding = d["Binding"]()
    openssl_version = d["Binding"].ffi.string(
        binding.lib.OpenSSL_version(0)
    ).decode("ascii", errors="replace")
    print(f"cryptography version: {d['version']}")
    print(f"OpenSSL version: {openssl_version}")
    print("Note: ECDSA/ECDH demo tasks in this script use the short-Weierstrass ec API.")
    return 0


def cmd_openssl_keygen(args: argparse.Namespace) -> int:
    require_short_weierstrass_openssl_curve(args.curve)
    d = require_cryptography()
    ec = d["ec"]
    serialization = d["serialization"]

    private_key = ec.generate_private_key(openssl_curve_object(args.curve))
    public_key = private_key.public_key()

    if args.password:
        encryption = serialization.BestAvailableEncryption(args.password.encode("utf-8"))
    else:
        encryption = serialization.NoEncryption()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    Path(args.private_key_out).write_bytes(private_pem)
    Path(args.public_key_out).write_bytes(public_pem)
    print(f"Private key written to: {args.private_key_out}")
    print(f"Public key written to: {args.public_key_out}")
    print(f"Curve: {args.curve.name} / OpenSSL {args.curve.openssl_name}")
    return 0


def cmd_openssl_sign(args: argparse.Namespace) -> int:
    require_short_weierstrass_openssl_curve(args.curve)
    d = require_cryptography()
    ec = d["ec"]

    private_key = load_private_key(args.private_key, args.password)
    data = read_message(args)
    signature = private_key.sign(data, ec.ECDSA(default_hash_algorithm(args.curve)))
    write_bytes_or_hex(signature, args.signature_out, "Signature DER")
    print(f"Message length: {len(data)} byte(s)")
    return 0


def cmd_openssl_verify(args: argparse.Namespace) -> int:
    require_short_weierstrass_openssl_curve(args.curve)
    d = require_cryptography()
    ec = d["ec"]
    InvalidSignature = d["InvalidSignature"]

    public_key = load_public_key(args.public_key)
    data = read_message(args)

    if args.signature_hex:
        signature = bytes.fromhex(args.signature_hex)
    else:
        signature = Path(args.signature).read_bytes()

    try:
        public_key.verify(signature, data, ec.ECDSA(default_hash_algorithm(args.curve)))
    except InvalidSignature:
        print("Signature valid: False")
        return 1

    print("Signature valid: True")
    print(f"Message length: {len(data)} byte(s)")
    return 0


def cmd_openssl_ecdh_demo(args: argparse.Namespace) -> int:
    require_short_weierstrass_openssl_curve(args.curve)
    d = require_cryptography()
    ec = d["ec"]
    hashes = d["hashes"]
    HKDF = d["HKDF"]

    openssl_curve = openssl_curve_object(args.curve)
    alice_private = ec.generate_private_key(openssl_curve)
    bob_private = ec.generate_private_key(openssl_curve)

    alice_shared = alice_private.exchange(ec.ECDH(), bob_private.public_key())
    bob_shared = bob_private.exchange(ec.ECDH(), alice_private.public_key())

    print(f"Curve: {args.curve.name} / OpenSSL {args.curve.openssl_name}")
    print(f"Raw ECDH shared secrets equal: {alice_shared == bob_shared}")
    print(f"Raw shared secret SHA-256: {hashlib.sha256(alice_shared).hexdigest()}")

    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=args.key_length,
        salt=args.salt.encode("utf-8") if args.salt else None,
        info=args.info.encode("utf-8"),
    ).derive(alice_shared)
    print(f"HKDF key ({args.key_length} byte): {derived_key.hex()}")
    return 0


# ============================================================
# ARGPARSE
# ============================================================


def add_message_options(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--message", help="UTF-8 message text")
    group.add_argument("--message-file", help="path to a message file")
    group.add_argument("--message-hex", help="hex-encoded message bytes")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Multi-model ECC arithmetic and OpenSSL-backed ECC task CLI.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--curve",
        type=parse_curve,
        default=P256,
        help="ECC curve name or alias",
    )

    sub = parser.add_subparsers(dest="task", required=True, title="tasks")

    p = sub.add_parser("list-curves", help="show supported curves")
    p.set_defaults(func=cmd_list_curves)

    p = sub.add_parser("info", help="show selected curve model, equation, and parameters")
    p.set_defaults(func=cmd_info)

    p = sub.add_parser("check-generator", help="check G and n*G for selected curve")
    p.set_defaults(func=cmd_check_generator)

    p = sub.add_parser("neg", help="compute -P")
    p.add_argument("--point", default="G", help="point: G, INF/ID, kG, k*G, or x,y")
    p.set_defaults(func=cmd_neg)

    p = sub.add_parser("double", help="compute 2P")
    p.add_argument("--point", default="G", help="point: G, INF/ID, kG, k*G, or x,y")
    p.set_defaults(func=cmd_double)

    p = sub.add_parser("add", help="compute P1 + P2")
    p.add_argument("--p1", required=True, help="first point: G, INF/ID, kG, k*G, or x,y")
    p.add_argument("--p2", required=True, help="second point: G, INF/ID, kG, k*G, or x,y")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("mul", help="compute kP by model-aware affine double-and-add")
    p.add_argument("--k", required=True, help="scalar in decimal or 0x hex")
    p.add_argument("--point", default="G", help="point: G, INF/ID, kG, k*G, or x,y")
    p.set_defaults(func=cmd_mul)

    p = sub.add_parser("xmul", help="Montgomery-only x-coordinate scalar multiplication by ladder")
    p.add_argument("--k", required=True, help="scalar in decimal or 0x hex")
    p.add_argument("--u", default="G", help="Montgomery u/x coordinate, or G for base u")
    p.add_argument("--compare-affine", action="store_true", help="compare with affine kG when u is the base coordinate")
    p.set_defaults(func=cmd_xmul)

    p = sub.add_parser("demo", help="run teaching demo for selected curve")
    p.add_argument("--scalar", default="123456789", help="demo private scalar")
    p.set_defaults(func=cmd_demo)

    p = sub.add_parser("openssl-info", help="show Python cryptography and OpenSSL versions")
    p.set_defaults(func=cmd_openssl_info)

    p = sub.add_parser("openssl-keygen", help="generate EC key pair using OpenSSL via cryptography; short-Weierstrass only")
    p.add_argument("--private-key-out", default="ec_private.pem", help="output private key PEM")
    p.add_argument("--public-key-out", default="ec_public.pem", help="output public key PEM")
    p.add_argument("--password", help="optional password for private key PEM")
    p.set_defaults(func=cmd_openssl_keygen)

    p = sub.add_parser("openssl-sign", help="sign a message using ECDSA; short-Weierstrass only")
    p.add_argument("--private-key", required=True, help="private key PEM")
    p.add_argument("--password", help="private key password, if encrypted")
    add_message_options(p)
    p.add_argument("--signature-out", help="write DER signature to this file; otherwise print hex")
    p.set_defaults(func=cmd_openssl_sign)

    p = sub.add_parser("openssl-verify", help="verify an ECDSA signature; short-Weierstrass only")
    p.add_argument("--public-key", required=True, help="public key PEM")
    add_message_options(p)
    sig_group = p.add_mutually_exclusive_group(required=True)
    sig_group.add_argument("--signature", help="DER signature file")
    sig_group.add_argument("--signature-hex", help="DER signature as hex text")
    p.set_defaults(func=cmd_openssl_verify)

    p = sub.add_parser("openssl-ecdh-demo", help="generate two EC keys and run ECDH + HKDF demo; short-Weierstrass only")
    p.add_argument("--key-length", type=int, default=32, help="HKDF output length in bytes")
    p.add_argument("--salt", default="", help="HKDF salt text; empty means no salt")
    p.add_argument("--info", default="ecc-ecdh-demo", help="HKDF info/context text")
    p.set_defaults(func=cmd_openssl_ecdh_demo)

    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return int(args.func(args) or 0)
    except (ValueError, RuntimeError, OSError, ZeroDivisionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
