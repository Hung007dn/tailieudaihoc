import base64
import hashlib
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

# === Generate and Save PEM Keys ===
def generate_and_save_keys():
    print("\n🔐 Generating 2048-bit RSA key pair...")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
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

# === Sign Message with PSS ===
def sign_pss(private_key, message: bytes):
    print("\n✍️ Step-by-step RSA-PSS Signing")

    digest = hashlib.sha256(message).digest()
    print(f"\nStep 1: Hash the message m with SHA-256")
    print(f"        H(m) = {digest.hex()}")

    print("\nStep 2: Generate EM = PSS-Encode(H(m), salt, MGF1)")
    print("        (Internally done with random salt)")
    print("        EM is the padded encoded message block.")

    print("\nStep 3: Compute signature:")
    print("        Signature = EM^d mod n (RSA private key operation)")

    signature = private_key.sign(
        message,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )

    b64_sig = base64.b64encode(signature).decode()
    print("\n✅ Signature (Base64):")
    print(b64_sig)

    with open("signature.b64", "w") as f:
        f.write(b64_sig)
    print("✔️ Saved to signature.b64")
    return signature

# === Verify Signature with PSS ===
def verify_pss(public_key, message: bytes, signature: bytes):
    print("\n🔍 Step-by-step RSA-PSS Verification")

    digest = hashlib.sha256(message).digest()
    print(f"\nStep 1: Hash the message m with SHA-256")
    print(f"        H(m) = {digest.hex()}")

    print("\nStep 2: Compute m′ = sig^e mod n (RSA public key operation)")
    print("        (RSA decrypts signature to get EM′)")

    print("\nStep 3: Verify PSS padding in EM′")
    print("        Check salt, trailer byte, MGF1 expansion, and hash")

    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        print("✅ Signature is VALID.")
    except Exception as e:
        print("❌ Signature is INVALID.")
        print("Error:", e)

# === Main Program ===
def main():
    print("=== RSA-PSS Sign & Verify ===")
    mode = input("Choose mode: (1) Sign, (2) Verify [default=1]: ").strip() or "1"

    if mode == "1":
        use_existing = input("Use existing key? (y/n) [default=n]: ").strip().lower() or "n"
        if use_existing == "y":
            priv_path = input("Enter private key path [default=private_key.pem]: ").strip() or "private_key.pem"
            private_key = load_private_key(priv_path)
        else:
            private_key, _ = generate_and_save_keys()

        message = input("Enter message to sign: ").encode()
        sign_pss(private_key, message)

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

        verify_pss(public_key, msg, signature)

    else:
        print("Invalid mode.")

if __name__ == "__main__":
    main()
