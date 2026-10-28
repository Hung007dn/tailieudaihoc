#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diffie-Hellman Lab with full RFC 7919 FFDHE group support.

Revision goals:
- Add all RFC 7919 FFDHE groups: FFDHE2048, FFDHE3072, FFDHE4096,
  FFDHE6144, and FFDHE8192.
- Fix the old group menu bug where the menu indexed groups that were not
  actually defined.
- Keep the original classroom workflow: load group, generate safe prime,
  manual p/g entry, generate key pair, compute shared secret, Client/Server demo.
- Add safer FFDHE public-key validation: 2 <= Y <= p-2 and, for safe-prime
  groups, Y^q mod p == 1 where q=(p-1)/2.

Notes:
- RFC 7919 FFDHE groups use safe-prime moduli and generator g=2.
- The large RFC primes are treated as trusted constants; expensive primality
  checks are skipped unless explicitly requested for small/manual values.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from sympy import factorint, isprime, nextprime


def _hex_to_int(hex_text: str) -> int:
    """Parse multi-line hexadecimal integer text."""
    return int("".join(hex_text.split()), 16)


# -----------------------------------------------------------------------------
# RFC 7919 Appendix A: FFDHE safe-prime groups.
# Generator g is 2 for all groups.
# -----------------------------------------------------------------------------
DH_GROUPS: Dict[str, Dict[str, int | str]] = {
    "FFDHE2048": {
        "source": "RFC7919",
        "bits": 2048,
        "registry_value": 256,
        "g": 2,
        "p": _hex_to_int("""
FFFFFFFFFFFFFFFFADF85458A2BB4A9AAFDC5620273D3CF1D8B9C583CE2D3695
A9E13641146433FBCC939DCE249B3EF97D2FE363630C75D8F681B202AEC4617A
D3DF1ED5D5FD65612433F51F5F066ED0856365553DED1AF3B557135E7F57C935
984F0C70E0E68B77E2A689DAF3EFE8721DF158A136ADE73530ACCA4F483A797A
BC0AB182B324FB61D108A94BB2C8E3FBB96ADAB760D7F4681D4F42A3DE394DF4
AE56EDE76372BB190B07A7C8EE0A6D709E02FCE1CDF7E2ECC03404CD28342F61
9172FE9CE98583FF8E4F1232EEF28183C3FE3B1B4C6FAD733BB5FCBC2EC22005
C58EF1837D1683B2C6F34A26C1B2EFFA886B423861285C97FFFFFFFFFFFFFFFF
        """),
    },
    "FFDHE3072": {
        "source": "RFC7919",
        "bits": 3072,
        "registry_value": 257,
        "g": 2,
        "p": _hex_to_int("""
FFFFFFFFFFFFFFFFADF85458A2BB4A9AAFDC5620273D3CF1D8B9C583CE2D3695
A9E13641146433FBCC939DCE249B3EF97D2FE363630C75D8F681B202AEC4617A
D3DF1ED5D5FD65612433F51F5F066ED0856365553DED1AF3B557135E7F57C935
984F0C70E0E68B77E2A689DAF3EFE8721DF158A136ADE73530ACCA4F483A797A
BC0AB182B324FB61D108A94BB2C8E3FBB96ADAB760D7F4681D4F42A3DE394DF4
AE56EDE76372BB190B07A7C8EE0A6D709E02FCE1CDF7E2ECC03404CD28342F61
9172FE9CE98583FF8E4F1232EEF28183C3FE3B1B4C6FAD733BB5FCBC2EC22005
C58EF1837D1683B2C6F34A26C1B2EFFA886B4238611FCFDCDE355B3B6519035B
BC34F4DEF99C023861B46FC9D6E6C9077AD91D2691F7F7EE598CB0FAC186D91C
AEFE130985139270B4130C93BC437944F4FD4452E2D74DD364F2E21E71F54BFF
5CAE82AB9C9DF69EE86D2BC522363A0DABC521979B0DEADA1DBF9A42D5C4484E
0ABCD06BFA53DDEF3C1B20EE3FD59D7C25E41D2B66C62E37FFFFFFFFFFFFFFFF
        """),
    },
    "FFDHE4096": {
        "source": "RFC7919",
        "bits": 4096,
        "registry_value": 258,
        "g": 2,
        "p": _hex_to_int("""
FFFFFFFFFFFFFFFFADF85458A2BB4A9AAFDC5620273D3CF1D8B9C583CE2D3695
A9E13641146433FBCC939DCE249B3EF97D2FE363630C75D8F681B202AEC4617A
D3DF1ED5D5FD65612433F51F5F066ED0856365553DED1AF3B557135E7F57C935
984F0C70E0E68B77E2A689DAF3EFE8721DF158A136ADE73530ACCA4F483A797A
BC0AB182B324FB61D108A94BB2C8E3FBB96ADAB760D7F4681D4F42A3DE394DF4
AE56EDE76372BB190B07A7C8EE0A6D709E02FCE1CDF7E2ECC03404CD28342F61
9172FE9CE98583FF8E4F1232EEF28183C3FE3B1B4C6FAD733BB5FCBC2EC22005
C58EF1837D1683B2C6F34A26C1B2EFFA886B4238611FCFDCDE355B3B6519035B
BC34F4DEF99C023861B46FC9D6E6C9077AD91D2691F7F7EE598CB0FAC186D91C
AEFE130985139270B4130C93BC437944F4FD4452E2D74DD364F2E21E71F54BFF
5CAE82AB9C9DF69EE86D2BC522363A0DABC521979B0DEADA1DBF9A42D5C4484E
0ABCD06BFA53DDEF3C1B20EE3FD59D7C25E41D2B669E1EF16E6F52C3164DF4FB
7930E9E4E58857B6AC7D5F42D69F6D187763CF1D5503400487F55BA57E31CC7A
7135C886EFB4318AED6A1E012D9E6832A907600A918130C46DC778F971AD0038
092999A333CB8B7A1A1DB93D7140003C2A4ECEA9F98D0ACC0A8291CDCEC97DCF
8EC9B55A7F88A46B4DB5A851F44182E1C68A007E5E655F6AFFFFFFFFFFFFFFFF
        """),
    },
    "FFDHE6144": {
        "source": "RFC7919",
        "bits": 6144,
        "registry_value": 259,
        "g": 2,
        "p": _hex_to_int("""
FFFFFFFFFFFFFFFFADF85458A2BB4A9AAFDC5620273D3CF1D8B9C583CE2D3695
A9E13641146433FBCC939DCE249B3EF97D2FE363630C75D8F681B202AEC4617A
D3DF1ED5D5FD65612433F51F5F066ED0856365553DED1AF3B557135E7F57C935
984F0C70E0E68B77E2A689DAF3EFE8721DF158A136ADE73530ACCA4F483A797A
BC0AB182B324FB61D108A94BB2C8E3FBB96ADAB760D7F4681D4F42A3DE394DF4
AE56EDE76372BB190B07A7C8EE0A6D709E02FCE1CDF7E2ECC03404CD28342F61
9172FE9CE98583FF8E4F1232EEF28183C3FE3B1B4C6FAD733BB5FCBC2EC22005
C58EF1837D1683B2C6F34A26C1B2EFFA886B4238611FCFDCDE355B3B6519035B
BC34F4DEF99C023861B46FC9D6E6C9077AD91D2691F7F7EE598CB0FAC186D91C
AEFE130985139270B4130C93BC437944F4FD4452E2D74DD364F2E21E71F54BFF
5CAE82AB9C9DF69EE86D2BC522363A0DABC521979B0DEADA1DBF9A42D5C4484E
0ABCD06BFA53DDEF3C1B20EE3FD59D7C25E41D2B669E1EF16E6F52C3164DF4FB
7930E9E4E58857B6AC7D5F42D69F6D187763CF1D5503400487F55BA57E31CC7A
7135C886EFB4318AED6A1E012D9E6832A907600A918130C46DC778F971AD0038
092999A333CB8B7A1A1DB93D7140003C2A4ECEA9F98D0ACC0A8291CDCEC97DCF
8EC9B55A7F88A46B4DB5A851F44182E1C68A007E5E0DD9020BFD64B645036C7A
4E677D2C38532A3A23BA4442CAF53EA63BB454329B7624C8917BDD64B1C0FD4C
B38E8C334C701C3ACDAD0657FCCFEC719B1F5C3E4E46041F388147FB4CFDB477
A52471F7A9A96910B855322EDB6340D8A00EF092350511E30ABEC1FFF9E3A26E
7FB29F8C183023C3587E38DA0077D9B4763E4E4B94B2BBC194C6651E77CAF992
EEAAC0232A281BF6B3A739C1226116820AE8DB5847A67CBEF9C9091B462D538C
D72B03746AE77F5E62292C311562A846505DC82DB854338AE49F5235C95B9117
8CCF2DD5CACEF403EC9D1810C6272B045B3B71F9DC6B80D63FDD4A8E9ADB1E69
62A69526D43161C1A41D570D7938DAD4A40E329CD0E40E65FFFFFFFFFFFFFFFF
        """),
    },
    "FFDHE8192": {
        "source": "RFC7919",
        "bits": 8192,
        "registry_value": 260,
        "g": 2,
        "p": _hex_to_int("""
FFFFFFFFFFFFFFFFADF85458A2BB4A9AAFDC5620273D3CF1D8B9C583CE2D3695
A9E13641146433FBCC939DCE249B3EF97D2FE363630C75D8F681B202AEC4617A
D3DF1ED5D5FD65612433F51F5F066ED0856365553DED1AF3B557135E7F57C935
984F0C70E0E68B77E2A689DAF3EFE8721DF158A136ADE73530ACCA4F483A797A
BC0AB182B324FB61D108A94BB2C8E3FBB96ADAB760D7F4681D4F42A3DE394DF4
AE56EDE76372BB190B07A7C8EE0A6D709E02FCE1CDF7E2ECC03404CD28342F61
9172FE9CE98583FF8E4F1232EEF28183C3FE3B1B4C6FAD733BB5FCBC2EC22005
C58EF1837D1683B2C6F34A26C1B2EFFA886B4238611FCFDCDE355B3B6519035B
BC34F4DEF99C023861B46FC9D6E6C9077AD91D2691F7F7EE598CB0FAC186D91C
AEFE130985139270B4130C93BC437944F4FD4452E2D74DD364F2E21E71F54BFF
5CAE82AB9C9DF69EE86D2BC522363A0DABC521979B0DEADA1DBF9A42D5C4484E
0ABCD06BFA53DDEF3C1B20EE3FD59D7C25E41D2B669E1EF16E6F52C3164DF4FB
7930E9E4E58857B6AC7D5F42D69F6D187763CF1D5503400487F55BA57E31CC7A
7135C886EFB4318AED6A1E012D9E6832A907600A918130C46DC778F971AD0038
092999A333CB8B7A1A1DB93D7140003C2A4ECEA9F98D0ACC0A8291CDCEC97DCF
8EC9B55A7F88A46B4DB5A851F44182E1C68A007E5E0DD9020BFD64B645036C7A
4E677D2C38532A3A23BA4442CAF53EA63BB454329B7624C8917BDD64B1C0FD4C
B38E8C334C701C3ACDAD0657FCCFEC719B1F5C3E4E46041F388147FB4CFDB477
A52471F7A9A96910B855322EDB6340D8A00EF092350511E30ABEC1FFF9E3A26E
7FB29F8C183023C3587E38DA0077D9B4763E4E4B94B2BBC194C6651E77CAF992
EEAAC0232A281BF6B3A739C1226116820AE8DB5847A67CBEF9C9091B462D538C
D72B03746AE77F5E62292C311562A846505DC82DB854338AE49F5235C95B9117
8CCF2DD5CACEF403EC9D1810C6272B045B3B71F9DC6B80D63FDD4A8E9ADB1E69
62A69526D43161C1A41D570D7938DAD4A40E329CCFF46AAA36AD004CF600C838
1E425A31D951AE64FDB23FCEC9509D43687FEB69EDD1CC5E0B8CC3BDF64B10EF
86B63142A3AB8829555B2F747C932665CB2C0F1CC01BD70229388839D2AF05E4
54504AC78B7582822846C0BA35C35F5C59160CC046FD8251541FC68C9C86B022
BB7099876A460E7451A8A93109703FEE1C217E6C3826E52C51AA691E0E423CFC
99E9E31650C1217B624816CDAD9A95F9D5B8019488D9C0A0A1FE3075A577E231
83F81D4A3F2FA4571EFC8CE0BA8A4FE8B6855DFE72B0A66EDED2FBABFBE58A30
FAFABE1C5D71A87E2F741EF8C1FE86FEA6BBFDE530677F0D97D11D49F7A8443D
0822E506A9F4614E011E2A94838FF88CD68C8BB7C5C6424CFFFFFFFFFFFFFFFF
        """),
    },
}


@dataclass
class DHState:
    group_name: Optional[str] = None
    p: Optional[int] = None
    g: Optional[int] = None
    q: Optional[int] = None
    private_key: Optional[int] = None
    public_key: Optional[int] = None

    def clear_keys(self) -> None:
        self.private_key = None
        self.public_key = None


def short_hex(n: int, *, head: int = 32, tail: int = 32) -> str:
    hx = f"{n:x}"
    if len(hx) <= head + tail + 3:
        return "0x" + hx
    return "0x" + hx[:head] + "..." + hx[-tail:]


def print_big_int(label: str, value: Optional[int], *, full: bool = False) -> None:
    if value is None:
        print(f"{label}: None")
        return
    if full:
        print(f"{label} = {value}")
        print(f"{label} hex = 0x{value:x}")
    else:
        print(f"{label} bits = {value.bit_length()}")
        print(f"{label} hex  = {short_hex(value)}")


# -----------------------------------------------------------------------------
# Prime/group generation helpers
# -----------------------------------------------------------------------------
def generate_prime(bits: int = 2048) -> int:
    if bits < 32:
        raise ValueError("bits must be at least 32 for this lab function.")
    n = secrets.randbits(bits)
    n |= 1 << (bits - 1)  # force requested bit length
    n |= 1                 # odd
    return int(nextprime(n))


def generate_safe_prime(bits: int = 2048) -> int:
    """Generate a safe prime p=2q+1. This can be slow for large bit sizes."""
    if bits < 64:
        raise ValueError("safe-prime generation needs at least 64 bits in this lab.")
    attempts = 0
    while True:
        attempts += 1
        q = generate_prime(bits - 1)
        p = 2 * q + 1
        if p.bit_length() == bits and isprime(p):
            print(f"Safe prime found after {attempts} q-candidate(s).")
            return int(p)


def find_generator_safe_prime(p: int) -> Optional[int]:
    """Find a generator for the full multiplicative group modulo safe prime p."""
    q = (p - 1) // 2
    for g in range(2, min(p, 100000)):
        # For p=2q+1, g is a full generator iff g^2 != 1 and g^q != 1 mod p.
        if pow(g, 2, p) == 1:
            continue
        if pow(g, q, p) == 1:
            continue
        return g
    return None


def is_generator_small_group(g: int, p: int) -> bool | str:
    """Full generator test for small p only; factoring p-1 is expensive."""
    if p.bit_length() > 64:
        return "Skipped: p is large; factoring p-1 is not suitable for a quick lab check."
    factors = factorint(p - 1)
    for q_factor in factors:
        if pow(g, (p - 1) // q_factor, p) == 1:
            return False
    return True


def compute_q_if_safe_prime(p: int, *, trust_large: bool = False) -> Optional[int]:
    q = (p - 1) // 2
    if trust_large and p.bit_length() >= 2048:
        return q
    if isprime(p) and isprime(q):
        return q
    return None


# -----------------------------------------------------------------------------
# Parameter validation and public-key validation
# -----------------------------------------------------------------------------
def validate_parameters(p: int, g: int, *, group_name: Optional[str] = None) -> Tuple[bool, str]:
    if p <= 3:
        return False, "p must be greater than 3."
    if not (2 <= g <= p - 2):
        return False, "g must satisfy 2 <= g <= p-2."

    if group_name in DH_GROUPS:
        expected = DH_GROUPS[group_name]
        if p != expected["p"] or g != expected["g"]:
            return False, f"Parameters do not match the selected {group_name} constants."
        return True, "Known RFC 7919 FFDHE group constants accepted."

    # For manual/generated small groups, verify primality. For very large manual
    # values, this can be slow but is still safer than silently accepting them.
    if not isprime(p):
        return False, "p is not prime."
    return True, "p is prime and g is in the valid range."


def validate_public_key(y: int, p: int, q: Optional[int] = None) -> Tuple[bool, str]:
    """Validate received DH public key.

    Basic DH check: 2 <= y <= p-2.
    For safe-prime FFDHE subgroups with generator 2, also require y^q mod p == 1.
    """
    if not (2 <= y <= p - 2):
        return False, "Invalid peer public key: must satisfy 2 <= Y <= p-2."
    if q is not None:
        if pow(y, q, p) != 1:
            return False, "Invalid peer public key: not in the expected safe-prime subgroup."
    return True, "Peer public key accepted."


# -----------------------------------------------------------------------------
# Standard group loading
# -----------------------------------------------------------------------------
def list_standard_groups() -> None:
    print("\nAvailable RFC 7919 FFDHE Groups")
    print("=" * 78)
    print(f"{'#':>2}  {'Name':<10}  {'Bits':>5}  {'Registry':>8}  {'g':>2}")
    print("-" * 78)
    for idx, name in enumerate(DH_GROUPS.keys(), start=1):
        group = DH_GROUPS[name]
        print(f"{idx:2d}  {name:<10}  {group['bits']:5d}  {group['registry_value']:8d}  {group['g']:2d}")
    print(" 0  Cancel")


def load_standard_group() -> Optional[Tuple[str, int, int, int]]:
    names = list(DH_GROUPS.keys())
    list_standard_groups()
    while True:
        raw = input("\nSelect group: ").strip()
        try:
            choice = int(raw)
        except ValueError:
            print("Invalid selection. Enter a number.")
            continue

        if choice == 0:
            return None
        if 1 <= choice <= len(names):
            name = names[choice - 1]
            group = DH_GROUPS[name]
            p = int(group["p"])
            g = int(group["g"])
            q = (p - 1) // 2
            return name, p, g, q
        print("Invalid selection.")


# -----------------------------------------------------------------------------
# Key generation and exchange
# -----------------------------------------------------------------------------
def generate_key_pair(p: int, g: int, q: Optional[int] = None) -> Tuple[int, int]:
    """Generate DH key pair.

    For RFC 7919 safe-prime subgroups, q=(p-1)//2 and g=2 has order q. In that
    case, choose private exponent x in [2, q-2]. For generic groups, use [2,p-2].
    """
    mode = input("Random private key? (Y/n): ").strip().lower()
    upper = q if q is not None else (p - 1)

    if mode in ("", "y", "yes"):
        priv = secrets.randbelow(upper - 3) + 2
    else:
        priv = int(input("Private key x: ").strip(), 0)
        if not (2 <= priv <= upper - 2):
            raise ValueError(f"Private key must satisfy 2 <= x <= {upper - 2}.")

    pub = pow(g, priv, p)
    return priv, pub


def compute_shared_secret(p: int, private_key: int, other_public: int, q: Optional[int] = None) -> int:
    ok, msg = validate_public_key(other_public, p, q)
    if not ok:
        raise ValueError(msg)
    return pow(other_public, private_key, p)


def demo_exchange(p: int, g: int, q: Optional[int] = None) -> None:
    a = secrets.randbelow((q if q is not None else p - 1) - 3) + 2
    b = secrets.randbelow((q if q is not None else p - 1) - 3) + 2
    A = pow(g, a, p)
    B = pow(g, b, p)

    ok_a, msg_a = validate_public_key(A, p, q)
    ok_b, msg_b = validate_public_key(B, p, q)
    if not (ok_a and ok_b):
        print("Public-key validation failed:", msg_a, msg_b)
        return

    SA = pow(B, a, p)
    SB = pow(A, b, p)

    print("\nClient/Server DH exchange")
    print("-" * 78)
    print_big_int("Client A", A)
    print_big_int("Server B", B)
    print_big_int("Shared secret", SA)
    print("Match =", SA == SB)


# -----------------------------------------------------------------------------
# Menu actions
# -----------------------------------------------------------------------------
def require_params(state: DHState) -> Tuple[int, int]:
    if state.p is None or state.g is None:
        raise ValueError("No DH parameters loaded. Choose option 1, 2, or 3 first.")
    return state.p, state.g


def show_parameters(state: DHState, *, full: bool = False) -> None:
    print("\nCurrent DH Parameters")
    print("=" * 78)
    print("Group:", state.group_name)
    print_big_int("p", state.p, full=full)
    print_big_int("q", state.q, full=full)
    print_big_int("g", state.g, full=True)
    if state.p is not None and state.g is not None:
        ok, msg = validate_parameters(state.p, state.g, group_name=state.group_name)
        print("Validation:", "OK" if ok else "FAILED", "-", msg)
        print("Generator check:", is_generator_small_group(state.g, state.p))


def show_key_pair(state: DHState, *, full: bool = False) -> None:
    print("\nCurrent DH Key Pair")
    print("=" * 78)
    print_big_int("Private x", state.private_key, full=full)
    print_big_int("Public Y", state.public_key, full=full)


def enter_manual_parameters() -> Tuple[str, int, int, Optional[int]]:
    p = int(input("p = ").strip(), 0)
    g = int(input("g = ").strip(), 0)
    ok, msg = validate_parameters(p, g)
    print("Validation:", "OK" if ok else "FAILED", "-", msg)
    if not ok:
        retry = input("Keep these parameters anyway for teaching? (y/N): ").strip().lower()
        if retry not in ("y", "yes"):
            raise ValueError("Manual parameters rejected.")
    q = compute_q_if_safe_prime(p, trust_large=False)
    if q is not None:
        print("Safe-prime form detected: p = 2q + 1.")
    return "Manual", p, g, q


def main() -> None:
    state = DHState()

    while True:
        print("\n=== DIFFIE-HELLMAN LAB ===")
        print("1. Load RFC 7919 FFDHE Group")
        print("2. Generate Safe Prime + Generator")
        print("3. Enter p,g Manually")
        print("4. Show Parameters")
        print("5. Generate Key Pair")
        print("6. Show Key Pair")
        print("7. Compute Shared Secret")
        print("8. Client/Server Demo")
        print("9. List FFDHE Groups")
        print("0. Exit")

        choice = input("Choice: ").strip()

        try:
            if choice == "1":
                loaded = load_standard_group()
                if loaded is None:
                    continue
                state.group_name, state.p, state.g, state.q = loaded
                state.clear_keys()
                print(f"Loaded {state.group_name}: {state.p.bit_length()} bits, g={state.g}")

            elif choice == "2":
                bits = int(input("Bits [2048]: ").strip() or "2048")
                p = generate_safe_prime(bits)
                g = find_generator_safe_prime(p)
                if g is None:
                    raise RuntimeError("Could not find generator quickly.")
                q = (p - 1) // 2
                state.group_name, state.p, state.g, state.q = "Generated safe prime", p, g, q
                state.clear_keys()
                print("Generated safe prime group.")
                show_parameters(state)

            elif choice == "3":
                state.group_name, state.p, state.g, state.q = enter_manual_parameters()
                state.clear_keys()

            elif choice == "4":
                full = input("Print full p/q? (y/N): ").strip().lower() in ("y", "yes")
                show_parameters(state, full=full)

            elif choice == "5":
                p, g = require_params(state)
                state.private_key, state.public_key = generate_key_pair(p, g, state.q)
                print("Generated key pair.")
                print_big_int("Public Y", state.public_key)

            elif choice == "6":
                full = input("Print full private/public values? (y/N): ").strip().lower() in ("y", "yes")
                show_key_pair(state, full=full)

            elif choice == "7":
                p, _g = require_params(state)
                if state.private_key is None:
                    raise ValueError("Generate or enter your private key first.")
                other = int(input("Other public key Y: ").strip(), 0)
                secret = compute_shared_secret(p, state.private_key, other, state.q)
                print_big_int("Shared Secret", secret, full=True)

            elif choice == "8":
                p, g = require_params(state)
                demo_exchange(p, g, state.q)

            elif choice == "9":
                list_standard_groups()

            elif choice == "0":
                break

            else:
                print("Invalid choice.")

        except Exception as exc:
            print("Error:", exc)


if __name__ == "__main__":
    main()
