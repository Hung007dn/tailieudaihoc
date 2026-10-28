# NIST DSA (Digital Signature Algorithm) Educational Demo
import base64
import hashlib
import random
from Crypto.Util import number

# === Generate DSA Parameters and Keys ===
def generate_keys(L=1024, N=160):
    print("\n🔐 Generating NIST DSA Key Pair...")
    q = number.getPrime(N)
    while True:
        p = number.getPrime(L)
        if (p - 1) % q == 0:
            break
    h = 2
    g = pow(h, (p - 1) // q, p)
    x = random.randrange(1, q)  # private key
    y = pow(g, x, p)            # public key

    print("✔️ Parameters and Keys:")
    print(f"   p = {p}\n   q = {q}\n   g = {g}\n   x (private) = {x}\n   y (public) = {y}")

    with open("dsa_private.txt", "w") as f:
        f.write(f"{p}\n{q}\n{g}\n{x}")
    with open("dsa_public.txt", "w") as f:
        f.write(f"{p}\n{q}\n{g}\n{y}")

    return (p, q, g, x), (p, q, g, y)

# === Load Keys ===
def load_private_key():
    with open("dsa_private.txt") as f:
        p, q, g, x = map(int, f.read().splitlines())
    return p, q, g, x

def load_public_key():
    with open("dsa_public.txt") as f:
        p, q, g, y = map(int, f.read().splitlines())
    return p, q, g, y

# === Sign Message ===
def sign_message(p, q, g, x, message: bytes):
    print("\n✍️ DSA Signing...")
    h = int(hashlib.sha1(message).hexdigest(), 16) % q
    print(f"Step 1: H(m) = SHA-1(m) mod q = {h}")

    while True:
        k = random.randrange(1, q)
        r = pow(g, k, p) % q
        if r == 0:
            continue
        k_inv = number.inverse(k, q)
        s = (k_inv * (h + x * r)) % q
        if s == 0:
            continue
        break

    print(f"Step 2: k = {k}, r = (g^k mod p) mod q = {r}")
    print(f"Step 3: s = k^-1 * (H(m) + x*r) mod q = {s}")

    with open("signature.txt", "w") as f:
        f.write(f"{r}\n{s}")
    print("✔️ Signature saved to signature.txt")
    return r, s

# === Verify Signature ===
def verify_signature(p, q, g, y, message: bytes, r: int, s: int):
    print("\n🔍 DSA Verification...")
    if not (0 < r < q and 0 < s < q):
        print("❌ Invalid signature range")
        return

    h = int(hashlib.sha1(message).hexdigest(), 16) % q
    print(f"Step 1: H(m) = SHA-1(m) mod q = {h}")

    w = number.inverse(s, q)
    u1 = (h * w) % q
    u2 = (r * w) % q
    v = ((pow(g, u1, p) * pow(y, u2, p)) % p) % q

    print(f"Step 2: Compute w = s^-1 mod q = {w}")
    print(f"Step 3: u1 = H(m)*w mod q = {u1}, u2 = r*w mod q = {u2}")
    print(f"Step 4: v = ((g^u1 * y^u2) mod p) mod q = {v}")

    if v == r:
        print("✅ Signature is VALID.")
    else:
        print("❌ Signature is INVALID.")

# === Main Program ===
def main():
    print("=== NIST DSA (Digital Signature Algorithm) ===")
    mode = input("Choose mode: (1) Sign, (2) Verify [default=1]: ").strip() or "1"

    if mode == "1":
        use_existing = input("Use existing key? (y/n) [default=n]: ").strip().lower() or "n"
        if use_existing == "y":
            p, q, g, x = load_private_key()
        else:
            (p, q, g, x), _ = generate_keys()
        msg = input("Enter message to sign: ").encode()
        sign_message(p, q, g, x, msg)

    elif mode == "2":
        p, q, g, y = load_public_key()
        msg = input("Enter message to verify: ").encode()
        sig_file = input("Signature file [default=signature.txt]: ").strip() or "signature.txt"
        try:
            with open(sig_file) as f:
                r, s = map(int, f.read().splitlines())
        except:
            print("❌ Failed to load signature.")
            return
        verify_signature(p, q, g, y, msg, r, s)

    else:
        print("Invalid mode.")

if __name__ == "__main__":
    main()