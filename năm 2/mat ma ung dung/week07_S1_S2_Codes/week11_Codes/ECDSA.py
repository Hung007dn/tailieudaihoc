import base64
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization

# === Select Curve from Available List ===
def select_curve():
    curves = {
        "1": ec.SECP256R1(),
        "2": ec.SECP384R1(),
        "3": ec.SECP521R1(),
        "4": ec.SECP256K1()
    }
    print("\nAvailable ECC Curves:")
    print("  1) SECP256R1 (P-256)")
    print("  2) SECP384R1 (P-384)")
    print("  3) SECP521R1 (P-521)")
    print("  4) SECP256K1 (Bitcoin Curve)")
    choice = input("Select curve [default=1]: ").strip() or "1"
    return curves.get(choice, ec.SECP256R1())

# === Generate and Save PEM Keys ===
def generate_and_save_keys():
    curve = select_curve()
    print(f"\n🔐 Generating ECDSA key pair ({curve.name})...")
    private_key = ec.generate_private_key(curve)
    public_key = private_key.public_key()

    with open("private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        ))

    with open("public_key.pem", "wb") as f:
        f.write(public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print("✔️ Keys saved to:")
    print("   - private_key.pem")
    print("   - public_key.pem")
    return private_key, public_key

# === Load PEM Keys ===
def load_private_key(filepath):
    with open(filepath, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def load_public_key(filepath):
    with open(filepath, "rb") as f:
        return serialization.load_pem_public_key(f.read())

# === Sign Message with ECDSA ===
def sign_ecdsa(private_key, message: bytes):
    print("\n✍️ Step-by-step ECDSA Signing")

    digest = hashlib.sha256(message).digest()
    print(f"\nStep 1: Hash the message m with SHA-256")
    print(f"        H(m) = {digest.hex()}")

    print("\nStep 2: Compute signature using ECDSA:")
    print("        Signature = (r, s) such that s = k^-1(H(m) + r*d) mod n")

    signature = private_key.sign(
        message,
        ec.ECDSA(hashes.SHA256())
    )

    b64_sig = base64.b64encode(signature).decode()
    print("\n✅ Signature (Base64):")
    print(b64_sig)

    with open("signature.b64", "w") as f:
        f.write(b64_sig)
    print("✔️ Saved to signature.b64")
    return signature

# === Verify ECDSA Signature ===
def verify_ecdsa(public_key, message: bytes, signature: bytes):
    print("\n🔍 Step-by-step ECDSA Verification")

    digest = hashlib.sha256(message).digest()
    print(f"\nStep 1: Hash the message m with SHA-256")
    print(f"        H(m) = {digest.hex()}")

    print("\nStep 2: Verify using public key and r, s components")
    print("        Check: s^-1 * H(m) and s^-1 * r * Q matches")

    try:
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        print("✅ Signature is VALID.")
    except Exception as e:
        print("❌ Signature is INVALID.")
        print("Error:", e)

# === Main Program ===
def main():
    print("=== ECDSA Sign & Verify ===")
    mode = input("Choose mode: (1) Sign, (2) Verify [default=1]: ").strip() or "1"

    if mode == "1":
        use_existing = input("Use existing key? (y/n) [default=n]: ").strip().lower() or "n"
        if use_existing == "y":
            priv_path = input("Enter private key path [default=private_key.pem]: ").strip() or "private_key.pem"
            private_key = load_private_key(priv_path)
        else:
            private_key, _ = generate_and_save_keys()

        message = input("Enter message to sign: ").encode()
        sign_ecdsa(private_key, message)

    elif mode == "2":
        msg = input("Enter message to verify: ").encode()

        sig_file = input("Signature file (Base64) [default=signature.b64]: ").strip() or "signature.b64"
        pub_file = input("Public key file [default=public_key.pem]: ").strip() or "public_key.pem"

        try:
            with open(sig_file, "r") as f:
                sig_b64 = f.read().strip()
            signature = base64.b64decode(sig_b64)
        except Exception as e:
            print("❌ Error loading signature:", e)
            return

        try:
            public_key = load_public_key(pub_file)
        except Exception as e:
            print("❌ Error loading public key:", e)
            return

        verify_ecdsa(public_key, msg, signature)

    else:
        print("Invalid mode.")

if __name__ == "__main__":
    main()