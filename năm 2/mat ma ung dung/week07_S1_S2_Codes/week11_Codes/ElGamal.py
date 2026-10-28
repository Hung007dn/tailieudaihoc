# ElGamal Digital Signature Scheme (Educational Demo)
import base64
import hashlib
import random
from Crypto.Util import number

# === Generate Keys ===
def generate_keys(bit_length=512):
    print("\n🔐 Generating ElGamal Key Pair...")
    p = number.getPrime(bit_length)
    g = random.randrange(2, p-1)
    x = random.randrange(2, p-2)  # Private key
    y = pow(g, x, p)             # Public key
    print("✔️ Key components:")
    print(f"   Prime p = {p}")
    print(f"   Generator g = {g}")
    print(f"   Private key x = {x}")
    print(f"   Public key y = {y}")
    with open("elgamal_private.txt", "w") as f:
        f.write(f"{p}\n{g}\n{x}")
    with open("elgamal_public.txt", "w") as f:
        f.write(f"{p}\n{g}\n{y}")
    return (p, g, x), (p, g, y)

# === Load Keys ===
def load_private_key(path="elgamal_private.txt"):
    with open(path) as f:
        p, g, x = map(int, f.read().splitlines())
    return p, g, x

def load_public_key(path="elgamal_public.txt"):
    with open(path) as f:
        p, g, y = map(int, f.read().splitlines())
    return p, g, y

# === Sign Message ===
def sign_message(p, g, x, message: bytes):
    print("\n✍️ ElGamal Signing...")
    h = int(hashlib.sha256(message).hexdigest(), 16) % p
    print(f"Step 1: H(m) = SHA-256(m) mod p = {h}")
    while True:
        k = random.randrange(2, p - 1)
        if number.GCD(k, p - 1) == 1:
            break
    r = pow(g, k, p)
    k_inv = number.inverse(k, p - 1)
    s = (k_inv * (h - x * r)) % (p - 1)
    print(f"Step 2: k = {k}, r = g^k mod p = {r}")
    print(f"Step 3: s = k^-1 * (H(m) - x*r) mod (p-1) = {s}")
    sig = f"{r}\n{s}"
    with open("signature.txt", "w") as f:
        f.write(sig)
    print("✔️ Signature saved to signature.txt")
    return r, s

# === Verify Signature ===
def verify_signature(p, g, y, message: bytes, r: int, s: int):
    print("\n🔍 ElGamal Verifying...")
    h = int(hashlib.sha256(message).hexdigest(), 16) % p
    print(f"Step 1: H(m) = SHA-256(m) mod p = {h}")
    if not (0 < r < p):
        print("❌ Invalid r")
        return
    v1 = (pow(y, r, p) * pow(r, s, p)) % p
    v2 = pow(g, h, p)
    print(f"Step 2: v1 = y^r * r^s mod p = {v1}")
    print(f"Step 3: v2 = g^H(m) mod p = {v2}")
    if v1 == v2:
        print("✅ Signature is VALID.")
    else:
        print("❌ Signature is INVALID.")

# === Main Program ===
def main():
    print("=== ElGamal Digital Signature ===")
    mode = input("Choose mode: (1) Sign, (2) Verify [default=1]: ").strip() or "1"

    if mode == "1":
        use_existing = input("Use existing key? (y/n) [default=n]: ").strip().lower() or "n"
        if use_existing == "y":
            p, g, x = load_private_key()
        else:
            (p, g, x), _ = generate_keys()
        msg = input("Enter message to sign: ").encode()
        sign_message(p, g, x, msg)

    elif mode == "2":
        p, g, y = load_public_key()
        msg = input("Enter message to verify: ").encode()
        sig_file = input("Signature file [default=signature.txt]: ").strip() or "signature.txt"
        try:
            with open(sig_file) as f:
                r, s = map(int, f.read().splitlines())
        except:
            print("❌ Failed to load signature.")
            return
        verify_signature(p, g, y, msg, r, s)

    else:
        print("Invalid mode.")

if __name__ == "__main__":
    main()
