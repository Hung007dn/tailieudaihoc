# Schnorr Digital Signature with Dynamic 2048-bit Parameters (Fast Prime Check)
import base64
import hashlib
import random
from Crypto.Util import number
from random import getrandbits

# === Generate Safe Prime and Generator ===
def generate_params(L=2048, N=256):
    print("[*] Generating safe prime (p = q·r + 1)...")
    while True:
        q = number.getPrime(N)
        for _ in range(1000):
            r = number.getPrime(L - N)
            p = q * r + 1
            if number.isPrime(p):
                for h in range(2, p - 1):
                    g = pow(h, r, p)
                    if g != 1:
                        print("✔️ Safe prime p and q found.")
                        return p, q, g

# === Generate Key Pair ===
def generate_keys():
    p, q, g = generate_params()
    x = random.randrange(1, q)
    y = pow(g, x, p)
    print(f"✔️ Private key x = {x}")
    print(f"✔️ Public key  y = {y}")
    with open("schnorr_private.txt", "w") as f:
        f.write(f"{p}\n{q}\n{g}\n{x}")
    with open("schnorr_public.txt", "w") as f:
        f.write(f"{p}\n{q}\n{g}\n{y}")
    return p, q, g, x, y

# === Load Keys ===
def load_private_key():
    with open("schnorr_private.txt") as f:
        p, q, g, x = map(int, f.read().splitlines())
    return p, q, g, x

def load_public_key():
    with open("schnorr_public.txt") as f:
        p, q, g, y = map(int, f.read().splitlines())
    return p, q, g, y

# === Sign Message ===
def sign_message(p, q, g, x, message: bytes):
    print("✔️ Schnorr Signing...")
    k = random.randrange(1, q)
    r = pow(g, k, p)
    e = int(hashlib.sha256(str(r).encode() + message).hexdigest(), 16) % q
    s = (k - x * e) % q
    print(f"Step 1: r = g^k mod p = {r}")
    print(f"Step 2: e = H(r || m) mod q = {e}")
    print(f"Step 3: s = k - x*e mod q = {s}")
    with open("signature.txt", "w") as f:
        f.write(f"{e}\n{s}")
    print("✔️ Signature saved to signature.txt")
    return e, s

# === Verify Signature ===
def verify_signature(p, q, g, y, message: bytes, e: int, s: int):
    print("✔️ Schnorr Verifying...")
    r_prime = (pow(g, s, p) * pow(y, e, p)) % p
    e_prime = int(hashlib.sha256(str(r_prime).encode() + message).hexdigest(), 16) % q
    print(f"Step 1: r' = g^s * y^e mod p = {r_prime}")
    print(f"Step 2: e' = H(r' || m) mod q = {e_prime}")
    if e == e_prime:
        print("✔️ Signature is VALID.")
    else:
        print("✔️ Signature is INVALID.")

# === Main ===
def main():
    print("=== Schnorr Digital Signature (Generated Safe Primes) ===")
    mode = input("Choose mode: (1) Sign, (2) Verify [default=1]: ").strip() or "1"

    if mode == "1":
        use_existing = input("Use existing key? (y/n) [default=n]: ").strip().lower() or "n"
        if use_existing == "y":
            p, q, g, x = load_private_key()
        else:
            p, q, g, x, _ = generate_keys()
        msg = input("Enter message to sign: ").encode()
        sign_message(p, q, g, x, msg)

    elif mode == "2":
        p, q, g, y = load_public_key()
        msg = input("Enter message to verify: ").encode()
        sig_file = input("Signature file [default=signature.txt]: ").strip() or "signature.txt"
        try:
            with open(sig_file) as f:
                e, s = map(int, f.read().splitlines())
        except:
            print("✔️ Failed to load signature.")
            return
        verify_signature(p, q, g, y, msg, e, s)

    else:
        print("Invalid mode.")

if __name__ == "__main__":
    main()