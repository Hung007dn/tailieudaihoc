import hashlib
import hmac
import secrets

def choose_hash_function():
    print("Available hash algorithms from hashlib:")
    available = sorted(hashlib.algorithms_available)
    options = [h for h in available if callable(getattr(hashlib, h, None))]

    for i, hname in enumerate(options):
        print(f"{i+1:2}) {hname}")

    index = input(f"\nChoose hash function [1-{len(options)}] (default=1): ").strip()
    index = int(index) if index.isdigit() and 1 <= int(index) <= len(options) else 1
    algo_name = options[index - 1]

    print(f"✔️ Selected hash function: {algo_name}")
    return getattr(hashlib, algo_name), algo_name

def choose_key():
    choice = input("Use (1) Hex input key or (2) Random key? [default=2]: ").strip() or '2'
    if choice == '1':
        hex_str = input("Enter secret key in hex format: ").strip()
        try:
            key = bytes.fromhex(hex_str)
        except ValueError:
            print("❌ Invalid hex! Generating random key instead.")
            key = secrets.token_bytes(32)
    else:
        key = secrets.token_bytes(32)
        print("(Generated random 256-bit key)")
    print(f"✔️ Secret key (hex): {key.hex()}")
    return key

def compute_hmac(key, message, hash_func):
    return hmac.new(key, message.encode('utf-8'), hash_func).hexdigest()

def main():
    print("=== HMAC Generator & Verifier ===")

    # Step 1: Select hash function
    hash_func, hash_name = choose_hash_function()

    # Step 2: Select or input key in hex
    key = choose_key()

    # Step 3: Input message
    msg = input("Enter message to authenticate: ")

    # Step 4: Generate HMAC
    mac = compute_hmac(key, msg, hash_func)
    print(f"\n✅ HMAC-{hash_name.upper()} = {mac}")

    # Step 5: Verification
    recv_mac = input("\nEnter received MAC to verify: ").strip()
    recomputed = compute_hmac(key, msg, hash_func)
    print(f"🔁 Recomputed MAC: {recomputed}")

    if hmac.compare_digest(recv_mac, recomputed):
        print("✅ HMAC verified successfully!")
    else:
        print("❌ HMAC verification failed.")

if __name__ == "__main__":
    main()
